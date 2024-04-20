import sqlite3
import json
import ast

def getOrder(DATABASE, username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'SELECT * FROM {username}_order')
    orderData = c.fetchall()

    inform_arr = []

    for order in orderData:
        item_arr = []

        # Parse the JSON string representing the list of products
        products = json.loads(order[1])
        # Iterate over each product dictionary in the list
        for product in products:
            order_dict = {
                "productName": product.get("productName", ""),
                "productPrice": product.get("productPrice", 0),
                "userItemCount": product.get("userItemCount", 0),
                "userProductSize": product.get("userProductSize", "")
            }
            item_arr.append(order_dict)

        inform_dict = {
            "orderID": order[0],
            "productItems": item_arr,
            "productPrice": order[3],
            "productStatus": order[4]
        }

        inform_arr.append(inform_dict)

    conn.close()

    return inform_arr

def getAdminOrder(DATABASE):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'SELECT * FROM orders')
    orderData = c.fetchall()

    inform_arr = []

    for order in orderData:
        item_arr = []
        # Parse the JSON string representing the list of products
        products = json.loads(order[2])
        for product in products:
            order_dict = {
                "productName": product.get("productName", ""),
                "productPrice": product.get("productPrice", 0),
                "userItemCount": product.get("userItemCount", 0),
                "userProductSize": product.get("userProductSize", "")
            }
            print(product.get("userItemCount", 0))
            item_arr.append(order_dict)

        inform_dict = {
            "orderID": order[0],
            "username": order[1],
            "productPrice": order[4],
            "productItems": item_arr,
            "productStatus": order[5],
            "address": order[3],
            "phoneNum": order[-1]
        }

        inform_arr.append(inform_dict)

    conn.close()

    return inform_arr

