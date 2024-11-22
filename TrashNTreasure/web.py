from flask import Flask, redirect, url_for, render_template, request, session, flash
import sqlite3


app = Flask(__name__)
app.secret_key = "Strong_Key"

con=sqlite3.connect("database.db")
con.execute("create table if not exists user(pid integer primary key, firstName text, lastName text, email text, password text)")
con.close()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    con = None  # Initialize con to None
    if request.method == "POST":
        try:
            fname = request.form["first_name"]
            lname = request.form["last_name"]
            email = request.form["email"]
            password = request.form["password"]
            
            con=sqlite3.connect("database.db") # Initialize the connection here
            cur = con.cursor()
            cur.execute(
                "INSERT INTO user (firstName, lastName, email, password) VALUES (?, ?, ?, ?)",
                (fname, lname, email, password),
            )
            con.commit()
            flash("Account Created Successfully!", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists. Please use a different email.", "danger")
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            if con:  # Check if con is initialized
                con.close()
    return render_template("signUp.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("SELECT * FROM user WHERE firstName=?", (name,)) #checking 
        data=cur.fetchone()
        con.close()

        if data:
            session["firstName"] = data["firstName"]
            flash("Login successful!", "success")   
            return redirect(url_for("user"))
        else:
            flash("Invalid email and password", "danger")
            return render_template("logIn.html")
        
    return render_template("logIn.html")

    

@app.route("/user", methods=["GET", "POST"])
def user():
        return render_template("user_page.html")
    
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
