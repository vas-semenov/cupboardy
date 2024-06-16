import os, sys, inspect

import pytest


from app import create_app
from extensions import db


@pytest.fixture
def app():
    # initialising the environment for the app
    app = create_app(sql_uri='sqlite://')

    # updating configurations for testing environment
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "MAIL_SUPPRESS_SEND": True
    })

    # creating the test database
    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def login(client, app):
    def _login():
        # registering the user
        client.post("/register", data={
            "username": "tests",
            "email": "tests@mail.com",
            "firstname": "tests",
            "postcode": "tests",
            "password": "tests",
            "confirm_password": "tests",
            "email_notifs": "on"
        })

        # logging the new user in
        response = client.post("/login", data={
            'loginEmail': 'tests@mail.com',
            'loginPassword': 'tests'
        }, follow_redirects=True)

        # ensuring everything worked
        assert response.status_code == 200
        return response
    return _login()

@pytest.fixture
def admin_login(client, app):
    def _login():
        client.post("/register", data={
            "username": "admintests",
            "email": "admintests@mail.com",
            "password": "admintests",
            "confirm_password": "admintests",
            "email_notifs": "on"
        })

        # Log the admin user in
        response = client.post("/login", data={
            'username': 'admintests@mail.com',
            'password': 'admintests'
        }, follow_redirects=True)

        assert response.status_code == 200
        return response
    return _login
