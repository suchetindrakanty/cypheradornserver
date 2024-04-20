import sqlite3

def addToCart(DATABASE, productName, username, productSize, productCount):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {username}_cart (
            testId INTEGER PRIMARY KEY AUTOINCREMENT,
            productName TEXT NOT NULL,
            productSize TEXT NOT NULL,
            productCount INTEGER NOT NULL
        )
    ''')

    c.execute(f'SELECT * FROM {username}_cart WHERE productName=?', (productName,))
    existing_data = c.fetchone()

    if existing_data:
        return {
            "message": "Already in cart :)"
        }
    else:
        c.execute(f'''
            INSERT INTO {username}_cart (
                productName,
                productSize,
                productCount
            ) VALUES (?,?,?)
        ''', (productName, productSize, productCount))

        conn.commit()
        conn.close()

        return {
            "message": "Succesfully added to cart"
        }