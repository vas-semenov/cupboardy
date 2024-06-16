from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from werkzeug.security import generate_password_hash

import extensions
from config import Config
import logging

from extensions import login_manager, db, mail
from inventory.views import inventory_bp
from shopping.views import shopping
from admin.views import admins
from routes import mainbp
from users.views import users

import pymysql

pymysql.install_as_MySQLdb()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# function to create the app
def create_app(sql_uri="mysql://root:root@db:3306/cupboardy"):
    # initialising the app
    app = Flask(__name__)
    # setting the configurations from file and some settings
    app.config.from_object(Config)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'cupboardyteam1@gmail.com'
    app.config['MAIL_PASSWORD'] = 'rtbx fcmb ahvn hpew'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = 'cupboardyteam1@gmail.com'
    app.config['SQLALCHEMY_DATABASE_URI'] = sql_uri

    # initialising external connections
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    extensions.testing = True

    # setting the login view for the login manager
    login_manager.login_view = 'users.login'

    # registering the blueprints with pages
    app.register_blueprint(shopping)
    app.register_blueprint(mainbp)
    app.register_blueprint(users)
    app.register_blueprint(admins)
    app.register_blueprint(inventory_bp)

    # error handlers for the website
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('error/400.html'), 400

    @app.errorhandler(403)
    def forbidden_request(error):
        return render_template('error/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_server(error):
        return render_template('error/500.html'), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        return render_template('error/503.html'), 503

    import models

    # database instantiation code
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
            # admin role as a base role
            admin = models.User(email='admin@gmail.com',
                                email_notifs=True,
                                firstname='Admin Account',
                                role = 'admin',
                                password=generate_password_hash('Admin1!'))

            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        print("Database already exists")

    return app
