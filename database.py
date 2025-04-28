from flask_sqlalchemy import SQLAlchemy
#Used to connect your Python app with a relational database

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  # Ensure correct table name
    id = db.Column(db.Integer, primary_key=True)
    # unique=True: no duplicates allowed and
    # nullable=False: field is required
    #All the db.Column(...) fields become columns in the SQL table
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)



    # Correct relationship definition
    orders = db.relationship('Order', backref='user_orders', lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'  # Ensure correct table name
    # Below one stores all menu items with a name,
    # description, price, and image link.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

class Order(db.Model):
    __tablename__ = 'orders'  # Ensure correct table name
    # Each order has a unique ID.
    id = db.Column(db.Integer, primary_key=True)
    #ForeignKey means it refers to users.id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   #Price, order status (like “Pending”, “Confirmed”)
    # and time when it was created
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Remove conflicting backref
    user = db.relationship('User', back_populates="orders")  # ✅ Fixed conflict

# Update back_populates for bidirectional relationship
#  stores all menu items with a name, description, price, and image link.
User.orders = db.relationship("Order", back_populates="user")
