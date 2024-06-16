from models import User


def test_homepage_access(client):
    response = client.get("/")
    assert b"<h1>Welcome to Cupboardy</h1>" in response.data


def test_client_register(client, app):

    client.post("/register", data={
        "username": "tests",
        "email": "test@mail.com",
        "firstname": "tests",
        "postcode": "tests",
        "password": "tests",
        "confirm_password": "tests",
        "email_notifs": "on"
    })

    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "test@mail.com"


def test_client_login(client, app, login):
    response = login
    assert response.status_code == 200


def test_client_logout(client, app, login):

    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200


def test_account_without_login(client, app):
    response = client.get("/account")

    assert response.status_code == 302
