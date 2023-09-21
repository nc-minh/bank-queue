from flask import Flask, request, jsonify


class CustomQueue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        else:
            raise IndexError("Queue is empty")

    def size(self):
        return len(self.items)


app = Flask(__name__)

message_queue = CustomQueue()


@app.route('/enqueue', methods=['POST'])
def enqueue_message():
    data = request.json
    message = data.get('message')

    if message:
        message_queue.enqueue(message)
        print(f'Message enqueued: {message}')
        return jsonify({'status': 'success', 'message': 'Message enqueued'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400


@app.route('/dequeue', methods=['GET'])
def dequeue_message():
    try:
        message = message_queue.dequeue()
        print(f'Message dequeued: {message}')
        return jsonify({'status': 'success', 'message': message}), 200
    except IndexError:
        return jsonify({'status': 'error', 'message': 'Queue is empty'}), 404


if __name__ == '__main__':
    app.run(host='localhost', port=5001)
