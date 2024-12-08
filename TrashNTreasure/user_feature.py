from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
import sqlite3

user_blueprint = Blueprint("user", __name__, template_folder="templates")

@user_blueprint.route("/")
def user_page():
    if "user_name" in session:
        return render_template("user_page.html", user = session["user_name"])    
    else:
        flash("Please log in to access the user account.", "danger")
        return redirect(url_for("login"))

@user_blueprint.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
