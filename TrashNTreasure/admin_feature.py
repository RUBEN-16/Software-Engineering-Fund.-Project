from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from user_feature import get_connect_db_user_
from logistic_feature import get_connect_db_logistic
from seller_feature import get_connect_db_seller_registration

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

@admin_blueprint.route('/seller_requests', methods=["GET", "POST"])
def seller_requests():
    con = get_connect_db_seller_registration()
    if request.method == "POST":
        action = request.form.get("action")
        seller_id = request.form.get("id")
        if action and seller_id:
            if action == "approve":
                con.execute("UPDATE seller_registration SET status = 'Approved' WHERE id = ?", (seller_id,))
                flash("Seller approved successfully!", "success")
            elif action == "reject":
                con.execute("UPDATE seller_registration SET status = 'Rejected' WHERE id = ?", (seller_id,))
                flash("Seller rejected successfully!", "danger")
            con.commit()
        else:
            flash("Invalid action or seller ID.", "danger")
    
    # Fetch all pending seller registrations
    cur = con.execute("SELECT * FROM seller_registration WHERE status = 'Pending'")
    pending_requests = cur.fetchall()
    con.close()
    return render_template('seller_approval_page.html', pending_requests=pending_requests)


# @admin_blueprint.route('/seller_request')
# def seller_request():
#     if "admin_name" not in session:  # Check if admin is logged in
#         flash("Please log in to access this page.", "danger")
#         return redirect(url_for("admin.login"))
    
#     con = get_connect_db_seller
#     cur = con.cursor()
#     cur.execute('SELECT id, buyer_id, ic_picture, profile_picture FROM seller_registration')
#     sellers = cur.fetchall()
#     con.close()
    
#     sellers = [{"id": seller[0], "first_name": seller[1], "last_name": seller[2], "email": seller[3]} for seller in sellers]
#     return render_template(
#         'seller_request.html',
#         sellers = sellers,
#         isBack = True,
#         back_url = url_for('admin.dashboard')
#     )
    
    
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


    

@admin_blueprint.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))