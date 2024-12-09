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
    if not seller_id:
        flash("You must be logged in to add a product", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        try:
            # Get form data
            product_name = request.form["product_name"]
            category = request.form["category"]
            description = request.form["description"]
            price = float(request.form["price"])
            quantity = int(request.form["quantity"])
            condition = request.form["condition"]
            seller_id = int(request.form["seller_id"])

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
            cur.execute(
                """INSERT INTO products 
                (name, category, description, price, quantity, condition, seller_id, image_path, video_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (product_name, category, description, price, quantity, condition, seller_id, image_path, video_path),
            )
            con.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("product.add_product"))
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            if con:
                con.close()

    return render_template("add_product.html", seller_id=seller_id)


        
