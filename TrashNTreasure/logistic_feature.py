from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
from db import get_connect_db

logistic_blueprint = Blueprint("logistic", __name__, template_folder="templates")

@logistic_blueprint.route("/logisticlogin", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        con = get_connect_db()
        cur=con.cursor()
        cur.execute("SELECT * FROM member WHERE email = ? and password = ?", (email, password)) #checking 
        data = cur.fetchone()
        con.close()

        if data:
            session["member_name"] = data["firstName"]  
            session["member_id"] = data["pid"]  
            return redirect(url_for("logistic.dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return render_template("logisticlogin_page.html")
        
    return render_template("logisticlogin_page.html")


@logistic_blueprint.route("/")
def dashboard():    
    if "member_id" in session:
        return render_template("logistic_page.html")
    else:
        flash("Please log in to access the admin account.", "danger")
        return redirect(url_for("logistic.login"))
    
@logistic_blueprint.route("/pickup_manage")
def pickup_management():
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    
    return render_template("pickup_management.html")

@logistic_blueprint.route("/delivery_manage")
def delivery_management():
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    
    return render_template("delivery_management.html")

@logistic_blueprint.route("/order_manage")
def order_management():
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    
    return render_template("order_management.html")

@logistic_blueprint.route("/report")
def logistics_reports():
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    
    return render_template("logistics_reports.html")

@logistic_blueprint.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("logistic.login"))