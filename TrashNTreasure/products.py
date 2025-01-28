from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
from db import get_connect_db
from werkzeug.utils import secure_filename
import os, sqlite3

product_blueprint = Blueprint("product", __name__, template_folder="templates")

UPLOAD_FOLDER = 'TrashNTreasure/static/products/'
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "avi", "mov", "wmv"}

# Create the folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@product_blueprint.route('/add_product', methods=["GET", "POST"])
def add_product():
    seller_id = session.get("buyer_id")
    admin_id = session.get("admin_name")
    
    if not seller_id and not admin_id:
        flash("You must be logged in as a seller or admin to add a product.", "danger")
        if not seller_id:
            return redirect(url_for("login"))
        else:
            return redirect(url_for("admin.login"))
    
    if request.method == "POST":
        try:
            # Get form data
            product_name = request.form["product_name"]
            category = request.form["category"]
            description = request.form["description"]
            price = float(request.form["price"])
            quantity = int(request.form["quantity"])
            condition = request.form["condition"]

            # Initialize file paths
            image_path = None
            video_path = None
            
            file_not_allowed = False
            # Handle image upload
            if "image" in request.files:
                image = request.files["image"]
                if image and image.filename != "":
                    if allowed_file(image.filename):
                        filename = secure_filename(image.filename)
                        image_path = os.path.join(UPLOAD_FOLDER, "images", filename)
                        os.makedirs(os.path.dirname(image_path), exist_ok=True)
                        image.save(image_path)
                        image_path = f'/static/products/images/{filename}' # Ensure web-compatible path
                    else:
                        flash("Invalid image file type. Please upload a PNG, JPG, JPEG, or GIF.", "danger")
                        file_not_allowed = True

            # Handle video upload
            if "video" in request.files:
                video = request.files["video"]
                if video and video.filename != "":
                    if allowed_file(video.filename):
                        filename = secure_filename(video.filename)
                        video_path = os.path.join(UPLOAD_FOLDER, "videos", filename)
                        os.makedirs(os.path.dirname(video_path), exist_ok=True)
                        video.save(video_path)
                        video_path = f'/static/products/videos/{filename}'  # Ensure web-compatible path
                    else:
                        flash("Invalid video file type. Please upload an MP4, AVI, MOV, or WMV.", "danger")
                        file_not_allowed = True
                        
            if file_not_allowed:
                return redirect(url_for("product.add_product"))

            # Insert data into the database
            con = get_connect_db()
            cur = con.cursor()
            if seller_id:
                cur.execute(
                    """INSERT INTO products 
                    (name, category, description, price, quantity, condition, seller_id, image_path, video_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (product_name, category, description, price, quantity, condition, seller_id, image_path, video_path),
                )
            elif admin_id:
                cur.execute(
                    """INSERT INTO products 
                    (name, category, description, price, quantity, condition, seller_id, image_path, video_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (product_name, category, description, price, quantity, condition, session["admin_id"], image_path, video_path),
                )
            con.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("product.add_product"))
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
    if seller_id:
        return render_template("seller_verification.html", seller_id=seller_id)
    elif admin_id:
        return render_template("inventory.html", admin_id=admin_id)
    
@product_blueprint.route("/remove_item/<id>", methods=["POST", "GET"])
def delete_item(id):
    try:
        con = get_connect_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM product WHERE id = ?", (id,))
        user = cur.fetchone()
        if not user:
            flash("Product not found.", "warning")
            return redirect(url_for("admin.inventory"))
        cur.execute("DELETE FROM product WHERE id = ?", (id,))
        con.commit()
        
        flash("Product deleted successfully!", "success")
        
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        
    finally:
        if con:
            con.close()
            
    return redirect(url_for("admin.inventory"))

@product_blueprint.route('/search', methods=["GET"])
def search_product():
    query = request.args.get("query", "").strip()  # Get the search query from the URL
    
    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for("product_page"))
    
    try:
        con = get_connect_db()
        cur = con.cursor()

        # Search for products matching the query in name or category
        cur.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? OR category LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        
        products = cur.fetchall()

        if not products:
            flash("No products found matching your search.", "info")
        
        return render_template("product.html", products=products, search_query=query)
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if con:
            con.close()

    return redirect(url_for("product_page"))

@product_blueprint.route("/filter", methods=["GET"])
def filter_product():
    category = request.args.get("category", "all")  # Get the selected category, default to 'all'
    try:
        con = get_connect_db()
        cur = con.cursor()
        if category == "all":
            cur.execute("SELECT * FROM products")
        else:
            cur.execute("SELECT * FROM products WHERE category = ?", (category,))
        products = cur.fetchall()
        if not products:
            flash("No products found in this category.", "info")
        return render_template("product.html", products=products, selected_category=category)
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if con:
            con.close()
    return redirect(url_for("product_page"))

@product_blueprint.route("/item_details/<id>", methods=["POST", "GET"])
def item_detail(id):
    con = get_connect_db()
    cur = con.cursor()
    product = cur.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    
    return render_template("product_details.html", product=product)


# Assuming this is part of your Flask app
@product_blueprint.route("/add-to-cart/<id>", methods=["POST"])
def add_to_cart(id):
    # Ensure the user is logged in
    user_id = session.get("buyer_id")
    if not user_id:
        flash("You must be logged in to add items to the cart.", "danger")
        return redirect(url_for("login"))  # Redirect to login page if not logged in

    # Get the product details from the database
    con = get_connect_db()
    cur = con.cursor()
    product = cur.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("product_page"))  # Redirect to product list if product doesn't exist

    # Get the quantity from the form (assuming it's submitted via POST)
    quantity = request.form.get("quantity", default=1, type=int)  # Default to 1 if quantity is not provided

    try:
        cur.execute(
            "INSERT INTO cart (buyer_id, product_id, product_name, quantity, max_quantity, price, product_image_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, id, product["name"], quantity, product["quantity"], product["price"], product["image_path"]),
        )
        con.commit()  # Commit the transaction
        flash("Product added to cart successfully!", "success")
    except sqlite3.Error as e:
        con.rollback()  # Rollback in case of error
        flash(f"An error occurred: {e}", "danger")
    finally:
        con.close()  # Close the database connection

    # Redirect to the product list or cart page
    return redirect(url_for("product_page"))  # Adjust the redirect as needed



    
    