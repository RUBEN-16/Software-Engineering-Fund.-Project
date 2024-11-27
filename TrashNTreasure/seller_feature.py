from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
import sqlite3
import os

seller_blueprint = Blueprint("seller", __name__, template_folder="templates")

UPLOAD_FOLDER = 'TrashNTreasure/static/uploads/'
DATABASE_PATH = 'TrashNTreasure/database.db'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

con=sqlite3.connect(DATABASE_PATH)
con.execute("""
    CREATE TABLE IF NOT EXISTS seller_registration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        ic_picture TEXT NOT NULL,
        profile_picture TEXT NOT NULL,
        FOREIGN KEY (buyer_id) REFERENCES user(pid)
    )
""")
con.close()

def get_connect_db_seller_registration():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn 

@seller_blueprint.route('/seller_verification', methods=["POST", "GET"])
def seller_verification():
    if "user_name" not in session: 
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))
    
    buyer_id = session.get('buyer_id')
    if not buyer_id:
        flash("You need to log in to proceed.", "danger")
        return redirect(url_for('login'))

    con = get_connect_db_seller_registration()
    cur = con.cursor()
    user_exist = cur.execute('SELECT * FROM seller_registration WHERE buyer_id = ?', (buyer_id,)).fetchone()
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
        
        ic_filename = os.path.join(UPLOAD_FOLDER, ic_picture.filename)
        profile_filename = os.path.join(UPLOAD_FOLDER, profile_picture.filename)
            
        try:
            ic_picture.save(ic_filename)
            profile_picture.save(profile_filename)
        except Exception as e:
            flash(f"Error saving files: {e}", "danger")
            return redirect(url_for('seller.seller_verification'))
            
        if os.path.exists(ic_filename) and os.path.exists(profile_filename):
            con = get_connect_db_seller_registration()
            con.execute("""
                INSERT INTO seller_registration (buyer_id, ic_picture, profile_picture)
                VALUES (?, ?, ?)
            """, (buyer_id, ic_filename, profile_filename))
            con.commit()
            con.close()
                        
            flash("Seller verification submitted successfully!", "success")
            return redirect(url_for('seller.seller_verification'))
        else:
            flash("File paths are invalid. Please try again.", "danger")
            return redirect(url_for('seller.seller_verification'))
    
    return render_template('seller_verification.html')

        