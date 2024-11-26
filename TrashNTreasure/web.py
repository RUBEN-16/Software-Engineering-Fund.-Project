from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response
from admin_feature import admin_blueprint
from user_feature import user_blueprint, get_connect_db_user_
from logistic_feature import logistic_blueprint, get_connect_db_logistic


app = Flask(__name__)
app.secret_key = "Strong_Key"

app.register_blueprint(admin_blueprint, url_prefix="/admin")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(logistic_blueprint, url_prefix="/logistic")

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
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            if con:  # Check if con is initialized
                con.close()
    return render_template("signUp.html")

@app.route("/login", methods=["POST", "GET"])
def login():
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
            return redirect(url_for("user.user_page"))
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
    return render_template("product.html")

@app.route("/mockHome")
def mockHome():
    return render_template("mockHome.html")

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(debug=True)
