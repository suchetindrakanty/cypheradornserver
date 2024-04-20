import flask
from flask import jsonify, request, send_from_directory, Flask
from flask_cors import CORS

import random
import os 
import sqlite3
import time
import json
import base64

from Utility.Products.AddProduct import create_product_table
from Utility.Products.EditProduct import get_individual_product, create_product_image_table
from Utility.Products.acquireProduct import acquireProductsForProductPage

from Utility.Users.addUser import createUser, checkUser
from Utility.Users.verifyUser import verifyUser
from Utility.Users.addToCart import addToCart
from Utility.Users.getCartItems import getCartItems

from Utility.Orders.placeOrder import placeOrder

from Utility.Orders.getOrder import getOrder, getAdminOrder

from email.message import EmailMessage
import ssl
import smtplib

import razorpay

PORT = 5000
YOUR_RAZORPAY_KEY = 'rzp_test_lqoZxQ0py4H1U5'
YOUR_RAZORPAY_SECRET = '3vdC6Z2dhYtNRua1eJpIaEIJ'

app = Flask(__name__, static_folder=r'DataBases/', static_url_path='')
CORS(app)

DATABASE = r'main.db'
UPLOAD_FOLDER = r'DataBases/Assets/ProductImage'
UPLOAD_IMAGES = r'DataBases/Assets/ProductIndivImages'

os.makedirs(UPLOAD_IMAGES, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_IMAGES'] = UPLOAD_IMAGES
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        create_product_table(DATABASE)
        product_name = request.form['productName']
        product_price = request.form['productPrice']
        product_discount = request.form['productDiscount']
        product_desc_upper = request.form['productDescriptionUpper']
        product_material = request.form['productMaterial']
        product_desc_lower = request.form['productDescriptionLower']
        product_print_type = request.form['productPrintType']

        product_images = request.files.getlist('productImages')
        
        conn = sqlite3.connect(DATABASE)
        conn.execute("BEGIN TRANSACTION")  # Begin transaction explicitly

        # Insert product details into the database
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (productName, productPrice, productDiscount, productDescriptionUpper, productMaterial, productDescriptionLower, productPrintType) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (product_name, product_price, product_discount, product_desc_upper, product_material, product_desc_lower, product_print_type))
            product_id = cursor.lastrowid
        
        # Update product images
        for img in product_images:
            if img.filename != '':
                path = os.path.join(app.config["UPLOAD_FOLDER"], img.filename).replace('\\', '/')
                img.save(path)
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET productImage = ? WHERE id = ?", (path, product_id))
        
        conn.execute("COMMIT")  # Commit transaction explicitly
        conn.close()

        return jsonify({'success': True}), 200
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to add product'}), 500

@app.route('/get_edit_page_products', methods=['GET'])
def get_edit_page_products():
    try:
        print('Debug 1')
        conn = sqlite3.connect('main.db')
        c = conn.cursor()
        c.execute('SELECT * FROM products')
        products = c.fetchall()
        print(products[0])
        conn.close()
        
        products_dict = []
        
        for product in products:
            try:
                with open(product[-1], 'rb') as f:
                    image_data = f.read()
                
                encoded_image = base64.b64encode(image_data).decode('utf-8')

                product_dict = {
                    'id': product[0],
                    'productName': product[2],
                    'productPrice': product[3],
                    'productImage': encoded_image
                }

                products_dict.append(product_dict)
            except FileNotFoundError as e:
                print(f"File not found: {product[4]}")
                continue
            except Exception as e:
                print(f"Error reading file: {e}")
                continue

        return jsonify(products_dict)

    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/get_individual_product', methods=['POST'])
def getProduct():
    print('Got connection on here')
    id = request.args.get('id')
    product = get_individual_product(DATABASE, id)
    try:
        if product:
            return product
         
        else:
            return {"error"}
    
    except Exception as e:
        print(e)

