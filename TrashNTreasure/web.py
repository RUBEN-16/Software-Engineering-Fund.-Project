from flask import Flask, redirect, url_for, render_template, request, session

app = Flask(__name__)
app.secret_key = "Hi"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form["first_name"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        return render_template("signUp.html")

@app.route("/login")
def login():
    return render_template("logIn.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("user_page.html", user = f"{user}")
    else:
        return redirect(url_for("signup"))


if __name__ == "__main__":
    app.run(debug=True)
