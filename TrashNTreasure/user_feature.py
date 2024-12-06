from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
import sqlite3

user_blueprint = Blueprint("user", __name__, template_folder="templates")

DATABASE_PATH = "TrashNTreasure/database.db"

# Admins database
con=sqlite3.connect(DATABASE_PATH)
con.execute("""
    CREATE TABLE IF NOT EXISTS user (
        pid INTEGER PRIMARY KEY,
        firstName TEXT NOT NULL,
        lastName TEXT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
con.close() 

def get_connect_db_user_():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn 

@user_blueprint.route("/")
def user_page():
    if "user_name" in session:
        return render_template("user_page.html", admin = session["user_name"])    
    else:
        flash("Please log in to access the user account.", "danger")
        return redirect(url_for("login"))

@user_blueprint.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