@app.route('/update_product', methods=['POST'])
def updateProduct():
    try:
        print('1')
        id = request.args.get('id')
        create_product_image_table(DATABASE, id)
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # Process the request data
        formData = request.form

        productName = formData.get('productName')
        productPrice = formData.get('productPrice')
        productDiscount = formData.get('productDiscount')
        productDescriptionUpper = formData.get('productDescriptionUpper')
        productMaterial = formData.get('productMaterial')
        productDescriptionLower = formData.get('productDescriptionLower')
        productPrintType = formData.get('productPrintType')
        product_S_Count = formData.get('product_S_count')
        product_M_Count = formData.get('product_M_count')
        product_L_Count = formData.get('product_L_count')
        product_XL_Count = formData.get('product_XL_count')
        product_XXL_Count = formData.get('product_XXL_count')
        product_XXXL_Count = formData.get('product_XXXL_count')
        
        # Retrieve the files from request.files
        productCoverImage = request.files.get('productCoverImage')
        productImages = request.files.getlist('productImages')

        c.execute('''
            UPDATE products_size
            SET product_S_Count = ?,
                product_M_count = ?,
                product_L_count = ?,
                product_XL_count = ?,
                product_XXL_count = ?,
                product_XXXL_count = ?
            WHERE id = ?
        ''', (product_S_Count, product_M_Count, product_L_Count, product_XL_Count, product_XXL_Count, product_XXXL_Count, id))

        print('2')

        # Process and save product images
        image_dir = app.config["UPLOAD_IMAGES"] + f'/{id}'
        os.makedirs(image_dir, exist_ok=True)
        
        for file in os.listdir(image_dir):
            os.remove(os.path.join(image_dir, file))

        cover_image_dir = app.config["UPLOAD_IMAGES"] + f'/{id}'
        os.makedirs(cover_image_dir, exist_ok=True)
        
        for file in os.listdir(cover_image_dir):
            os.remove(os.path.join(cover_image_dir, file))
        
        c.execute(f'DELETE FROM product_{id}_image')
        for image in productImages:   
            c.execute(f'INSERT INTO product_{id}_image (imagePath) VALUES (?)', (image_dir+f'/{image.filename}',))
            image.save(image_dir+f'/{image.filename}')

        for image in [productCoverImage]:
            image.save(cover_image_dir+f'/{image.filename}')
            c.execute('''
                UPDATE products 
                SET productName = ?,
                    productPrice = ?,
                    productDiscount = ?,
                    productDescriptionUpper = ?,
                    productMaterial = ?,
                    productDescriptionLower = ?,
                    productPrintType = ?,
                    productImage = ?
                WHERE id = ?
            ''', (productName, productPrice, productDiscount, productDescriptionUpper, 
                  productMaterial, productDescriptionLower, productPrintType, 
                  cover_image_dir+f'/{image.filename}', id))
           
        # Commit changes to the database
        conn.commit()
        conn.close()

        # Return a success response
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        print(f'Error in update product: {e}')
        # Return an error response
        return jsonify({"error": str(e)}), 500

@app.route('/addUser', methods = ['POSt'])
def addUser():
    data = request.get_json()
    userName = data.get('username')
    email = data.get('email')
    password = data.get('password')

    try:
        createUser(DATABASE, userName, email, password)
        return {
            "message": "Succesfully created the account."
        }

    except Exception as e:
        print(f'Database error: \n{e}')
        return {
            "message": "Database error."
        }

@app.route('/sendOTP', methods=['POST'])
def sendOTP():
    data = request.get_json()
    userName = data.get('username')
    email = data.get('email')
    password = data.get('password')

    try:
        check_result, user_exists = checkUser(DATABASE, userName, email)
        print(user_exists)
        if user_exists:
            return check_result, 400

        em = EmailMessage()

        email_sender = 'sunnytaneti2005@gmail.com'
        email_password = 'tvdd enlp glwa qovz'

        em['From'] = email_sender
        em['To'] = email
        em['Subject'] = 'Sign up OTP for Cypher Adorn'

        OTP = int(''.join(random.choices('0123456789', k=6)))

        body = f'''
            Your otp is {OTP}
        '''

        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email, em.as_string())
            
        return {
            "OTP": OTP
        }
    
    except Exception as e:
        print(f'Database error: \n{e}')
        return {"error": "Database error"}, 203
    
