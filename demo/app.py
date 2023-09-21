import http.client
import time

mq_server_host = 'localhost'
mq_server_port = 5001

while True:
    try:
        connection = http.client.HTTPConnection(mq_server_host, mq_server_port)

        connection.request('GET', '/dequeue')

        response = connection.getresponse()

        if response.status == 200:
            data = response.read()
            print('Dequeued message:', data.decode('utf-8'))
        # else:
        #     print('Failed to dequeue message')
    except Exception as e:
        print(f'Error: {str(e)}')

    time.sleep(1)  # Sleep for 1 second
