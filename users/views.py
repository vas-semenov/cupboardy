import secrets
from datetime import datetime
from functools import wraps

from flask_login import login_required, logout_user, login_user, current_user
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, mail
from models import User
from users.forms import RegisterForm, LoginForm, ChangePasswordEmail, ChangePassword
from flask import flash, render_template, redirect, url_for, Blueprint, request

users = Blueprint('users', __name__)


def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                return render_template('error/403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("SOMETHING HAPPENED")
        print("form sent")
        email = form.email.data
        firstname = form.firstname.data
        password = form.password.data
        role = "user"
        email_notifs = True

        if User.query.filter_by(email=email).first():
            flash('Email already Registered')
            print("FAILED")
            return render_template('account/register.html', error='Email already Registered', form=form)
        else:
            User.create_user(email, firstname, password, role, email_notifs)

        msg = Message("Daily Food Updates",
                      sender="cupboardyteam1@gmail.com",
                      recipients=[email])

        msg.body = f"Hello, \nThank you for signing up to Cupboardy\n"

        mail.send(msg)
        print("SUCCEEDING")
        return redirect(url_for('users.login'))

    return render_template('account/register.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.loginEmail.data
        password = form.loginPassword.data

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_login = datetime.now()
            db.session.commit()
            if current_user.role == 'admin':
                return redirect(url_for('users.admin'))
            elif current_user.role == 'user':
                return redirect(url_for('mainbp.main'))
        else:
            flash('Invalid username or password')

    return render_template('account/login.html', form=form)


@users.route('/account')
@login_required
def account():
    return render_template('account/account.html')


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('mainbp.main'))


@users.route('/admin')
@roles_required("admin")
@login_required
def admin():
    return render_template('admin.html')


@users.route('/update_password')
def update_password():
    return url_for('users.account')

"""
Author: Nathan
Description: Function to create and send email for password reset
"""
@users.route('/change_password_email', methods=['POST', 'GET'])
def change_password_email():
    form = ChangePasswordEmail()
    if form.validate_on_submit():
        # gets email to send link to
        email = request.form['email']
        #generates secure token
        token = secrets.token_urlsafe(16)
        # checks that the email links to a registered account
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email not found', 'error')
        else:
            user.reset_token = token
            # updates the database
            db.session.commit()

            # generates URL
            reset_url = url_for('users.change_password', token=token, _external=True)

            msg = Message('Password Reset Request', sender='cupboardyteam1@gmail.com', recipients=[email])
            msg.body = f'Please click the link to change your password: {reset_url}'
            #sends email
            mail.send(msg)
            flash('Password reset email has been sent', 'info')
        return redirect(url_for('mainbp.main'))
    return render_template("account/change_password_email.html", form=form)


"""
Author: Nathan
Description: Function to change password
"""
@users.route('/users.change_password/<token>', methods=['GET', 'POST'])
def change_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash('Invalid or expired token', 'error')
        return redirect(url_for('mainbp.main'))

    form = ChangePassword()

    if form.validate_on_submit():
        new_password = form.password.data
        user.password = generate_password_hash(new_password)
        user.reset_token = None
        #updates database
        db.session.commit()
        flash('Your password has been changed', 'success')
        if current_user.is_authenticated:
            return redirect(url_for('users.logout'))
        return redirect(url_for('users.login'))
    return render_template('account/change_password.html', token=token, form=form)
