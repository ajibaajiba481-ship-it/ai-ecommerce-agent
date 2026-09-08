import sqlite3

DB_NAME = "ecommerce.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price INTEGER,
            stock INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            product TEXT,
            status TEXT
        )
    """)

    products = [
        (1, "Samsung Galaxy A55", "Mobile", 29999, 15),
        (2, "iPhone 15", "Mobile", 54999, 8),
        (3, "HP Laptop 15", "Laptop", 45999, 10),
        (4, "Dell Inspiron", "Laptop", 52999, 5),
        (5, "Boat Headphones", "Accessories", 1999, 25),
        (6, "Sony Headphones", "Accessories", 7999, 12)
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO products
        VALUES (?, ?, ?, ?, ?)
    """, products)

    orders = [
        ("ORD1001", "Customer", "Samsung Galaxy A55", "Shipped"),
        ("ORD1002", "Customer", "HP Laptop 15", "Delivered"),
        ("ORD1003", "Customer", "Boat Headphones", "Processing")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO orders
        VALUES (?, ?, ?, ?)
    """, orders)

    conn.commit()
    conn.close()


def search_products(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, category, price, stock
        FROM products
        WHERE name LIKE ? OR category LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))

    result = cursor.fetchall()
    conn.close()

    return result


def get_order_status(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT order_id, product, status
        FROM orders
        WHERE order_id = ?
    """, (order_id,))

    result = cursor.fetchone()
    conn.close()

    return result


def request_return(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status FROM orders
        WHERE order_id = ?
    """, (order_id,))

    result = cursor.fetchone()

    if not result:
        conn.close()
        return "Order not found."

    cursor.execute("""
        UPDATE orders
        SET status = 'Return Requested'
        WHERE order_id = ?
    """, (order_id,))

    conn.commit()
    conn.close()

    return f"Return request successfully created for order {order_id}."