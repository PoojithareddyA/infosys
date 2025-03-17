from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app import models  # Import models after initializing db

        # ✅ Import and register Blueprints AFTER app creation
        from app.views import views  
        app.register_blueprint(views)

    return app
