from flask import request, render_template, redirect, flash, Blueprint
from flask_login import current_user, login_required
from flask_mail import Message

from extensions import db, mail
from models import ShoppingList
from users.views import roles_required

"""
Author: Hugh Johnson
Description: This is the view file for everything handling the shopping list
"""

# blueprint handling all the shopping list functionality
shopping = Blueprint('shopping', __name__)


# route for shopping list webpage
@shopping.route("/shopping_list", methods=["GET", "POST"])
@login_required
@roles_required('user')
def shopping_list():
    # getting post adding new item to the shopping list
    if request.method == "POST":
        # getting the name of the item submitted
        item_name = request.form.get("item")

        # adding the item to the shopping list table linking with user id for individual user access
        db.session.add(ShoppingList(name=item_name, id=current_user.id))
        db.session.commit()
        # returning to shopping list webpage which will be updated
        return render_template("food/shopping.html", items=ShoppingList.query.filter_by(id=current_user.id).all())
    else:
        return render_template("food/shopping.html", items=ShoppingList.query.filter_by(id=current_user.id).all())


# route to remove an item from the shopping list
@shopping.route("/remove_shopping_list", methods=["POST"])
@login_required
def remove_shopping_list():
    # post request removing an item
    if request.method == "POST":
        # fetching the id of the item
        food_id = request.form.get("food_id")
        # getting the item with the given id from the database
        item = ShoppingList.query.filter_by(food_id=food_id).first()
        # deleting the item from the database
        db.session.delete(item)
        db.session.commit()
    return redirect("/shopping_list")


# button to export the shopping list in an email
@shopping.route("/export_email", methods=["POST"])
@login_required
def export_email():
    # getting the list of items associated with the user
    items = ShoppingList.query.filter_by(id=current_user.id).all()
    # getting the names of the items
    names = [i.name for i in items]
    # formatting the email with the shopping list
    msg = Message("Today's Shopping List",
                  sender="cupboardyteam1@gmail.com")
    # setting the recipients of the email
    msg.recipients = [current_user.email]
    # setting the email text
    msg.body = f"Hey {current_user.firstname}, \nHere is your shopping list for today:\n\n" + "\n".join(names)
    # sending the email
    mail.send(msg)
    flash("Email Sent Successfully")
    return redirect("/shopping_list")
