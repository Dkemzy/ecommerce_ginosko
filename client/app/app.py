import os
import secrets
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt  # Import the Bcrypt extension
from models import db, User
from main import main  # Import the main Blueprint
from datetime import timedelta

# Use os.path.join for cross-platform compatibility
file_path = os.path.abspath(os.path.join(os.getcwd(), "instance", "ecommerce.db"))

# Initialize the extensions
login_manager = LoginManager()
bcrypt = Bcrypt()  # Initialize Bcrypt

def create_app():
    # Create and configure the app
    app = Flask(__name__)

    # Use os.path.join for cross-platform compatibility
    file_path = os.path.abspath(os.path.join(os.getcwd(), "instance", "ecommerce.db"))

    app.config['SECRET_KEY'] = secrets.token_hex(16)  # Use secrets module for a strong secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
    app.permanent_session_lifetime = timedelta(minutes=30)

    # Initialize the extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)  # Initialize Bcrypt with the app

    # Set the login view to the admin login endpoint
    login_manager.login_view = 'main.admin_login'

    # Register the blueprints
    app.register_blueprint(main)

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        # Try loading the user from the User model
        return User.query.get(int(user_id))

    # Create the tables within the application context
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5030)
