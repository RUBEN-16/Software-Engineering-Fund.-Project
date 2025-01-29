from flask import Blueprint, flash, redirect, url_for
import sqlite3

database_blueprint = Blueprint("database", __name__)

DATABASE_PATH = "TrashNTreasure/database.db"

con=sqlite3.connect(DATABASE_PATH)

# User database
con.execute("""
    CREATE TABLE IF NOT EXISTS user (
        pid INTEGER PRIMARY KEY AUTOINCREMENT,
        firstName TEXT NOT NULL,
        lastName TEXT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        isSeller INTEGER DEFAULT 0,
        haveBankCard INTEGER DEFAULT 0,
        phone_number TEXT,
        wallet DECIMAL(10, 2) DEFAULT 0.00,
        address TEXT
    )
""")

# Logistic members database
con.execute("""
    CREATE TABLE IF NOT EXISTS member (
        pid INTEGER PRIMARY KEY AUTOINCREMENT,
        firstName TEXT NOT NULL,
        lastName TEXT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")

#  Seller registers database
con.execute("""
    CREATE TABLE IF NOT EXISTS seller_registration (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        ic_picture TEXT NOT NULL,
        profile_picture TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (id) REFERENCES user(pid) ON DELETE CASCADE
    )
""")

# Seller database
con.execute("""
    CREATE TABLE IF NOT EXISTS sellers (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT NOT NULL,
        FOREIGN KEY (id) REFERENCES user(pid) ON DELETE CASCADE ON UPDATE CASCADE
    )
""")

# E-Wallet Transaction database
con.execute("""
    CREATE TABLE IF NOT EXISTS wallet_transaction (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        date DATE NOT NULL,
        description TEXT NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (buyer_id) REFERENCES user(pid) ON DELETE CASCADE ON UPDATE CASCADE
    )
""")

# Order database
con.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        date DATE NOT NULL,
        payment_method TEXT NOT NULL,
        delivery_status TEXT DEFAULT 'Pending',
        seller_status TEXT DEFAULT 'Pending',
        total_amount DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (buyer_id) REFERENCES user(pid) ON DELETE CASCADE ON UPDATE CASCADE
        FOREIGN KEY (product_id) REFERENCES products(id) 
    )
""")

# Feedback database
con.execute("""
    CREATE TABLE IF NOT EXISTS feedback2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (buyer_id) REFERENCES user(pid) ON DELETE CASCADE ON UPDATE CASCADE
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE ON UPDATE CASCADE
    )
""")

# Pickup Request database
con.execute("""
    CREATE TABLE IF NOT EXISTS pickup_request (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        seller_id INTEGER NOT NULL,
        courier TEXT NOT NULL,
        seller_address TEXT NOT NULL,
        buyer_address TEXT NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE ON UPDATE CASCADE
        FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE ON UPDATE CASCADE
    )
""")

# Cart database
con.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        max_quantity INTEGER NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        product_image_path TEXT NOT NULL,
        FOREIGN KEY (buyer_id) REFERENCES user(pid) 
        FOREIGN KEY (product_id) REFERENCES products(id) 
    )
""")

# Product database
con.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        quantity INTEGER NOT NULL,
        condition TEXT NOT NULL,
        seller_id TEXT NOT NULL,
        image_path TEXT,
        video_path TEXT,
        FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE
    )
    """)

con.close()

# Database connection
def get_connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn 

# Save the approved seller in the sellers database
def seller_database(ID):
    con = get_connect_db()
    cur = con.cursor()
    try:
        # Fetch user and seller registration details
        selling_user_data = cur.execute("SELECT * FROM user WHERE pid = ?", (ID,)).fetchone()
        selling_registered_data = cur.execute("SELECT * FROM seller_registration WHERE id = ?", (ID,)).fetchone()
        
        # Check if the user and registration data exist
        if not selling_user_data:
            flash(f"No eligible user found for seller creation with ID {ID}", "danger")
            return
        if not selling_registered_data:
            flash(f"No registration data found for seller with ID {ID}", "danger")
            return

        # Extract relevant details from seller_registration
        name = selling_registered_data["name"]
        email = selling_registered_data["email"]
        phone_number = selling_registered_data["phone_number"]

        # Insert into sellers table
        cur.execute(
            "INSERT INTO sellers (id, name, email, phone_number) VALUES (?, ?, ?, ?)",
            (ID, name, email, phone_number)
        )
        
        # Update the user's phone number in the user table (if necessary)
        cur.execute(
            "UPDATE user SET phone_number = ? WHERE pid = ?",
            (phone_number, ID)
        )

        # Commit changes to the database
        con.commit()
        flash(f"Seller with ID {ID} has been successfully added to the database.", "success")
    except Exception as e:
        flash(f"An error occurred while creating seller: {e}", "danger")
    finally:
        if con:
            con.close()





