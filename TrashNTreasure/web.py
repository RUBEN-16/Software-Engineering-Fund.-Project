from flask import Flask, redirect, url_for, render_template, request, session, flash
import sqlite3


app = Flask(__name__)
app.secret_key = "Strong_Key"

# Admins database
con=sqlite3.connect("database_user.db")
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

def get_connect_db_user_():
    conn = sqlite3.connect("database_user.db")
    conn.row_factory = sqlite3.Row
    return conn
def get_connect_db_logistic():
    conn = sqlite3.connect("database_logistics.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    con = None 
    if request.method == "POST":
        try:
            fname = request.form["first_name"]
            lname = request.form["last_name"]
            email = request.form["email"]
            password = request.form["password"]
            
            con = get_connect_db_user_() # Initialize the connection here
            cur = con.cursor()
            
            cur.execute("SELECT * FROM user WHERE email = ?", (email,))
            user = cur.fetchone()
            
            if user:  # If a record is found    
                flash("Email already exists!", "danger")
                return redirect(url_for("signup"))
            cur.execute("INSERT INTO user (firstName, lastName, email, password) VALUES (?, ?, ?, ?)",(fname, lname, email, password),)
            con.commit()
            flash("Account Created Successfully!", "success")
            return redirect(url_for("login_user"))
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            if con:  # Check if con is initialized
                con.close()
    return render_template("signUp.html")


@app.route("/login", methods=["POST", "GET"])
def login_user():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        con = get_connect_db_user_()
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE email = ? and password = ?", (email, password)) #checking 
        data = cur.fetchone()
        con.close()

        if data:
            session["user_name"] = data["firstName"]  
            return redirect(url_for("user"))
        else:
            flash("Invalid email or password", "danger")
            return render_template("logIn.html")
        
    return render_template("logIn.html")
@app.route("/loginAdmin", methods=["POST", "GET"])
def login_admin():
    admins = [
        {"Username": "ruben123", "Password" : "passRuben", "Name" : "Rubeneswaran"},
        {"Username": "thris987", "Password" : "passThris", "Name" : "Thrissha"},
        {"Username": "nasss123", "Password" : "passNasss", "Name" : "Nasreen"}
    ]
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        for admin in admins:
            if admin["Username"] == username and admin["Password"] == password:
                session["admin_name"] = admin["Name"] 
                return redirect(url_for("admin"))
            
        flash("Invalid username and password", "danger")
        return render_template("adminlogin_page.html")

    return render_template("adminlogin_page.html")

@app.route("/addLogistic", methods=["POST", "GET"])
def adding_logistic():
    con = None 
    if request.method == "POST":
        try:
            action = request.form.get("action")
            if action == "Register":
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
                    return redirect(url_for("adding_logistic"))
                cur.execute("INSERT INTO member (firstName, lastName, email, password) VALUES (?, ?, ?, ?)",(fname, lname, email, password),)
                con.commit()
                flash("Account Created Successfully!", "success")
                return redirect(url_for("adding_logistic"))
            elif action == "Back":
                return redirect(url_for("admin"))
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            if con:  # Check if con is initialized
                con.close()
    return render_template("mem_hiring.html")

@app.route("/logisticlogin", methods=["POST", "GET"])
def login_logistic():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        con = get_connect_db_logistic()
        cur=con.cursor()
        cur.execute("SELECT * FROM member WHERE email = ? and password = ?", (email, password)) #checking 
        data=cur.fetchone()
        con.close()

        if data:
            session["member_name"] = data["firstName"]  
            return redirect(url_for("logistic"))
        else:
            flash("Invalid username or password", "danger")
            return render_template("logisticlogin_page.html")
        
    return render_template("logisticlogin_page.html")

@app.route("/aboutus")
def about_page():
    return render_template("about.html")

@app.route("/product")
def product_page():
    return render_template("product.html")

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.route("/admin")
def admin():
    if "admin_name" in session:
        return render_template("admin_page.html", admin = session["admin_name"])    
    else:
        flash("Please log in to access the admin account.", "danger")
        return redirect(url_for("login_admin"))

@app.route("/logistic")
def logistic():
    return render_template("logistic_page.html")

@app.route("/user")
def user():
    if "user_name" in session:
        return render_template("user_page.html", admin = session["user_name"])    
    else:
        flash("Please log in to access the user account.", "danger")
        return redirect(url_for("login"))
    
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
