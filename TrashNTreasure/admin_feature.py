from flask import Blueprint, redirect, url_for, render_template, request, session, flash
import sqlite3

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")

# Logistic members database
con=sqlite3.connect("database_logistics.db")
con.execute("""
    CREATE TABLE IF NOT EXISTS member (
        pid INTEGER PRIMARY KEY,
        firstName TEXT NOT NULL,
        lastName TEXT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
con.close()

def get_connect_db_logistic():
    conn = sqlite3.connect("database_logistics.db")
    conn.row_factory = sqlite3.Row
    print("Database connected successfully")
    return conn


@admin_blueprint.route("/login", methods=["POST", "GET"])
def login():
    admins = [
        {"Username": "ruben123", "Password" : "passRuben", "Name" : "Rubeneswaran"},
        {"Username": "thris987", "Password" : "passThris", "Name" : "Thrissha"},
        {"Username": "nasss123", "Password" : "passNasss", "Name" : "Nasreen"}
    ]
    if request.method == "POST":
        action = request.form.get("action")
        if action == "Login":
            username = request.form["username"]
            password = request.form["password"]
            
            for admin in admins:
                if admin["Username"] == username and admin["Password"] == password:
                    session["admin_name"] = admin["Name"] 
                    return redirect(url_for("admin.dashboard"))
                
            flash("Invalid username and password", "danger")
            return render_template("adminlogin_page.html")
        elif action == "Back":
            return redirect(url_for("home"))

    return render_template("adminlogin_page.html")

@admin_blueprint.route("/")
def dashboard():
    if "admin_name" in session:
        return render_template("admin_page.html", admin = session["admin_name"])    
    else:
        flash("Please log in to access the admin account.", "danger")
        return redirect(url_for("admin.login"))
    
@admin_blueprint.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))

@admin_blueprint.route("/addLogistic", methods=["POST", "GET"])
def adding_logistic():
    con = None 
    if request.method == "POST":
        try:
            action = request.form.get("action")
            if action == "Hire":
                fname = request.form["first_name"]
                lname = request.form["last_name"]
                email = request.form["email"]
                password = request.form["password"]
                
                
                
                con = get_connect_db_logistic() # Initialize the connection here
                cur = con.cursor()
                cur.execute("SELECT * FROM member WHERE email = ?", (email,))
                member = cur.fetchone()
                
                if member:  # If a record is found
                    flash("Email already exists!", "danger")
                    return redirect(url_for("admin.adding_logistic"))
                cur.execute("INSERT INTO member (firstName, lastName, email, password) VALUES (?, ?, ?, ?)",(fname, lname, email, password),)
                con.commit()
                flash("Account Created Successfully!", "success")
                return redirect(url_for("admin.adding_logistic"))
            elif action == "Back":
                return redirect(url_for("admin.dashboard"))
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            if con:  # Check if con is initialized
                con.close()
    return render_template("mem_hiring.html")