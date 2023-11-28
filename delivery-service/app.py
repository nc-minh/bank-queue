import atexit
import json
import os
import sqlite3
import threading
import time
from colorama import Fore
from flask import Flask, render_template
import requests

app = Flask(__name__, static_folder='static')
exit_event = threading.Event()
is_exiting = False
queue_server_url = 'http://localhost:5555'

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
            response = requests.get(f'{queue_server_url}/dequeue?key=restaurant-service', timeout=1200000)
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


                print(f'Processing payment for order {message_object["order_id"]}...')

                conn = get_db_connection()
                conn.execute('UPDATE orders SET status = ? WHERE order_id = ?', ('DELIVERING', message_object["order_id"]))
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
    rows = conn.execute('SELECT * FROM orders WHERE status = ?', ('DELIVERING',)).fetchall()
    conn.close()

    orders = [dict(row) for row in rows]

    for order in orders:
        print(order["order_id"])
        order['order_info'] = json.loads(order['order_info'])

    return render_template('index.html', orders=orders)



def cleanup():
    exit_event.set()
    is_exiting = True
    print('Exiting...')

atexit.register(cleanup)


consumer_thread = threading.Thread(target=consumer, daemon=True)
consumer_thread.start()

if __name__ == '__main__':
    app.run(host='localhost', port=5003)
