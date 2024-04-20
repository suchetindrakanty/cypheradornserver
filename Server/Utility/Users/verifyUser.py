import sqlite3

def verifyUser(DATABASE, username, password):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(f'''
        SELECT password FROM users WHERE username = ?
    ''', (username,))

    password_backend = c.fetchone()
    print(password_backend)

    c.execute(f'''
        SELECT email FROM users WHERE username = ?
    ''', (username,))

    email = c.fetchone()

    if str(password_backend[0])  == str(password):
        print('Access granted')
        return {
            "message": "Okay",
            "username": username,
            "email": email[0],
            "password": password
        }
    
    elif password_backend != password:
        return {
            "message": "2"  # Incorrect password
        }
    else:
        return {
            "message": "Database error"  # User not found
        }