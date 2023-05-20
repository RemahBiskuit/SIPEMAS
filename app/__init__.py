from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from app.errors.routes import error_404, error_500

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)

    # Retrieve configuration information
    app.config.from_object('app.config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/sipemas'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialization of blueprints
    from app.main import main_bp

    # Error handlers
    app.register_error_handler(404, error_404)
    app.register_error_handler(500, error_500)

    app.register_blueprint(main_bp)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    return app

from app import models

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
