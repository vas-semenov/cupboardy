from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import app
from extensions import db, login_manager, mail, testing
from models import User, Inventory, FoodItems, CustomFoodItem
from flask import jsonify

from users.views import roles_required
from util.util import fetch_product_data, search_products, add_food_item_to_inventory, remove_food_item_from_inventory, \
    update_food_item, add_custom_food_item_to_inventory, remove_custom_food_item_from_inventory, update_custom_food_item
from util.googlemaps_util import get_location_data, get_food_banks, get_food_bank_details
import requests
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

mainbp = Blueprint('mainbp', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@mainbp.route('/')
def main():
    return render_template('main.html')


# Author: Vasily Semenov
# Route for viewing product data from search window
@mainbp.route('/product/<barcode>')
def product_detail(barcode):
    print(f"Received barcode: {barcode}")  # Debugging line
    product = fetch_product_data(barcode)
    if product:
        return render_template('food/product_detail.html', product=product)
    else:
        return render_template('food/product_detail.html', error="Product not found")


'''Author: Ayomide Kehinde
Function: To display all the users'''


@mainbp.route('/view_customers')
@login_required
def view_customers():
    # searches through the database for user with user role
    current_users = User.query.filter_by(role='user').all()
    # renders the admin template with the users
    return render_template('admin.html', current_users=current_users)


'''Author: Ayomide Kehinde
Function: To display expired food items'''


@mainbp.route('/view_food_stats', methods=['GET', 'POST'])
@login_required
def view_food_stats():
    # searches through the database for user with user role
    current_users = User.query.filter_by(role='user').all()
    # creates a list for expired food
    expired_food_stats = []
    # iterates through the users
    for user in current_users:
        # gets the inventory items of the users
        inventory_items = Inventory.query.filter_by(id=user.id).all()
        # iterates through items of the inventory
        for item in inventory_items:
            # retrieves information about the item
            food_item = FoodItems.query.get(item.food_id)
            product_data = fetch_product_data(food_item.barcode)
            # checks if the item has expired
            if item.expiration_date < datetime.now():
                # adds the item to the list
                expired_food_stats.append({
                    'email': user.email,
                    'product_name': product_data['product_name'],
                    'expiration_date': item.expiration_date,
                    'amount': item.amount,
                    'units': item.units
                })

    # returns admin page with the list of expired items
    return render_template('admin.html', expired_food_stats=expired_food_stats)


"""
Author: Thomas Reece
Description: This route is used to display the food banks near the user's location.
"""


@mainbp.route('/donate', methods=['GET', 'POST'])
@roles_required("user")
@login_required
def donate():
    if request.method == 'POST':
        postcode = request.form.get('postcode')

        if not re.match(r'^[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][ABD-HJLNP-UW-Z]{2}$', postcode, re.I):
            flash("Invalid postcode", 'error')
            return redirect(url_for('mainbp.donate'))

        location_data = get_location_data(postcode)
        if location_data:
            food_banks = get_food_banks(location_data['latitude'], location_data['longitude'])
            for food_bank in food_banks:
                details = get_food_bank_details(food_bank['place_id'])
                if details:
                    food_bank['phone_number'] = details['phone_number']
                    food_bank['website'] = details['website']
            return render_template('donate.html', food_banks=food_banks, postcode=postcode,
                                   latitude=location_data['latitude'], longitude=location_data['longitude'])
        else:
            flash("Location not found.", 'error')
            return redirect(url_for('mainbp.donate'))
    return render_template('donate.html')


"""
Author: Hugh Johnson
Description: Function handling sending email updates with food expiring soon
"""


@mainbp.route('/send_updates')
@login_required
def send_updates():
    # storing the current date for comparison
    currentDate = datetime.now()
    # iterating through every user with email notifications on
    for user in User.query.filter_by(email_notifs=True):
        # keeping track of foods expiring soon
        expiring_soon = []
        # iterating through each food item associated with a user
        for food_item in Inventory.query.filter_by(id=user.id).all():
            # checking if the food item expires in the next day
            if currentDate + timedelta(days=1) >= food_item.expiration_date:
                # getting the name of the food item from the open food facts database
                barcode = FoodItems.query.filter_by(food_id=food_item.food_id).first().barcode
                food_name = fetch_product_data(barcode).get("product_name")
                # adding the food item to the expiring soon file
                expiring_soon.append(food_name + " is expiring " + str(food_item.expiration_date.date()))
        # sending email only if there is food expiring
        if expiring_soon != []:
            # forming the email
            msg = Message("Daily Food Updates",
                          sender="cupboardyteam1@gmail.com",
                          recipients=[user.email])
            msg.recipients = [user.email]
            msg.body = f"Hey {user.firstname}, \nHere is your daily reminder of items expiring in the next day.\n" + "\n".join(
                expiring_soon)
            # sending the email
            mail.send(msg)
    flash('Email notifications sent successfully')
    return redirect(url_for('users.admin'))
