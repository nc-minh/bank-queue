import os
from flask import jsonify, render_template, Flask, request, flash, redirect, url_for
from flask_restful import Resource, Api
import sqlite3

app = Flask(__name__, static_folder='static')
api = Api(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM products').fetchall()
    conn.close()

    products = [dict(row) for row in rows]
    return render_template('index.html',  products=products)

@app.route('/product/create', methods=('GET', 'POST'))
def create_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        # upload image
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        file.save(os.path.join("static/images", file.filename))

        # get image path
        image_path = os.path.join("static/images", file.filename)

        if not name:
            flash('Name is required!')
        elif not description:
            flash('Description is required!')
        elif not price:
            flash('Price is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO products (name, description, price, image_path) VALUES (?, ?, ?, ?)',
                 (name, description, price, image_path))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create_product.html')

# create all products
@app.route('/products', methods=['GET'])
def get_products():

    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM products').fetchall()
    conn.close()

    posts = [dict(row) for row in rows]
    
    return jsonify(posts)

# create a product
@app.route('/products', methods=['POST'])
def create_product_api():
    product = request.get_json()

    conn = get_db_connection()
    conn.execute('INSERT INTO products (name, description, price) VALUES (?, ?, ?)',
                 (product['name'], product['description'], product['price']))
    conn.commit()
    conn.close()

    return jsonify(product)



if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
