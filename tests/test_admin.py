from models import User


def test_admin_page_access(client):
    response = client.get("/")
    assert b"<h1>Cupboardy Admin</h1>" in response.data

def test_admin_register(client,app):
        client.post("/register", data={
            "username": "admintests",
            "email": "admintests@mail.com",
            "firstname": "admintests",
            "postcode": "NE1 1AA",
            "password": "admintests",
            "confirm_password": "admintests",
            "email_notifs": "on"
        })

        with app.app_context():
            assert User.query.count() == 1
            assert User.query.first().email == "admintest@mail.com"


def test_admin_login(client, admin_login):
    response = admin_login
    assert b"<h2> Accounts Details Page </h2>" in response.data


def test_view_customers(client, admin_login, login, app):
    login()
    admin_login()

    # Access view_customers page
    response = client.get("/view_customers")

    assert response.status_code == 200
    assert b"tests" in response.data
    assert b"admin" not in response.data



def test_view_stats(client, admin_login, login):
    with app.app_context():
        user_id = User.query.first().id
        client.post("/account/add_food_item", data={
            "user_id": user_id,
            "barcode": 54491472,
            "amount": 1,
            "units": "pcs"
        }, follow_redirects=True)

        response = client.get("view_food_stats")
        assert b"admin" not in response.data
