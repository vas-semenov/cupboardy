from models import User


def test_inventory_access(client, app, login):
    response = client.get("/inventory")

    assert b"<h2>Inventory</h2>" in response.data


def test_inventory_without_login(client, app):
    response = client.get("/inventory")

    assert response.status_code == 302


def test_inventory_search_new_food(client, app, login):
    response = client.get("/food/search?query=beans")
    assert b"Beanz In a rich tomato sauce" in response.data


def test_inventory_add_food_from_search(client, app, login):
    with app.app_context():
        user_id = User.query.first().id

    response = client.post("/account/add_food_item", data={
        "user_id": user_id,
        "barcode": 54491472,
        "amount": 1,
        "units": "pcs"
    }, follow_redirects = True)
    print (response.data)
    assert b"Coca Cola" in response.data



