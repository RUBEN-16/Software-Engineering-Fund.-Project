from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from db import get_connect_db, send_notification, seller_database

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
                    session["admin_id"] = admin["Username"] 
                    session["admin_name"] = admin["Name"] 
                    return redirect(url_for("admin.dashboard"))
                
            flash("Invalid username and password", "danger")
            return render_template("adminlogin_page.html")
        elif action == "Back":
            return redirect(url_for("home"))

    return render_template("adminlogin_page.html")

@admin_blueprint.route("/")
def dashboard(): 
    if "admin_id" in session:
        return render_template("admin_page.html", admin = session["admin_name"])    
    else:
        flash("Please log in to access the admin account.", "danger")
        return redirect(url_for("admin.login"))

@admin_blueprint.route("/addLogistic", methods=["POST", "GET"])
def adding_logistic():
    if "admin_id" not in session:  # Check if admin is logged in
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
                
                con = get_connect_db() # Initialize the connection here
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
    return render_template("logistic_management.html")

@admin_blueprint.route("/logistic_management")
def logistic_management():
    if "admin_id" not in session:  # Check if admin is logged in
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("admin.login"))
    
    con = get_connect_db()
    cur = con.cursor()
    cur.execute("SELECT pid, firstName, lastName, email FROM member")
    members = cur.fetchall()
    con.close()
    members = [{"id": member[0], "first_name": member[1], "last_name": member[2], "email": member[3]} for member in members]

    return render_template("logistic_management.html", members=members,)

@admin_blueprint.route("/inventory") 
def inventory():
    if "admin_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("admin.login"))
    
    con = get_connect_db()
    cur = con.cursor()
    cur.execute("SELECT name, quantity, condition, price, id FROM products")
    products = cur.fetchall()
    con.close()

    # Convert products to dictionaries
    products = [{"name": product[0], "quantity": product[1], "condition": product[2], "price": product[3], "id": product[4]} for product in products]
    return render_template('inventory.html', products=products,)
    
    
@admin_blueprint.route('/product_management')
def user_management():
    if "admin_id" not in session:  # Check if admin is logged in
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("admin.login"))
    
    con = get_connect_db()
    cur = con.cursor()
    users = cur.execute("SELECT pid, firstName, lastName, email FROM user").fetchall()
    sellers = cur.execute("SELECT id, name, email FROM sellers").fetchall()
    con.close()

    # Convert users to dictionaries
    users = [{"id": user[0], "first_name": user[1], "last_name": user[2], "email": user[3]} for user in users]
    sellers = [{"id": seller[0], "name": seller[1], "email": seller[2]} for seller in sellers]
    return render_template(
        'user_management.html', 
        users=users,
        sellers=sellers
    )
 
@admin_blueprint.route("/view_user/<id>", methods=["POST", "GET"])
def view_user(id):
    try:
        con = get_connect_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE pid = ?", (id,))
        user = cur.fetchone()
        if not user:
            flash("User not found.", "warning")
            return redirect(url_for("admin.user_management"))
        con.commit()        
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        if con:
            con.close()
            
    return render_template("user_view.html", user=user)

@admin_blueprint.route("/remove_user/<id>", methods=["POST", "GET"])
def delete_user(id):
    try:
        con = get_connect_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE pid = ?", (id,))
        user = cur.fetchone()
        if not user:
            flash("User not found.", "warning")
            return redirect(url_for("admin.user_management"))
        cur.execute("DELETE FROM user WHERE pid = ?", (id,))
        con.commit()
        
        flash("User deleted successfully!", "success")
        
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        
    finally:
        if con:
            con.close()
            
    return redirect(url_for("admin.user_management"))

@admin_blueprint.route("/seller_approval")
def seller_approval():
    if "admin_id" not in session:
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
    if "admin_id" not in session:
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
        
        cur.execute("UPDATE user SET isSeller = 1 WHERE pid = ?", (seller_id,))
        con.commit()
        
        seller_database(seller_id)
        con.commit()
        
        flash("Seller application approved!", "success")
        send_notification(con, seller_id, "Seller Application Approved", "Congratulations! Your seller application has been approved. You can now start listing your products.")
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
        send_notification(con, seller_id, "Seller Application Rejected", "Your seller application has been rejected. You can review the requirements and apply again.")
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

