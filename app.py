from flask import Flask                                                           #creat web appliction
from backend.routes import setup_routes                                           # Register your Url
from backend.database import db                                                   #Manage the Database
from backend.payment import payment_bp                                            # Import payment module(hangaling payment)
import os                                                                        #used for working with file paths

# Initialize Flask app and explicitly define template and static folder locations
app = Flask(
    __name__,
    template_folder=os.path.abspath("templates"),  # Ensure Flask finds the templates
    static_folder=os.path.abspath("static")       # Ensure Flask finds static files
)

# Set a secret key for session management
app.secret_key = os.urandom(24)  #  Generate Secure random key

# MySQL Database Configuration where and how to connect
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/food_ordering_db' #username and password
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database without below database won@t work
db.init_app(app)

# Set up routes
setup_routes(app)

# Register payment routes
app.register_blueprint(payment_bp, url_prefix="/payment")  # Payment routes at /payment/pay

# Flask server when you run python app.py
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)  # Explicitly define host and port
