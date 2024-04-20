import sqlite3

import base64
import os 
import time

def acquireProductsForProductPage(DATABASE, id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM products WHERE id = ?
    ''', (id, ))
    productData = c.fetchall()
    productData = productData[0]
    productName = productData[1]
    productPrice = productData[2]
    productDiscount = productData[3]
    productDescriptionUpper = productData[4]
    productMaterial = productData[5]
    productDescriptionLower = productData[6]
    productPrintType = productData[7]
    productCoverImage = productData[-1]

    with open(productCoverImage, 'rb') as f:
        image_data = f.read()
        encoded_cover_image = base64.b64encode(image_data).decode('utf-8')

    c.execute(f'''SELECT imagePath FROM product_{id}_image''')
    imagePaths = c.fetchall()
    print(imagePaths)
    imageData = []

    for filename in imagePaths:
        with open(filename[0], 'rb') as f:
            image_data = f.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
        f.close()
        imageData.append(encoded_image)

    print(f'length is {len(imageData)}')
    
    c.execute('''
        SELECT * FROM products_size where id = ?
    ''', (id,))
    
    size_data = c.fetchone()
    
    product_S_count = size_data[1]
    product_M_count = size_data[2]
    product_L_count = size_data[3]
    product_XL_count = size_data[4]
    product_XXL_count = size_data[5]
    product_XXXL_count = size_data[6]

    return {
        "productName": productName,
        "productPrice": productPrice,
        "productDiscount": productDiscount,
        "productDescriptionUpper": productDescriptionUpper,
        "productMaterial": productMaterial,
        "productDescriptionLower": productDescriptionLower,
        "productPrintType": productPrintType,
        "product_S_count": product_S_count,
        "product_M_count": product_M_count,
        "product_L_count": product_L_count,
        "product_XL_count": product_XL_count,
        "product_XXL_count": product_XXL_count,
        "product_XXXL_count": product_XXXL_count,
        "productCoverImage": encoded_cover_image,
        "productImages": imageData
    }