from flask import Blueprint, redirect, url_for, render_template, session, flash
import sqlite3

product_blueprint = Blueprint('product', __name__, template_folder="templates")

DATABASE_PATH = "TrashNTreasure/database.db"

# Admins database
con=sqlite3.connect(DATABASE_PATH)
con.execute("""
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pName TEXT NOT NULL,
        pCategory TEXT NOT NULL,
        pPrice REAL NOT NULL,
        pQuantity INTEGER NOT NULL,
        pCondition TEXT NOT NULL,
        pImage TEXT NOT NULL,
        pVideo TEXT
        pSeller_ID INTEGER NOT NULL,
        FOREIGN KEY (pSeller_ID) REFERENCES sellers(id)
    )
""")
con.close() 

def get_connect_db_product():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn 

@product_blueprint.route("/add_product")
def add_product_page():
    return render_template("add_product_page.html")
