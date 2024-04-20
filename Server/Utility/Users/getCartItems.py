import sqlite3
import base64

def getCartItems(DATABASE, username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'''
        SELECT * FROM {username}_cart
    ''')
    data = c.fetchall()
    print(data)

    product_arr = []
    
    for item in data:
        item = list(item)
        c.execute('''
            SELECT * FROM products WHERE productName = ?
        ''', (item[1],))  # Add comma after the value to create a tuple with one element
        product_data = c.fetchone()
        print(product_data)
        product_id = product_data[0]
        productName = product_data[1]
        productPrice = product_data[2]
        productDiscount = product_data[3]
        productImage = product_data[8]

        with open(productImage, 'rb') as f:
            image_data = f.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')

        c.execute(
            f'''SELECT * FROM products_size WHERE id = ?''', (product_id,)
        )

        size_data = c.fetchone()
        product_S_count = size_data[1]
        product_M_count = size_data[2]
        product_L_count = size_data[3]
        product_XL_count = size_data[4]
        product_XXL_count = size_data[5]
        product_XXXL_count = size_data[6]

        dict = {
            "productID": product_id,
            "productName": productName,
            "productPrice": productPrice,
            "productDiscount": productDiscount,
            "productImage": encoded_image,
            "product_S_count": product_S_count,
            "product_M_count": product_M_count,
            "product_L_count": product_L_count,
            "product_XL_count": product_XL_count,
            "product_XXL_count": product_XXL_count,
            "product_XXXL_count": product_XXXL_count,
            "userProductSize": item[2],
            "userItemCount": item[-1]
        }

        product_arr.append(dict)

    return product_arr
