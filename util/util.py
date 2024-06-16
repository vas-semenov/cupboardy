# File and code author: Vasily Semenov


from openfoodfacts import API, Country, Flavor, APIVersion, Environment
from flask_login import current_user
from models import FoodItems, Inventory, CustomFoodItem
from extensions import db
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize API object
api = API(
    user_agent="MyAwesomeApp/1.0",
    country=Country.world,
    flavor=Flavor.off,  # Open Food Facts
    version=APIVersion.v2,
    environment=Environment.org
)


# Fetch product data from Open Food Facts using the barcode
def fetch_product_data(barcode):
    try:
        product_data = api.product.get(barcode)
        if product_data:
            return {
                'product_name': product_data.get('product_name', 'No name available'),
                'image_url': product_data.get('image_url', 'placeholder.jpg'),
                'nutriments': product_data.get('nutriments', {}),
                'ingredients_text': product_data.get('ingredients_text', 'No ingredients available'),
                'categories': product_data.get('categories', 'No categories available'),
                'barcode': barcode  # Ensure barcode is included
            }
        return None
    except Exception as e:
        return None


# Search products from Open Food Facts using a query
def search_products(query):
    try:
        search_results = api.product.text_search(query)
        products = search_results.get('products', [])
        return products
    except Exception as e:
        return []


# Add a food item to the user's inventory
def add_food_item_to_inventory(user_id, barcode, amount, units, expiration_date):
    food_item = FoodItems.query.filter_by(barcode=barcode).first()
    if not food_item:
        product_data = fetch_product_data(barcode)
        if product_data:
            food_item = FoodItems(
                barcode=barcode,
                expiredCount=0,
                consumedCount=0,
                inUse=False,
                units=units
            )
            db.session.add(food_item)
            db.session.commit()
        else:
            return False  # Failed to fetch product data

    # Check if the item already exists in the inventory
    existing_inventory_item = Inventory.query.filter_by(id=user_id, food_id=food_item.food_id).first()
    if existing_inventory_item:
        existing_inventory_item.amount += amount
        existing_inventory_item.expiration_date = expiration_date
    else:
        new_inventory = Inventory(
            amount=amount,
            id=user_id,
            units=units,
            food_id=food_item.food_id,
            expiration_date=expiration_date
        )
        db.session.add(new_inventory)

    db.session.commit()
    return True


# Remove a food item from the user's inventory
def remove_food_item_from_inventory(user_id, food_id):
    logger.debug(f"Attempting to remove food item with food_id: {food_id} for user_id: {user_id}")

    # Find the Inventory record and remove it
    inventory_item = Inventory.query.filter_by(id=user_id, food_id=food_id).first()
    if inventory_item:
        logger.debug(f"Found inventory item: {inventory_item}")
        db.session.delete(inventory_item)
        db.session.commit()
        logger.debug("Food item removed successfully")
        return True
    else:
        logger.debug("No inventory item found")
    return False


# Update a food item in the user's inventory
def update_food_item(food_id, amount, units, expiration_date):
    inventory_item = Inventory.query.filter_by(food_id=food_id, id=current_user.id).first()
    if inventory_item:
        inventory_item.amount = amount
        inventory_item.units = units
        inventory_item.expiration_date = expiration_date
        db.session.commit()
        logger.debug(f"Food item updated: food_id={food_id}")
        return True
    logger.error(f"Food item not found: food_id={food_id}")
    return False


# Add a custom food item to the user's inventory
def add_custom_food_item_to_inventory(user_id, name, amount, units, expiration_date, image_url):
    # Create new custom food item
    new_custom_food_item = CustomFoodItem(
        name=name,
        units=units,
        image_url=image_url,
    )
    db.session.add(new_custom_food_item)
    db.session.commit()

    # Add the custom food item to the inventory
    new_inventory_item = Inventory(
        amount=amount,
        id=user_id,
        units=units,
        cfood_id=new_custom_food_item.cfood_id,  # Set the cfood_id
        expiration_date=expiration_date,
        food_id=None  # Ensure food_id is None
    )
    db.session.add(new_inventory_item)
    db.session.commit()
    return True


# Remove a custom food item from the user's inventory
def remove_custom_food_item_from_inventory(user_id, cfood_id):
    inventory_item = Inventory.query.filter_by(id=user_id, cfood_id=cfood_id).first()
    if inventory_item:
        db.session.delete(inventory_item)
        db.session.commit()
        return True
    return False


# Update a custom food item in the user's inventory
def update_custom_food_item(cfood_id, amount, units, expiration_date):
    inventory_item = Inventory.query.filter_by(cfood_id=cfood_id, id=current_user.id).first()
    if inventory_item:
        inventory_item.amount = amount
        inventory_item.units = units
        inventory_item.expiration_date = expiration_date
        db.session.commit()
        return True
    return False
