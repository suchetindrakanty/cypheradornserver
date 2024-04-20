import sqlite3
import json
import random

def placeOrder(DATABASE, items, username, address, price, status, phoneNo, oid):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    orderID = int(oid)
    
    c.execute(
        f'''CREATE TABLE IF NOT EXISTS {username}_order (
            orderID INTEGER,
            items TEXT NOT NULL,
            address TEXT NOT NULL,
            price INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Order Placed',
            phone_number TEXT NOT NULL
        )'''
    )

    c.execute(f'''
        CREATE TABLE IF NOT EXISTS orders (
            orderID INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            items TEXT NOT NULL,
            address TEXT NOT NULL,
            price INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Order Placed',
            phone_number TEXT NOT NULL
        )
    ''')

    conn.commit()

    try:
        c.execute('SELECT orderID FROM orders')
        orderids = [row[0] for row in c.fetchall()]

        items_json = items.replace('\\', '')
        items_tuple = (orderID, items_json, username, address, price, status, phoneNo)

        c.execute('INSERT INTO orders (orderID, items, username, address, price, status, phone_number) VALUES (?, ?, ?, ?, ?, ?, ?)', items_tuple)
        
        user_tuple = (orderID, items_json, address, price, status, phoneNo)
        c.execute(f'INSERT INTO {username}_order (orderID, items, address, price, status, phone_number) VALUES (?, ?, ?, ?, ?, ?)', user_tuple)
        
        conn.commit()
        
        return {
            'message': 'Success'
        }

    except Exception as e:
        conn.rollback()
        print(e)
        return {
            'message': 'Database error, try again later :('
        }
    
    finally:
        conn.close()
