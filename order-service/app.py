from flask import Flask, render_template, jsonify

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products', methods=['GET'])
def get_products():
    products = [
        {'id': 1, 'name': 'Product 1', 'price': 10.99},
        {'id': 2, 'name': 'Product 2', 'price': 19.99},
        {'id': 3, 'name': 'Product 3', 'price': 5.99},
    ]
    return jsonify(products)
    


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
