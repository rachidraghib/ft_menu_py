import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_restaurant_key'
##############################################
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

##############################################
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

##############################################
def get_db_connection():
    conn = sqlite3.connect('restaurant.db')
    conn.row_factory = sqlite3.Row
    return conn

##############################################
# --- PUBLIC / MENU ROUTES ---
@app.route('/')
def index():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    menu_by_category = {}
    for cat in categories:
        items = conn.execute('SELECT * FROM menu_items WHERE category_id = ?', (cat['id'],)).fetchall()
        if items: menu_by_category[cat['name']] = items
    conn.close()
    return render_template('menu.html', menu=menu_by_category, nav_categories=categories)

# --- CUSTOMER AUTHENTICATION ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('customer_login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid login credentials.', 'danger')
    return render_template('customer_login.html')

@app.route('/customer/logout')
def customer_logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))
##############################################

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return jsonify({'status': 'unauthorized', 'message': 'Please login to process payments.'}), 401
    
    data = request.get_json()
    cart_items = data.get('cart', [])
    
    if not cart_items:
        return jsonify({'status': 'error', 'message': 'Your shopping cart is empty.'}), 400
        
    # Calculate balance totals securely on the backend server to prevent client-side tampering
    conn = get_db_connection()
    subtotal = 0
    for item in cart_items:
        db_item = conn.execute('SELECT price FROM menu_items WHERE id = ?', (item['id'],)).fetchone()
        if db_item:
            subtotal += db_item['price'] * int(item['quantity'])
            
    tax = subtotal * 0.0825
    grand_total = round(subtotal + tax, 2)
    conn.close()

    # Pass checkout values into the payment gateway page wrapper
    return jsonify({
        'status': 'redirect', 
        'grand_total': grand_total,
        'cart_data': cart_items
    })

##############################################
@app.route('/process-payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        flash('Session expired.', 'danger')
        return redirect(url_for('index'))
        
    card_name = request.form.get('card_name')
    card_number = request.form.get('card_number')
    cart_json = request.form.get('cart_json')
    fulfillment_type = request.form.get('fulfillment_type')
    fulfillment_details = request.form.get('fulfillment_details')
    
    if not card_name or len(card_number.replace(" ", "")) < 16:
        flash('Payment Denied: Invalid Card Credentials.', 'danger')
        return redirect(url_for('index'))
        
    import json
    try:
        cart_items = json.loads(cart_json)
    except:
        flash('Error processing cart payload.', 'danger')
        return redirect(url_for('index'))

    conn = get_db_connection()
    try:
        subtotal = 0
        for item in cart_items:
            db_item = conn.execute('SELECT price FROM menu_items WHERE id = ?', (item['id'],)).fetchone()
            if db_item: subtotal += db_item['price'] * int(item['quantity'])
        grand_total = round(subtotal + (subtotal * 0.0825), 2)

        cursor = conn.cursor()
        # Injected fulfillment parameters directly inside write command string queries
        cursor.execute('''
            INSERT INTO orders (user_id, total_price, fulfillment_type, fulfillment_details) 
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], grand_total, fulfillment_type, fulfillment_details))
        order_id = cursor.lastrowid

        for item in cart_items:
            db_item = conn.execute('SELECT price FROM menu_items WHERE id = ?', (item['id'],)).fetchone()
            cursor.execute('''
                INSERT INTO order_items (order_id, menu_item_id, quantity, price_at_purchase)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item['id'], item['quantity'], db_item['price']))
            
        conn.commit()
        flash(f'💳 Order #{order_id} [{fulfillment_type}] setup confirmed!', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error processing order database transaction records.', 'danger')
    finally:
        conn.close()

    return redirect(url_for('customer_profile'))
##############################################
# --- ADMIN ROUTES (Exposed for Order Monitoring) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'): return redirect(url_for('login'))
    conn = get_db_connection()
    items = conn.execute('SELECT menu_items.*, categories.name AS category_name FROM menu_items JOIN categories ON menu_items.category_id = categories.id').fetchall()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    # Pull incoming customer orders to present inside the panel dashboard view
    orders = conn.execute('SELECT orders.*, users.name FROM orders JOIN users ON orders.user_id = users.id ORDER BY orders.id DESC').fetchall()
    conn.close()
    return render_template('admin.html', items=items, categories=categories, orders=orders)

@app.route('/admin/add', methods=['POST'])
def add_item():
    if not session.get('logged_in'): return redirect(url_for('login'))
    title, description, price, category_id = request.form['title'], request.form['description'], request.form['price'], request.form['category_id']
    filename = 'default_meal.jpg'
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    conn = get_db_connection()
    conn.execute('INSERT INTO menu_items (title, description, price, category_id, image) VALUES (?, ?, ?, ?, ?)', (title, description, price, category_id, filename))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# --- CUSTOMER PROFILE & ITEMIZED ORDER HISTORY ---
@app.route('/profile')
def customer_profile():
    if 'user_id' not in session:
        flash('Please log in to view your order history.', 'danger')
        return redirect(url_for('customer_login'))
        
    conn = get_db_connection()
    
    # 1. Fetch all master orders belonging to this user
    orders = conn.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY id DESC
    ''', (session['user_id'],)).fetchall()
    
    # 2. Fetch all itemized breakdowns linked to this user's orders using an SQL JOIN
    order_items_raw = conn.execute('''
        SELECT order_items.*, menu_items.title 
        FROM order_items 
        JOIN menu_items ON order_items.menu_item_id = menu_items.id
        JOIN orders ON order_items.order_id = orders.id
        WHERE orders.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    # Map itemized data rows systematically into a dictionary grouped by order_id
    items_by_order = {}
    for item in order_items_raw:
        order_id = item['order_id']
        if order_id not in items_by_order:
            items_by_order[order_id] = []
        items_by_order[order_id].append(item)
    
    return render_template('profile.html', orders=orders, items_by_order=items_by_order)

@app.route('/admin/order/status/<int:id>', methods=['POST'])
def update_order_status(id):
    if not session.get('logged_in'): 
        return redirect(url_for('login'))
    
    new_status = request.form['status']
    
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()
    
    flash(f'Order #{id} status updated to {new_status}!', 'success')
    return redirect(url_for('admin_dashboard'))

# 1. Update the view router link to pass fulfillment types forward into the layout context variables
@app.route('/process-payment-view', methods=['POST'])
def process_payment_view():
    grand_total = float(request.form.get('grand_total', 0.00))
    cart_json = request.form.get('cart_json', '[]')
    fulfillment_type = request.form.get('fulfillment_type', 'Takeout')
    fulfillment_details = request.form.get('fulfillment_details', '')
    
    return render_template(
        'payment.html', 
        grand_total=grand_total, 
        cart_json=cart_json, 
        fulfillment_type=fulfillment_type, 
        fulfillment_details=fulfillment_details
    )



if __name__ == '__main__':
    app.run()
