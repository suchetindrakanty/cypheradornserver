import sqlite3
import random

email_sender = 'sunnytaneti2005@gmail.com'
email_password = 'tvdd enlp glwa qovz'

def checkUser(DATABASE, userName, email):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
              userID INTEGER PRIMARY KEY,
              userName TEXT UNIQUE,
              email TEXT UNIQUE,
              password TEXT
        )
    ''')

    try:
        c.execute('''SELECT userName FROM users''')
        userNames = c.fetchall()

        c.execute('''SELECT email FROM users''')
        emails = c.fetchall()

        if (userName,) in userNames or (email,) in emails:
            print(f'{userName} or {email} already exists. Please use another.')
            return {
                "error": f'{userName} or {email} already exists. Please use another username or email..'
            }, True

        else:
            return {
                "success": "No account present."
            }, False
    
    except Exception as e:
        print('Database connectivity error.')

def createUser(DATABASE, userName, email, password):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
              userID INTEGER PRIMARY KEY,
              userName TEXT UNIQUE,
              email TEXT UNIQUE,
              password TEXT
        )
    ''')

    c.execute('''SELECT userID FROM users''')
    existingUserIDs = c.fetchall()

    userID = random.randint(1000000, 9999999)
    while (userID,) in existingUserIDs:
        userID = random.randint(1000000, 9999999)

    try:
        c.execute('''
            INSERT INTO users (userID, userName, email, password) VALUES (?, ?, ?, ?)
        ''', (userID, userName, email, password))

        conn.commit()  # Commit the transaction

        return {
            "Success": "Account Created"
        }
    
    except sqlite3.IntegrityError as e:
        print(f'Error has occurred: \n{e}')
        return {"error": str(e)}
    
    finally:
        conn.close()  # Close the connection after executing the query

