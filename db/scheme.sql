DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;

CREATE TABLE Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    image_path TEXT,
    price FLOAT NOT NULL
);

CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_info TEXT NOT NULL,
    status TEXT
);