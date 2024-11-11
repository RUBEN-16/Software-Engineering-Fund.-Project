from flask import Flask, redirect, url_for, render_template, request, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "Hi"

con=sqlite3.connect("database.db")
con.execute("create table if not exists user(pid integer primary key, firstName text, lastName text, email text, password text)")
con.close()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        try:
            fname = request.form["first_name"]
            lname = request.form["last_name"]
            email = request.form["email"]
            password = request.form["password"]
            
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("insert into user(firstName,lastName,email,password)values(?,?,?,?)", (fname,lname,email,password))
            con.commit()
            flash("Account Saved", "success")
            print("Redirecting to login page")
            return redirect(url_for("login"))
        except:
            flash("Error in insertion", "danger")
        finally:
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
        cur.execute("select * from user where firstName=? and password=?", (name,password)) #checking 
        data=cur.fetchone()
        con.close()
        if data:
            session["firstName"] = data["firstName"]
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
    return redirect(url_for("signup"))

if __name__ == "__main__":
    app.run(debug=True)
