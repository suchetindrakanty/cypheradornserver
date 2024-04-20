from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os 
import time
import base64

image_path = r'DataBases/Assets/ProductImage'

def create_prodcut_size_table(DATABASE, id):
    print(f'ID is {id}')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS products_size (
            id INTEGER PRIMARY KEY,
            product_S_Count INT DEFAULT 0,
            product_M_count INT DEFAULT 0,
            product_L_count INT DEFAULT 0,
            product_XL_count INT DEFAULT 0,
            product_XXL_count INT DEFAULT 0,
            product_XXXL_count INT DEFAULT 0
        )
    ''')
    conn.commit()

    # Check if the id already exists
    c.execute("SELECT * FROM products_size WHERE id=?", (id,))
    existing_product = c.fetchone()

    # If the id does not exist, insert it along with default values
    if existing_product is None:
        c.execute(f'''
            INSERT INTO products_size
            (id, product_S_Count, product_M_count, product_L_count, 
            product_XL_count, product_XXL_count, product_XXXL_count)
            VALUES (?, 0, 0, 0, 0, 0, 0)
        ''', (id,))
    else:
        pass

    conn.commit()
    conn.close()

def create_product_image_table(DATABASE, id):
    print(f'ID is {id}')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS product_{id}_image (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imagePath TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def get_individual_product(DATABASE, id):
    create_prodcut_size_table(DATABASE, id)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM products_size WHERE id=?", (id,))
    product = c.fetchone()
    c.execute("SELECT * FROM products where id=?", (id,))
    product_main = c.fetchone()
    conn.close()
    filename = product_main[-1]
    
    with open(filename, 'rb') as f:
        image_data = f.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
    
    f.close()

    try:
        if product_main:
            return {
                "id": product[0],
                "productName": product_main[1],
                "productPrice": product_main[2],
                "productDiscount": product_main[3],
                "productDescriptionUpper": product_main[4], 
                "productMaterial": product_main[5],
                "productDescriptionLower": product_main[6],  
                "productPrintType": product_main[7], 
                "product_S_Count": product[1],
                "product_M_count": product[2],
                "product_L_count": product[3],
                "product_XL_count": product[4],
                "product_XXL_count": product[5],
                "product_XXXL_count": product[6],
                "productImage": encoded_image,
            }
        else:
            return {"error": "Product not found"}

    except Exception as e:
        print(e)