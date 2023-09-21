import http.client
import json

mq_server_host = 'localhost'
mq_server_port = 5001

while True:
    message = input("Nhập message (Nhấn Enter để gửi hoặc 'q' để thoát): ")

    if message == 'q':
        break

    if message:
        try:
            connection = http.client.HTTPConnection(
                mq_server_host, mq_server_port)

            headers = {'Content-type': 'application/json'}
            payload = json.dumps({'message': message})

            connection.request('POST', '/enqueue',
                               body=payload, headers=headers)

            response = connection.getresponse()

            if response.status == 200:
                print('Message sent to queue')
            else:
                print('Failed to send message to queue')
        except Exception as e:
            print(f'Error: {str(e)}')
    else:
        print('Invalid message')
