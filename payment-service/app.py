import atexit
import http
import json
import os
import sqlite3
from colorama import Fore
from flask import Flask, render_template, request
import threading
import requests
import time

app = Flask(__name__, static_folder='static')

exit_event = threading.Event()
is_exiting = False

queue_server_url = 'http://localhost:5555'
mq_server_host = 'localhost'
mq_server_port = 5555

def get_db_connection():
    conn = None
    try:
        db_path = os.path.abspath(os.getcwd() + "/db/database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def dequeue_message():
    max_retries = 100
    retries = 0

    while retries < max_retries:
        try:
            if is_exiting:
                print("Exiting from dequeue_message")
                break
            response = requests.get(f'{queue_server_url}/dequeue?key=order-service', timeout=1200000)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            return response.json()
        except requests.exceptions.Timeout:
            print(f"Timeout error. Retry {retries + 1}/{max_retries}")
        except requests.exceptions.HTTPError:
            print(f"HTTPError. Retry {retries + 1}/{max_retries}")
        except requests.exceptions.RequestException:
            print(f"RequestException. Retry {retries + 1}/{max_retries}")
        except Exception:
            print(f"Exception. Retry {retries + 1}/{max_retries}")

        if exit_event.is_set():
            print("Exit event set. Exiting...")
            break

        retries += 1
        # Use exponential backoff with a maximum delay of 32 seconds
        delay = min(2 ** retries, 32)
        time.sleep(delay)

    print(Fore.RED + "Max retries reached. Unable to dequeue message.")
    return None  # Return None to indicate that no message was retrieved

def consumer():
    while True:
        try:
            if is_exiting:
                print("Exiting from consumer")
                break
            
            message = dequeue_message()
            if message:
                print(f'Received message: {message}')

                message_object = message.get('message')

                order_info = json.dumps(message_object)
                order_status = 'PENDING'

                conn = get_db_connection()
                conn.execute('INSERT INTO orders (order_info, status) VALUES (?, ?)',
                            (order_info, order_status))
                conn.commit()
                conn.close()

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Retrying...")

        
        if exit_event.is_set():
            print("Exit event set. Exiting...")
            break

@app.route('/')
def index():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM orders WHERE status = ?', ('PENDING',)).fetchall()
    conn.close()

    orders = [dict(row) for row in rows]

    for order in orders:
        print(order["order_id"])
        order['order_info'] = json.loads(order['order_info'])

    return render_template('index.html', orders=orders)

@app.route('/prepare', methods=['POST'])
def prepare():

    order = request.get_json()
    connection = http.client.HTTPConnection(
        mq_server_host, mq_server_port)

    headers = {'Content-type': 'application/json'}
    payload = json.dumps({'message': {
        'order_id': order['order_id'],
    }, 'key': "payment-service"})

    connection.request('POST', '/enqueue',
                        body=payload, headers=headers)

    response = connection.getresponse()

    if response.status == 200:
        print('Message sent to queue')
    else:
        print('Failed to send message to queue')

    return '', 204


def cleanup():
    exit_event.set()
    is_exiting = True
    print('Exiting...')

atexit.register(cleanup)



consumer_thread = threading.Thread(target=consumer, daemon=True)
consumer_thread.start()

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='localhost', port=5001)
