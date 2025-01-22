from flask import Flask, redirect, url_for, render_template, request, session, flash
from admin_feature import admin_blueprint
from user_feature import user_blueprint
from logistic_feature import logistic_blueprint
from seller_feature import seller_blueprint
from products import product_blueprint
from db import get_connect_db
import os

app = Flask(__name__)
app.secret_key = "Strong_Key_Secret_Key"

app.register_blueprint(admin_blueprint, url_prefix="/admin")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(logistic_blueprint, url_prefix="/logistic")
app.register_blueprint(seller_blueprint, url_prefix="/seller")
app.register_blueprint(product_blueprint, url_prefix="/product")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        try:
            # Get user input from the form
            fname = request.form.get("first_name")
            lname = request.form.get("last_name")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            
            if password != confirm_password:
                print(f'{password} != {confirm_password}')
                flash("Password confirmation does not match.", "danger")
                return redirect(url_for("signup"))
            
            # Connect to the database
            with get_connect_db() as con:
                cur = con.cursor()
                
                # Check if the email already exists
                cur.execute("SELECT * FROM user WHERE email = ?", (email,))
                user = cur.fetchone()
                if user:
                    flash("Email already exists. Please log in or use a different email.", "danger")
                    return redirect(url_for("signup"))
                
                # Insert the new user into the database
                cur.execute(
                    "INSERT INTO user (firstName, lastName, email, password) VALUES (?, ?, ?, ?)",
                    (fname, lname, email, password),
                )
                con.commit()
                flash("Account created successfully! You can now log in.", "success")
                return redirect(url_for("login"))
        
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for("signup"))

    # Render the sign-up page
    return render_template("signUp.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        con = get_connect_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE email = ? and password = ?", (email, password)) #checking 
        data = cur.fetchone()
        con.close()

        if data: 
            session["user_name"] = data["firstName"] + " " + data["lastName"] 
            session["email"] = data["email"]
            session["buyer_id"] = data["pid"]  
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "danger")
        
    return render_template("logIn.html")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/aboutus") 
def about_page():
    return render_template("about.html")

@app.route("/product")
def product_page():
    con = get_connect_db()
    cur = con.cursor()
    products = cur.execute("SELECT * FROM products").fetchall()
    
    return render_template("product.html", products=products)

@app.route("/mockHome")
def mockHome():
    return render_template("mockHome.html")

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(debug=True)
 