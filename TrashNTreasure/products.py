from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
from db import get_connect_db

product_blueprint = Blueprint("product", __name__, template_folder="templates")


@product_blueprint.route('/add_product')
def add_product():
    seller_id = session.get("buyer_id")
    if not seller_id:
        flash("You must be logged in to add a product", "danger")
        return redirect(url_for("login"))
    
    return render_template("add_product.html", seller_id=seller_id)

        
