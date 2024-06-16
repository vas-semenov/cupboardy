from datetime import datetime

from extensions import db
from flask_login import UserMixin
import flask_wtf
from wtforms.validators import Email
from werkzeug.security import generate_password_hash


# Author: Vasily Semenov
# Model representing a user
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(50), unique=False, nullable=False)
    firstname = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    reset_token = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(15), nullable=False, default="user")
    email_notifs = db.Column(db.Boolean, nullable=False, default=True)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    @staticmethod
    def create_user(email, firstname, password, role, email_notifs):
        new_user = User(email=email,
                        firstname=firstname,
                        password=generate_password_hash(password),
                        role="user",
                        email_notifs=email_notifs,
                        registered_on=datetime.utcnow()
                        )
        db.session.add(new_user)
        db.session.commit()


# Author: Vasily Semenov
# Model representing openFoodFacts food item
class FoodItems(db.Model):
    barcode = db.Column(db.String(13), nullable=False)  # Product barcode references OpenFoodFacts
    expiredCount = db.Column(db.Float, default=0)  # Amount of expired
    consumedCount = db.Column(db.Float, default=0)  # Amount of consumed
    inUse = db.Column(db.Float, default=False)  # In use right now
    units = db.Column(db.String(20), nullable=False)  # Units of measurement
    food_id = db.Column(db.Integer, nullable=False, primary_key=True)  # Food item ID don't touch!! primary key


# Author: Vasily Semenov
# Model representing the inventory
class Inventory(db.Model):
    amount = db.Column(db.Float, nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('user'))  # ID references to user ID
    units = db.Column(db.String(20), nullable=False)  # Units of measurement
    food_id = db.Column(db.Integer, db.ForeignKey('food_items'), nullable=True)  # Food ID references FoodItems food_id
    cfood_id = db.Column(db.Integer, db.ForeignKey('custom_food_item.cfood_id'),
                         nullable=True)  # Custom Food ID references CustomFoodItem cfood_id
    inv_id = db.Column(db.Integer, primary_key=True)  # Inventory ID don't touch
    expiration_date = db.Column(db.DateTime, nullable=False)  # Expiration date
    food_item = db.relationship('FoodItems', foreign_keys=[food_id])
    custom_food_item = db.relationship('CustomFoodItem', foreign_keys=[cfood_id])


class ShoppingList(db.Model):
    name = db.Column(db.String(200), nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('user'))
    food_id = db.Column(db.Integer, primary_key=True, autoincrement=True)


# Author: Vasily Semenov
# Model representing custom food item
class CustomFoodItem(db.Model):
    cfood_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expiredCount = db.Column(db.Float, default=0)
    consumedCount = db.Column(db.Float, default=0)
    inUse = db.Column(db.Boolean, default=False)
    units = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # Optional field for image URL
