from models import ShoppingList


def test_shopping_list_access(client, app, login):
    response = client.get("/shopping_list")

    assert b"<h2>Shopping List</h2>" in response.data


def test_shopping_list_without_login(client, app):
    response = client.get("/shopping_list")

    assert response.status_code == 302


def test_add_item_to_shopping_list(client, app, login):
    response = client.post("/shopping_list", data={
        "item":"test_item"
    })

    assert b"test_item" in response.data


def test_remove_item_from_shopping_list(client, app, login):
    client.post("/shopping_list", data={
        "item": "test_item"
    })

    with app.app_context():
        food_id = ShoppingList.query.first().food_id

    response = client.post("/remove_list", data={
        "food_id": food_id
    }, follow_redirects=True)

    assert b"test_item" not in response.data
