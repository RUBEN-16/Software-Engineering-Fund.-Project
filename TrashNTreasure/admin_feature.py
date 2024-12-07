from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from user_feature import get_connect_db_user_
from logistic_feature import get_connect_db_logistic
from seller_feature import get_connect_db

admin_blueprint = Blueprint("admin", __name__, template_folder="templates")


@admin_blueprint.route("/login", methods=["POST", "GET"])
def login():
    admins = [
        {"Username": "ruben123", "Password" : "passRuben", "Name" : "Rubeneswaran"},
        {"Username": "thris987", "Password" : "passThris", "Name" : "Thrissha"},
        {"Username": "nasss123", "Password" : "passNasss", "Name" : "Nasreen"}
    ]
    if request.method == "POST":
        action = request.form.get("action")
        if action == "Login":
            username = request.form["username"]
            password = request.form["password"]
            
            for admin in admins:
                if admin["Username"] == username and admin["Password"] == password:
                    session["admin_name"] = admin["Name"] 
                    return redirect(url_for("admin.dashboard"))
                
            flash("Invalid username and password", "danger")
            return render_template("adminlogin_page.html")
        elif action == "Back":
            return redirect(url_for("home"))

    return render_template("adminlogin_page.html")

@admin_blueprint.route("/")
def dashboard():
    if "admin_name" in session:
        return render_template("admin_page.html", admin = session["admin_name"])    
    else:
        flash("Please log in to access the admin account.", "danger")
        return redirect(url_for("admin.login"))

@admin_blueprint.route("/addLogistic", methods=["POST", "GET"])
def adding_logistic():
    if "admin_name" not in session:  # Check if admin is logged in
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("admin.login"))
    
    con = None 
    if request.method == "POST":
        try:
            action = request.form.get("action")
            if action == "Hire":
                fname = request.form["first_name"]
                lname = request.form["last_name"]
                email = request.form["email"]
                password = request.form["password"]
                
                
                
                con = get_connect_db_logistic() # Initialize the connection here
                cur = con.cursor()
                cur.execute("SELECT * FROM member WHERE email = ?", (email,))
                member = cur.fetchone()
                
                if member:  # If a record is found
                    flash("Email already exists!", "danger")
                    return redirect(url_for("admin.adding_logistic"))
                cur.execute("INSERT INTO member (firstName, lastName, email, password) VALUES (?, ?, ?, ?)",(fname, lname, email, password),)
                con.commit()
                flash("Account Created Successfully!", "success")
                return redirect(url_for("admin.adding_logistic"))
            elif action == "Back":
                return redirect(url_for("admin.dashboard"))
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            if con:  # Check if con is initialized
                con.close()
    return render_template("mem_hiring.html")

    
@admin_blueprint.route('/manage_users')
def manage_users():
    if "admin_name" not in session:  # Check if admin is logged in
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("admin.login"))
    
    con = get_connect_db_user_()
    cur = con.cursor()
    cur.execute("SELECT pid, firstName, lastName, email FROM user")
    users = cur.fetchall()
    con.close()

    # Convert users to dictionaries
    users = [{"id": user[0], "first_name": user[1], "last_name": user[2], "email": user[3]} for user in users]
    return render_template(
        'user_management.html', 
        users=users,
        show_back_button = True,  # Enable Back button
        back_url=url_for('admin.dashboard')  # Specify where Back button points
    )
 

@admin_blueprint.route("/remove_user/<id>", methods=["POST", "GET"])
def delete_user(id):
    try:
        con = get_connect_db_user_()
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE pid = ?", (id,))
        user = cur.fetchone()
        if not user:
            flash("User not found.", "warning")
            return redirect(url_for("admin.manage_users"))
        cur.execute("DELETE FROM user WHERE pid = ?", (id,))
        con.commit()
        
        flash("User deleted successfully!", "success")
        
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        
    finally:
        if con:
            con.close()
            
    return redirect(url_for("admin.manage_users"))

@admin_blueprint.route("/seller_approval")
def seller_approval():
    if "admin_name" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("admin.login"))

    con = get_connect_db()
    cur = con.cursor()
    cur.execute("""
        SELECT sr.id, u.firstName, u.lastName, u.email 
        FROM seller_registration sr 
        JOIN user u ON sr.id = u.pid 
        WHERE sr.status = 'Pending'
    """)
    pending_sellers = cur.fetchall()
    con.close()

    return render_template("seller_approval.html", pending_sellers=pending_sellers)

@admin_blueprint.route("/view_seller/<int:seller_id>", methods=["POST"])
def view_seller(seller_id):
    if "admin_name" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("admin.login"))

    con = get_connect_db()
    cur = con.cursor()
    cur.execute("""
        SELECT sr.*, u.firstName, u.lastName, u.email 
        FROM seller_registration sr 
        JOIN user u ON sr.id = u.pid 
        WHERE sr.id = ?
    """, (seller_id,))
    seller_details = cur.fetchone()
    con.close()

    if not seller_details:
        flash("Seller not found.", "danger")
        return redirect(url_for("admin.seller_approval"))

    return render_template("seller_details.html", seller_details=seller_details)

@admin_blueprint.route("/approve_seller/<int:seller_id>", methods=["POST"])
def approve_seller(seller_id):
    try:
        con = get_connect_db()
        cur = con.cursor()
        cur.execute("UPDATE seller_registration SET status = 'Approved' WHERE id = ?", (seller_id,))
        con.commit()
        flash("Seller application approved!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        con.close()

    return redirect(url_for("admin.seller_approval"))

@admin_blueprint.route("/reject_seller/<int:seller_id>", methods=["POST"])
def reject_seller(seller_id):
    try:
        con = get_connect_db()
        cur = con.cursor()
        cur.execute("UPDATE seller_registration SET status = 'Rejected' WHERE id = ?", (seller_id,))
        con.commit()
        flash("Seller application rejected.", "info")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        con.close()

    return redirect(url_for("admin.seller_approval"))

@admin_blueprint.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))