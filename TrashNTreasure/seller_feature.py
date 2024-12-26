from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
from db import get_connect_db
import os

seller_blueprint = Blueprint("seller", __name__, template_folder="templates")
UPLOAD_FOLDER = 'TrashNTreasure/static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@seller_blueprint.route('/seller_verification', methods=["POST", "GET"])
def seller_verification():
    if "user_name" not in session: 
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))
    
    buyer_id = session.get('buyer_id')
    if not buyer_id:
        flash("You need to log in to proceed.", "danger")
        return redirect(url_for('login'))

    con = get_connect_db()
    cur = con.cursor() 
    user_exist = cur.execute('SELECT * FROM seller_registration WHERE id = ?', (buyer_id,)).fetchone()
    con.close()
    
    if user_exist:
        session['isExist'] = True
        print("isExist")
    else:
        session['isExist'] = False
        print("notExist")
    
    if request.method == "POST":
        if session['isExist']:
            return render_template("seller_registration.html")
        
        if 'ic_picture' not in request.files or 'profile_picture' not in request.files:
            flash("Both IC and profile pictures are required.", "danger")
            return redirect(url_for('seller.seller_verification'))

        ic_picture = request.files['ic_picture']
        profile_picture = request.files['profile_picture']

        if ic_picture.filename == '' or profile_picture.filename == '':
            flash("Both IC and profile pictures must have valid filenames.", "danger")
            return redirect(url_for('seller.seller_verification'))
        
        # Create a folder for the seller based on their buyer_id
        seller_folder = os.path.join(UPLOAD_FOLDER, f'seller_{buyer_id}')
        os.makedirs(seller_folder, exist_ok=True)
        
        ic_filename = os.path.join(seller_folder, ic_picture.filename)
        profile_filename = os.path.join(seller_folder, profile_picture.filename)
        ic_filename_db = f'/static/uploads/seller_{buyer_id}/{ic_picture.filename}'
        profile_filename_db = f'/static/uploads/seller_{buyer_id}/{profile_picture.filename}'
            
        try:
            ic_picture.save(ic_filename)
            profile_picture.save(profile_filename)
        except Exception as e:
            flash(f"Error saving files: {e}", "danger")
            return redirect(url_for('seller.seller_verification'))
            
        if os.path.exists(ic_filename) and os.path.exists(profile_filename):
            con = get_connect_db()
            con.execute("""
                INSERT INTO seller_registration (id, ic_picture, profile_picture)
                VALUES (?, ?, ?)
            """, (buyer_id, ic_filename_db, profile_filename_db))
            con.commit()
            con.close()
                        
            flash("Seller verification submitted successfully!", "success")
            return redirect(url_for('seller.seller_verification'))
        else:
            flash("File paths are invalid. Please try again.", "danger")
            return redirect(url_for('seller.seller_verification'))
    
    return render_template('seller_verification.html', user_id=buyer_id)

        