@app.route('/verifyUser', methods = ['POST'])
def verify_user():
    data = request.get_json()
    return verifyUser(DATABASE, data.get('username'), data.get('password'))

@app.route('/getProductPageDetails', methods = ['POST'])
def getProductPageDetails():
    data = request.get_json()
    id = data.get('productId')
    a = acquireProductsForProductPage(DATABASE, id)
    return a

@app.route('/addToCart', methods = ['POST'])
def add_to_cart():
    data = request.json
    print(data.get('productName'))
    a = addToCart(DATABASE, data.get('productName'), data.get('username'),data.get('productSize'), data.get('productCount'))
    return a

@app.route('/getCartProducts', methods = ['POST'])
def get_cart_items():
    data = request.get_json()
    return getCartItems(DATABASE, data.get('username'))

@app.route('/contactForm', methods = ['POST'])
def sendContactForm():
    form_data = request.json.get('formData')
    name = form_data['name']
    email = form_data['email']
    desc = form_data['description']

    em = EmailMessage()

    email_sender = 'sunnytaneti2005@gmail.com'
    email_password = 'tvdd enlp glwa qovz'

    em['From'] = email_sender
    em['To'] = email #Change this to whatever the reciever end point is
    em['Subject'] = f'Message from {name}'
    body = desc

    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email, em.as_string())
    smtp.close()

    return {
        "message": "We will get back to you shortly :)"
    }

@app.route('/getProductsPage', methods = ['POST'])    
def getProductsPage():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''select id from products''')

    ids = c.fetchall()

    productData = []

    for id in ids:
        id = id[0]
        c.execute('''select * from products where id = ?''', (id,))
        productData1 = c.fetchone()
        productName = productData1[1]
        productPrice = productData1[2]
        productDiscount = productData1[3]
        productCoverImage = productData1[-1]

        with open(productCoverImage, 'rb') as f:
            image_data = f.read()
            encoded_cover_image = base64.b64encode(image_data).decode('utf-8')
        
        f.close()

        a = {
            'productID': id,
            'productName': productName,
            'productPrice': productPrice,
            'productDiscount': productDiscount,
            'productCoverImage': encoded_cover_image
        }

        productData.append(a)
    
    return productData

@app.route('/removeCartItem', methods = ['POST'])
def removeItem():
    data = request.get_json()
    username = data.get('username')
    item = data.get('productId')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute(f'''
        DELETE from {username}_cart where productName = ?
    ''', (item, ))

    conn.commit()
    conn.close()

    return {
        "message": "okay"
    }

@app.route('/addCoupoun', methods = ['POST'])
def addCoupoun():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        create table if not exists coupouns (
            coupoun_name text unique not null,
            coupoun_num int default 1,
            coupoun_discount int default 5
        )
    ''')

    conn.commit()

    coupoun_name = request.form['coupoun_name']
    coupoun_discount = request.form['coupoun_discount']
    coupoun_num = request.form['coupoun_num']

    print(coupoun_name)
    print(coupoun_discount)
    print(coupoun_num)

    c.execute('''select * from coupouns where coupoun_name = ?''', (coupoun_name, ))
    if c.fetchall():
        conn.close()
        return {
            'message': 'Coupoun already exists :('
        }
    
    else:
        try:
            c.execute('''
                insert into coupouns (
                    coupoun_name, coupoun_num, coupoun_discount
                ) values (?, ?, ?)
            ''', (coupoun_name, coupoun_num, coupoun_discount))

            conn.commit()
            conn.close()

            return {
                'message': 'Added Succesfully :)'
            }    
        
        except Exception as e:
            print(e)
            conn.close()
            return {
                'message': 'Database error.'
            }

