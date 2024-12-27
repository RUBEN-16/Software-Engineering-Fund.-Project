from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
from db import get_connect_db
from werkzeug.utils import secure_filename
import os

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

            # Handle image upload
            if "image" in request.files:
                image = request.files["image"]
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(UPLOAD_FOLDER, "images", filename)
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    image.save(image_path)
                    image_path = image_path.replace("\\", "/")  # Ensure web-compatible path

            # Handle video upload
            if "video" in request.files:
                video = request.files["video"]
                if video and allowed_file(video.filename):
                    filename = secure_filename(video.filename)
                    video_path = os.path.join(UPLOAD_FOLDER, "videos", filename)
                    os.makedirs(os.path.dirname(video_path), exist_ok=True)
                    video.save(video_path)
                    video_path = video_path.replace("\\", "/")  # Ensure web-compatible path

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
        return render_template("add_product.html", seller_id=seller_id)
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


        
