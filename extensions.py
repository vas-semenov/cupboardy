from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
db = SQLAlchemy()
mail = Mail()
testing = False
