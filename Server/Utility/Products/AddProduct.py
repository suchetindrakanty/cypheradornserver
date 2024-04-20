import sqlite3
import os 

def create_product_table(DATABASE):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            productName TEXT,
            productPrice REAL,
            productDiscount INTEGER,
            productDescriptionUpper TEXT,
            productMaterial TEXT,
            productDescriptionLower TEXT,
            productPrintType TEXT,
            productImage TEXT
        )
    ''')

    conn.commit()
    conn.close()