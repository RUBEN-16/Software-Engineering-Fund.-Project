from flask import Blueprint, flash, redirect, url_for
import sqlite3

database_blueprint = Blueprint("database", __name__)

DATABASE_PATH = "TrashNTreasure/database.db"

con=sqlite3.connect(DATABASE_PATH)

# Admins database
con.execute("""
    CREATE TABLE IF NOT EXISTS user (
        pid INTEGER PRIMARY KEY,
        firstName TEXT NOT NULL,
        lastName TEXT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        isSeller INTEGER DEFAULT 0,
        haveBankCard INTEGER DEFAULT 0,
        phone_number TEXT
    )
""")

# Logistic members database
con.execute("""
    CREATE TABLE IF NOT EXISTS member (
        pid INTEGER PRIMARY KEY,
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
        ic_picture TEXT NOT NULL,
        profile_picture TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (id) REFERENCES user(pid) ON DELETE CASCADE ON UPDATE CASCADE
    )
""")

# Seller database
con.execute("""
    CREATE TABLE IF NOT EXISTS sellers (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
""")

con.close()

def get_connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn 


def seller_database(ID):
    con = get_connect_db()
    cur = con.cursor()
    try:
        selling_user = cur.execute("SELECT * FROM user WHERE pid = ?", (ID,)).fetchone()
        con.commit()
        if not selling_user:
            flash(f"No eligible user found for seller creation with ID {ID}", "danger")
            return
        name = selling_user["firstName"] + selling_user["lastName"]
        email = selling_user["email"]
        cur.execute("INSERT INTO sellers (id, name, email) VALUES (?, ?, ?)",(ID, name, email))
        con.commit()
    except Exception as e:
        flash(f"An error occurred while creating seller: {e}", "danger")
    finally:
        if con:
            con.close()




