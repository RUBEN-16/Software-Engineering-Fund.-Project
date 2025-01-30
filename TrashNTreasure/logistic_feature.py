from flask import Blueprint, redirect, url_for, render_template, request, session, flash, current_app
from db import get_connect_db

logistic_blueprint = Blueprint("logistic", __name__, template_folder="templates")

@logistic_blueprint.route("/logisticlogin", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        con = get_connect_db()
        cur=con.cursor()
        cur.execute("SELECT * FROM member WHERE email = ? and password = ?", (email, password)) #checking 
        data = cur.fetchone() 
        con.close()

        if data:
            session["member_name"] = data["firstName"]  
            session["member_id"] = data["pid"]  
            return redirect(url_for("logistic.dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return render_template("logisticlogin_page.html")
        
    return render_template("logisticlogin_page.html")


@logistic_blueprint.route("/")
def dashboard():    
    if "member_id" in session:
        return render_template("logistic_page.html")
    else:
        flash("Please log in to access the admin account.", "danger")
        return redirect(url_for("logistic.login"))
    
@logistic_blueprint.route("/pickup_manage")
def pickup_management():
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    con = get_connect_db()
    cur = con.cursor()
    
    pickup_requests = cur.execute("""
        SELECT 
            pr.id,
            pr.order_id,
            pr.courier,
            pr.seller_address,
            pr.buyer_address,
            pr.assigned_status,
            o.delivery_status
        FROM pickup_request2 pr
        JOIN orders o ON pr.order_id = o.id
        JOIN products p ON o.product_id = p.id
        WHERE p.seller_id = ?
    """, (session["member_id"],)).fetchall()

    return render_template("pickup_management.html", pickup_requests=pickup_requests)

@logistic_blueprint.route("/delivery_manage")
def delivery_management():
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    con = get_connect_db()
    cur = con.cursor()
    
    shipped_orders = cur.execute("""
           SELECT 
                o.id as order_id,
                o.product_id,
                p.name as product_name,
                o.delivery_status,
                ad.condition AS assign_delivery_condition
            FROM orders o
            JOIN products p ON o.product_id = p.id
            LEFT JOIN assign_delivery ad ON o.id = ad.order_id
            WHERE o.delivery_status = 'Shipped'
        """).fetchall()
    
    return render_template("delivery_management.html", shipped_orders=shipped_orders)

@logistic_blueprint.route("/order_manage")
def order_management():
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    
    con = get_connect_db()
    cur = con.cursor()

    all_orders = cur.execute("""
        SELECT 
            o.id,
            o.product_id,
            o.buyer_id,
            o.delivery_status
        FROM orders o
    """).fetchall()

    return render_template("order_management.html", all_orders=all_orders)

@logistic_blueprint.route("/report")
def logistics_reports():
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    
    return render_template("logistics_reports.html")

@logistic_blueprint.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("logistic.login"))

@logistic_blueprint.route("/pickup_details/<int:pickup_id>", methods=['GET', 'POST'])
def pickup_details(pickup_id):
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))

    con = get_connect_db()
    cur = con.cursor()
    
    pickup_details = cur.execute("SELECT * FROM pickup_request2 WHERE id = ?", (pickup_id,)).fetchone()
    if not pickup_details:
        flash("Pickup request not found.", "danger")
        return redirect(url_for("logistic.pickup_management"))
    
    order_details = cur.execute("SELECT * FROM orders WHERE id = ?", (pickup_details['order_id'],)).fetchone()
    if not order_details:
        flash("Order details not found for this pickup request.", "danger")
        return redirect(url_for("logistic.pickup_management"))
    
    # Fetch delivery status
    delivery_status = cur.execute("SELECT delivery_status FROM orders WHERE id = ?", (pickup_details['order_id'],)).fetchone()

    if delivery_status:
      pickup_details = dict(pickup_details)
      pickup_details['delivery_status'] = delivery_status['delivery_status']

    seller_details = cur.execute("""
        SELECT s.*
        FROM sellers s
        JOIN products p ON s.id = p.seller_id
        JOIN orders o ON p.id = o.product_id
        WHERE o.id = ?
    """, (pickup_details['order_id'],)).fetchone()
    if not seller_details:
        flash("Seller details not found for this pickup request.", "danger")
        return redirect(url_for("logistic.pickup_management"))
    
    buyer_details = cur.execute("SELECT * FROM user WHERE pid = ?", (order_details['buyer_id'],)).fetchone()
    if not buyer_details:
        flash("Buyer details not found for this pickup request.", "danger")
        return redirect(url_for("logistic.pickup_management"))

    return render_template(
        "pickup_details.html",
        pickup_details=pickup_details,
        order_details=order_details,
        seller_details=seller_details,
        buyer_details=buyer_details
    )

@logistic_blueprint.route("/assign_courier/<int:pickup_id>", methods=['POST'])
def assign_courier(pickup_id):
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))

    if request.method == 'POST':
        courier = request.form['courier']
        con = get_connect_db()
        cur = con.cursor()
        cur.execute("UPDATE pickup_request2 SET courier = ?, assigned_status = 'Assigned' WHERE id = ?", (courier, pickup_id))
        con.commit()
        con.close()
        flash("Courier assigned successfully.", "success")
        return redirect(url_for('logistic.pickup_management'))
    
    flash("Invalid request method", 'danger')
    return redirect(url_for('logistic.pickup_management'))



