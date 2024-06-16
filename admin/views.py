
from flask_mail import Message
from flask import flash, render_template, redirect, url_for, Blueprint
from models import User
from users.forms import RegisterForm
from extensions import mail
admins = Blueprint('admin', __name__)


@admins.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    form = RegisterForm()
    # validates form when submitted
    if form.validate_on_submit():
        # collects data from form
        email = form.email.data
        password = form.password.data
        firstname = form.firstname.data
        role = "admin"
        email_notifs = True

        # searches through the database for the username.
        if User.query.filter_by(email=email).first():
            # displays a message if the username exists
            flash('Username already exists!')
            # renders admin template with error message
            return render_template('admin.html', error='Username already exists!', form=form)
        # creates new admin user
        User.create_user(email, password, firstname, role, email_notifs)

        # creates message format
        msg = Message("Announcement",
                      sender="cupboardyteam1@gmail.com",
                      recipients=[email])

        # creates message body
        msg.body = f"Hey {firstname}, \nYou have been added as an admin to cupboardy"

        # sends message
        mail.send(msg)
        # displays message to confirm message has been sent
        flash('New Admin Added')
        # redirects user to admin page
        return redirect(url_for('admin.add_admin'))
    # renders register page
    return render_template('account/register.html', form=form)
