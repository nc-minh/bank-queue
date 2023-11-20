import time
from flask import Flask, request, jsonify

class CustomQueue:
    def __init__(self):
        self.queues = {}

    def is_empty(self, key):
        return len(self.queues.get(key, [])) == 0

    def enqueue(self, key, item):
        if key not in self.queues:
            self.queues[key] = []
        self.queues[key].append(item)

    def dequeue(self, key):
        if not self.is_empty(key):
            return self.queues[key].pop(0)
        # else:
        #     raise IndexError(f'Queue with key "{key}" is empty')

    def size(self, key):
        return len(self.queues.get(key, []))


app = Flask(__name__)



@app.route('/enqueue', methods=['POST'])
def enqueue_message():
    data = request.json
    key = data.get('key')
    message = data.get('message')

    if key and message:
        message_queues.enqueue(key, message)
        print(f'MESSAGE ENQUEUED FOR KEY {key}: {message}')
        return jsonify({'status': 'success', 'message': f'Message enqueued for key {key}'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@app.route('/dequeue', methods=['GET'])
def dequeue_message():
    key = request.args.get('key')
    try:
        while True:
            # Check for new data
            message = message_queues.dequeue(key)
            if message:
                print(f'MESSAGE DEQUEUED FOR KEY {key}: {message}')
                return jsonify({'status': 'success', 'message': message}), 200
    except IndexError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404

if __name__ == '__main__':
    message_queues = CustomQueue()
    app.run(host='localhost', port=5555, threaded=True)