@logistic_blueprint.route("/delivery_details/<int:order_id>", methods=['GET', 'POST'])
def delivery_details(order_id):
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))

    con = get_connect_db()
    cur = con.cursor()

    # Fetch order details
    order_details = cur.execute("""
        SELECT 
            o.id as order_id,
            o.product_id,
            p.name as product_name,
            o.quantity,
            o.total_amount,
            o.buyer_id
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.id = ?
    """, (order_id,)).fetchone()

    if not order_details:
        flash("Order not found.", "danger")
        return redirect(url_for("logistic.delivery_management"))

     # Fetch buyer details
    buyer_details = cur.execute("SELECT * FROM user WHERE pid = ?", (order_details['buyer_id'],)).fetchone()
    if not buyer_details:
        flash("Buyer details not found for this order.", "danger")
        return redirect(url_for("logistic.delivery_management"))

    # Fetch seller details
    seller_details = cur.execute("""
        SELECT s.*
        FROM sellers s
        JOIN products p ON s.id = p.seller_id
        JOIN orders o ON p.id = o.product_id
        WHERE o.id = ?
    """, (order_id,)).fetchone()
    if not seller_details:
        flash("Seller details not found for this order.", "danger")
        return redirect(url_for("logistic.delivery_management"))
    
    # Fetch assign delivery info if exists
    assign_delivery_info = cur.execute("SELECT * FROM assign_delivery WHERE order_id = ?", (order_id,)).fetchone()


    con.close()

    return render_template(
        "delivery_details.html",
        order_details=order_details,
        buyer_details=buyer_details,
        seller_details=seller_details,
        assign_delivery_info = assign_delivery_info
    )


@logistic_blueprint.route("/assign_delivery/<int:order_id>", methods=['POST'])
def assign_delivery(order_id):
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))

    if request.method == 'POST':
        pickup_date = request.form['pickup_date']
        arrival_date = request.form['arrival_date']
        condition = request.form['condition']
        description = request.form['description']
        courier = request.form['courier']
        
        con = get_connect_db()
        cur = con.cursor()

        # Fetch seller id from order table
        order_details = cur.execute("SELECT product_id FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not order_details:
            flash("Order not found to get the seller ID.", "danger")
            con.close()
            return redirect(url_for("logistic.delivery_details", order_id=order_id))
        
        product_details = cur.execute("SELECT seller_id FROM products WHERE id = ?", (order_details['product_id'],)).fetchone()
         
        if not product_details:
            flash("Product not found to get the seller ID.", "danger")
            con.close()
            return redirect(url_for("logistic.delivery_details", order_id=order_id))
        seller_id = product_details['seller_id']


        try:
            cur.execute("""
                INSERT INTO assign_delivery (order_id, seller_id, condition, courier, arrival_date, pickup_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (order_id, seller_id, condition, courier, arrival_date, pickup_date, description))
            con.commit()
            flash("Delivery assigned successfully.", "success")
        except Exception as e:
            flash(f"Error assigning delivery: {e}", "danger")
        finally:
           con.close()

    return redirect(url_for("logistic.delivery_details", order_id=order_id))

@logistic_blueprint.route("/update_delivery_status/<int:order_id>", methods=['POST'])
def update_delivery_status(order_id):
    if "member_id" not in session:
         flash("Please log in to access this page.", "danger")
         return redirect(url_for("logistic.login"))
    
    con = get_connect_db()
    cur = con.cursor()
    
    try:
        cur.execute("UPDATE orders SET delivery_status = 'Delivered' WHERE id = ?", (order_id,))
        
         # Fetch the assign_delivery record id
        assign_delivery_data = cur.execute("SELECT id FROM assign_delivery WHERE order_id = ?", (order_id,)).fetchone()
        if assign_delivery_data:
             assign_delivery_id = assign_delivery_data['id']
             cur.execute("UPDATE assign_delivery SET delivered_date = DATE('now') WHERE id = ?", (assign_delivery_id,))

        con.commit()
        flash("Delivery status updated to 'Delivered'.", "success")
    except Exception as e:
        flash(f"Error updating delivery status: {e}", "danger")
    finally:
        con.close()
    
    return redirect(url_for("logistic.delivery_details", order_id=order_id))


@logistic_blueprint.route("/update_pickup_status/<int:pickup_id>", methods=['POST'])
def update_pickup_status(pickup_id):
    if "member_id" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("logistic.login"))
    
    con = get_connect_db()
    cur = con.cursor()

    try:
        # Fetch order ID from pickup_request2 table
        pickup_details = cur.execute("SELECT order_id FROM pickup_request2 WHERE id = ?", (pickup_id,)).fetchone()
        if not pickup_details:
            flash("Pickup request not found.", "danger")
            con.close()
            return redirect(url_for("logistic.pickup_details", pickup_id=pickup_id))
        order_id = pickup_details['order_id']

        # Update delivery status in orders table
        cur.execute("UPDATE orders SET delivery_status = 'Shipped' WHERE id = ?", (order_id,))
        con.commit()
        flash("Delivery status updated to 'Shipped'.", "success")

    except Exception as e:
        flash(f"Error updating delivery status: {e}", "danger")
    finally:
        con.close()
    
    return redirect(url_for("logistic.pickup_details", pickup_id=pickup_id))