from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
    # Initialize database and migrations
    db.init_app(app)

    with app.app_context():
        # Import models after initializing db
        from app import models  
        migrate.init_app(app, db)

    # Import and register Blueprints after app is created
    from app.views import views  
    app.register_blueprint(views)

    return app
