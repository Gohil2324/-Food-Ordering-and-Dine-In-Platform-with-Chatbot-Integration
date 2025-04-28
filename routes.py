import random

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from backend.database import db, User, MenuItem, Order

def setup_routes(app):
    @app.route('/')
    def home():
        """Redirect to the homepage"""
        return redirect(url_for('index'))

    @app.route('/index')
    def index():
        """Render the homepage"""
        return render_template('index.html')

    @app.route('/menu', methods=['GET'])
    def menu():
        """Render the menu page"""
        menu_items = MenuItem.query.all()
        return render_template('menu.html', menu_items=menu_items)

    @app.route('/api/menu', methods=['GET'])
    def get_menu():
        """Return menu items as JSON (for API requests)"""
        menu_items = MenuItem.query.all()
        return jsonify([
            {
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "image_url": item.image_url  # ✅ Ensure image is included
            }
            for item in menu_items
        ])

    @app.route('/order', methods=['GET', 'POST'])
    def order():
        """Handle order placement and retrieval"""
        if request.method == 'POST':
            data = request.form  # Get form data instead of JSON
            user_email = data.get('email')
            phone = data.get('phone')
            address = data.get('address')
            payment_method = data.get('payment')
            total_price = float(data.get('total_price', 0))  # Ensure we get a valid float

            if not all([user_email, phone, address, payment_method, total_price]):
                flash("All fields are required!", "danger")
                return redirect(url_for('order'))

            # Check if user exists in the database
            user = User.query.filter_by(email=user_email).first()
            if not user:
                flash("User not found. Please sign up first.", "danger")
                return redirect(url_for('signup'))

            try:
                new_order = Order(user_id=user.id, total_price=total_price, status="Confirmed")
                db.session.add(new_order)
                db.session.commit()

                # Store order details in session for confirmation page
                session['order_id'] = new_order.id
                session['total_price'] = total_price
                session['payment_method'] = payment_method

                flash("Order placed successfully!", "success")
                return redirect(url_for('order_confirmation'))

            except IntegrityError:
                db.session.rollback()
                flash("An error occurred. Please try again.", "danger")
                return redirect(url_for('order'))

        # Render order page for GET requests
        return render_template('order.html')

    @app.route('/place_order', methods=['POST'])
    def place_order():
        data = request.get_json()

        user_email = data.get("email")
        total_price = float(data.get("total_price", 0))  # Ensure total price is parsed correctly

        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({"success": False, "error": "User not found. Please sign up."}), 400

        try:
            new_order = Order(user_id=user.id, total_price=total_price, status="Confirmed")
            db.session.add(new_order)
            db.session.commit()

            # Store order details in session
            session["order_id"] = new_order.id
            session["total_price"] = total_price
            session["payment_method"] = data.get("payment", "Not Specified")

            return jsonify({"success": True, "redirect": url_for("order_confirmation")})

        except IntegrityError:
            db.session.rollback()
            return jsonify({"success": False, "error": "Database error occurred."}), 500

    @app.route('/order_confirmation')
    def order_confirmation():
        """Display the order confirmation page"""

        if "order_id" not in session:
            flash("No recent order found!", "danger")
            return redirect(url_for("menu"))

        order_id = session.get("order_id")
        total_price = session.get("total_price", 0.0)
        payment_method = session.get("payment_method", "Not Specified")

        return render_template(
            "order_confirmation.html",
            order_id=order_id,
            total_price=f"${total_price:.2f}",  # Ensure correct price formatting
            payment_method=payment_method
        )

    @app.route('/api/orders', methods=['GET'])

    def get_orders():
        """Retrieve all orders as JSON"""
        orders = Order.query.all()
        return jsonify([
            {"id": order.id, "user_id": order.user_id, "total_price": order.total_price, "status": order.status}
            for order in orders
        ])

    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        """Render the Forgot Password Page"""
        return render_template('forgot_password.html')

    # ✅ Fixed: Ensure all routes exist to avoid BuildError in base.html
    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/cart')
    def cart():
        return render_template('cart.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """Handle user registration"""
        if request.method == 'GET':
            return render_template('signup.html')

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([name, email, phone, password, confirm_password]):
            flash("All fields are required!", "danger")
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered!", "danger")
            return redirect(url_for('signup'))

        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            return redirect(url_for('signup'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login"""
        if request.method == 'GET':
            return render_template('login.html')

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password!", "danger")
            return redirect(url_for('login'))

        flash("Login successful!", "success")
        return redirect(url_for('index'))

    @app.route('/invoice')
    def invoice():
        return render_template('invoice.html')

    @app.route('/products')
    def products():
        return render_template('products.html')

    # Sample chatbot responses
    responses = {
        "hi": ["Hello! How can I assist you?", "Hi there! What do you need help with?"],
        "hello": ["Hey! How can I help?", "Hi! Need any recommendations?"],
        "menu": ["We have Burgers, Pizzas, Drinks, and Desserts! What would you like?", "Check out our menu page!"],
        "order": ["You can place an order from the menu!", "What would you like to order today?"],
        "bye": ["Goodbye! Have a great day!", "See you next time!"],
        "default": ["I'm not sure I understand. Can you rephrase?", "Sorry, I didn't get that."]
    }

    import random

    chatbot_responses = {
        "hi": ["Hello! How can I assist you?", "Hi there! What do you need help with?"],
        "hello": ["Hey! How can I help?", "Hi! Need any recommendations?"],
        "menu": [
            "You can check out our menu <a href='/menu' target='_blank'>here</a>!",
            "Browse delicious options on our <a href='/menu' target='_blank'>menu page</a>."
        ],
        "order": ["You can place an order from the menu!", "What would you like to order today?"],
        "veg": ["We have delicious vegetarian options like paneer tikka, veggie burger, and more!"],
        "non veg": ["Try our grilled chicken, mutton biryani, or spicy wings!"],
        "vegan": ["Yes! We offer fresh salads, tofu bowls, and plant-based burgers."],
        "allergy": ["Do you have any allergies we should know about?",
                    "Let us know your dietary restrictions so we can help!"],
        "book": [
            "Sure! You can book a table <a href='/book_table' target='_blank'>here</a>.",
            "Click <a href='/book_table' target='_blank'>here</a> to reserve a table now."
        ],
        "time": ["What time would you like to book your table for?",
                 "You can pick a time on our <a href='/book_table' target='_blank'>booking page</a>."],
        "bye": ["Goodbye! Have a great day!", "See you next time!"],
        "default": ["I'm not sure I understand. Can you rephrase?",
                    "Sorry, I didn't get that. Can you say it differently?"]
    }

    @app.route("/chatbot", methods=["GET", "POST"])
    def chatbot():
        if request.method == "POST":
            user_message = request.json.get("message", "").lower()
            reply = chatbot_responses.get(user_message, chatbot_responses["default"])
            return jsonify({"reply": random.choice(reply)})

        return render_template('chatbot.html')



    @app.route('/check-email', methods=['POST'])
    def check_email():
        """Check if an email is already registered (AJAX request)"""
        data = request.get_json()
        email = data.get('email')
        exists = User.query.filter_by(email=email).first() is not None
        return jsonify({"available": not exists})

    @app.route('/search')
    def search():
        return render_template('search.html')

    # ✅ Added a 404 Error Handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/book_table', methods=['GET', 'POST'])
    def book_table():
        """Handle table bookings"""
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            date = request.form.get('date')
            time = request.form.get('time')
            guests = request.form.get('guests')
            special_request = request.form.get('special_request')

            if not all([name, email, phone, date, time, guests]):
                flash("All fields except special requests are required!", "danger")
                return redirect(url_for('book_table'))

            try:
                # Store booking details in session (or database if needed)
                session['booking'] = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "date": date,
                    "time": time,
                    "guests": guests,
                    "special_request": special_request
                }

                flash("Table booked successfully!", "success")
                return redirect(url_for('booking_confirmation'))

            except Exception as e:
                flash("An error occurred while booking. Please try again.", "danger")
                return redirect(url_for('book_table'))

        return render_template('book_table.html')

    @app.route('/booking_confirmation')
    def booking_confirmation():
        """Booking Confirmation Page"""
        if "booking" not in session:
            flash("No recent booking found!", "danger")
            return redirect(url_for("book_table"))

        booking = session.get("booking")
        return render_template('booking_confirmation.html', booking=booking)

    @app.route('/feedback', methods=['GET'])
    def feedback():
        """Render the feedback page"""
        return render_template('feedback.html')

    @app.route('/submit_feedback', methods=['POST'])
    def submit_feedback():
        """Handle feedback form submission"""
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not all([name, email, message]):
            flash("All fields are required!", "danger")
            return redirect(url_for('feedback'))

        try:
            # Store feedback in database (if using a DB)
            # new_feedback = Feedback(name=name, email=email, message=message)
            # db.session.add(new_feedback)
            # db.session.commit()

            flash("Thank you for your feedback!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash("An error occurred. Please try again.", "danger")
            return redirect(url_for('feedback'))