@app.route('/getDiscount', methods = ['POST'])
def getDiscount():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    name = request.form['coupoun_name']
    c.execute('''select coupoun_discount from coupouns where coupoun_name = ?''', (name,))
    name = c.fetchone()
    if name:
        return {
            'discount': name
        }
    else:
        return {
            'discount': 'No coupoun :('
        }

@app.route('/createOrder', methods=['POST'])
def createOrder():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT orderID FROM orders')
    orderIDS = c.fetchall()

    orderID = random.randrange(10000, 999999)
    while orderID in orderIDS:
        orderID = random.randrange(10000, 999999)

    data = request.get_json()
    phone = data.get('phone')
    address = data.get('address')
    amount = data.get('totalPrice')

    print(address)
    
    data = request.get_json()
    print(orderID)
    razorpay_client = razorpay.Client(auth=(YOUR_RAZORPAY_KEY, YOUR_RAZORPAY_SECRET))

    try:
        order = {
            'amount': int(data.get('totalPrice')) * 100,
            'currency': 'INR',
            'receipt': f'{orderID}',
            'payment_capture': '1'
        }

        created_order = razorpay_client.order.create(data=order)
        print(created_order['id'])

        return {
            'message': created_order['id'],
            'key': YOUR_RAZORPAY_KEY,
            'OID': orderID,
            'address': address,
            'phone': phone,
            'amount': amount
        }, 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Error creating order'}), 500

@app.route('/placeOrder', methods = ['POST'])
def place_order():
    data = request.get_json()
    items = data.get('items')
    username = data.get('username')
    address = data.get('address')
    price = data.get('price')
    status = data.get('status')
    phoneNo = data.get('phoneNo')
    oid = data.get('OID')

    print(username)
    print(address)
    print(price)
    print(status)
    print(phoneNo)
    print(oid)

    a = placeOrder(DATABASE, items, username, address, price, status, phoneNo, oid)

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'delete from {username}_cart')
    conn.commit()

    c.execute('select email from users where username = ?', (username, ))
    email = c.fetchone()
    
    em = EmailMessage()

    email_sender = 'sunnytaneti2005@gmail.com'
    email_password = 'tvdd enlp glwa qovz'

    em['From'] = email_sender
    em['To'] = email 
    em['Subject'] = f'Updte on your prudct - Cypher Adorn'
    body = ''

    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email, em.as_string())
    smtp.close()

    return a

@app.route('/getOrderStatus', methods = ['POST'])
def getOrderStatus():
    data = request.get_json()
    username = data.get('username')
    a = getOrder(DATABASE, username)
    return a

@app.route('/getAdminOrders', methods = ['POST'])
def get_admin_order():
    a = getAdminOrder(DATABASE)
    return a

@app.route('/updateOrderStatus', methods=['POST'])
def updateOrderStatus():
    data = request.get_json()
    status = data.get('newStatus')
    orderId = int(data.get('orderId'))
    username = data.get('username')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Update order status in the 'orders' table
    c.execute('UPDATE orders SET status = ? WHERE orderID = ?', (status, orderId,))
    # Update order status in the user's cart table
    c.execute(f'UPDATE {username}_order SET status = ? WHERE orderID = ?', (status, orderId,))
    conn.commit()

    c.execute('select email from users where username = ?', (username,))
    email = c.fetchone()

    em = EmailMessage()

    email_sender = 'sunnytaneti2005@gmail.com'
    email_password = 'tvdd enlp glwa qovz'

    em['From'] = email_sender
    em['To'] = email
    em['Subject'] = 'Your order status has been updated - Cypher Adorn'

    body = f'''
        Your order status is {status}
    '''

    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email, em.as_string())
    
    conn.close()

    return {
        'message': 'Success'
    }

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == '__main__':
    print('Running I guess')
    app.run(debug=True, port=PORT)