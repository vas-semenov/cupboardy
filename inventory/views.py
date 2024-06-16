# File and code author: Vasily Semenov

from datetime import datetime

from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_required, current_user
from models import Inventory, FoodItems, CustomFoodItem
from users.views import roles_required
from util.util import fetch_product_data, search_products, add_food_item_to_inventory, remove_food_item_from_inventory, \
    logger, update_food_item, remove_custom_food_item_from_inventory, add_custom_food_item_to_inventory, \
    update_custom_food_item

# Define a blueprint for the inventory module
inventory_bp = Blueprint('inventory_bp', __name__)

# Route to display the inventory page
@inventory_bp.route('/inventory')
@login_required
@roles_required("user")
def inventory():
    sort_by = request.args.get('sort_by', '')  # Get sorting preference from query parameters
    inventory_items = Inventory.query.filter_by(id=current_user.id).all()  # Fetch all inventory items for the current user

    if sort_by == 'expiration_date':
        inventory_items.sort(key=lambda x: x.expiration_date)  # Sort items by expiration date if requested

    items = []
    for item in inventory_items:
        if item.food_id:
            food_item = FoodItems.query.get(item.food_id)  # Fetch food item details from FoodItems table
            if food_item:
                product_data = fetch_product_data(food_item.barcode)  # Fetch additional product data using the barcode
                if product_data:
                    items.append({
                        'food_id': food_item.food_id,
                        'amount': item.amount,
                        'units': item.units,
                        'expiration_date': item.expiration_date,
                        'product_name': product_data['product_name'],
                        'image_url': product_data['image_url'],
                        'categories': product_data['categories'],
                        'ingredients_text': product_data['ingredients_text']
                    })
        elif item.cfood_id:
            custom_food_item = CustomFoodItem.query.get(item.cfood_id)  # Fetch custom food item details from CustomFoodItem table
            if custom_food_item:
                items.append({
                    'cfood_id': custom_food_item.cfood_id,
                    'amount': item.amount,
                    'units': item.units,
                    'expiration_date': item.expiration_date,
                    'product_name': custom_food_item.name,
                    'image_url': custom_food_item.image_url,
                    'categories': 'Custom Category',
                    'ingredients_text': 'Custom Ingredients'
                })
    return render_template('food/inventory.html', items=items)  # Render the inventory template with the items

# Route to display the search results for products
@inventory_bp.route('/food/search')
@login_required
def search():
    query = request.args.get('query', '')  # Get search query from query parameters
    page = request.args.get('page', 1, type=int)  # Get page number from query parameters, default to 1
    per_page = 24  # Number of products per page
    if query:
        results = search_products(query)  # Search for products matching the query
        total = len(results)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = results[start:end]

        return render_template('food/search.html', results=paginated_results, query=query, page=page, total=total,
                               per_page=per_page)
    return render_template('food/search.html', results=None, query=query)

# Route to add a food item to the inventory
@inventory_bp.route('/account/add_food_item', methods=['POST'])
@login_required
def add_food_item():
    user_id = request.form.get('user_id')
    barcode = request.form.get('barcode')
    amount = request.form.get('amount', type=float)
    units = request.form.get('units')
    expiration_date_str = request.form.get('expiration_date', default='2024-12-31')  # Default expiration date

    # Convert string to datetime object
    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')

    if not barcode or not amount or not units or not expiration_date:
        flash('All fields are required')
        return redirect(url_for('inventory_bp.inventory'))

    if add_food_item_to_inventory(user_id, barcode, amount, units, expiration_date):
        flash('Food item added successfully')
    else:
        flash('Failed to add food item')

    return redirect(url_for('inventory_bp.inventory'))

# Route to remove a food item from the inventory
@inventory_bp.route('/account/remove_food_item', methods=['POST'])
@login_required
def remove_food_item():
    food_id = request.form.get('food_id')
    cfood_id = request.form.get('cfood_id')
    logger.debug(f"Received food_id: {food_id}, cfood_id: {cfood_id}")

    user_id = current_user.id

    if food_id:
        if remove_food_item_from_inventory(user_id, food_id):
            flash('Food item removed successfully')
            logger.debug('Food item removed successfully')
        else:
            flash('Failed to remove food item')
            logger.debug('Failed to remove food item')
    elif cfood_id:
        if remove_custom_food_item_from_inventory(user_id, cfood_id):
            flash('Custom food item removed successfully')
            logger.debug('Custom food item removed successfully')
        else:
            flash('Failed to remove custom food item')
            logger.debug('Failed to remove custom food item')
    else:
        flash('Food ID or Custom Food ID is required')
        logger.debug('Food ID or Custom Food ID is required')

    return redirect(url_for('inventory_bp.inventory'))

# Route to add a food item to the inventory using its barcode
@inventory_bp.route('/account/add_food_item_by_barcode', methods=['POST'])
@login_required
def add_food_item_by_barcode():
    data = request.get_json()
    barcode = data.get('barcode')
    amount = data.get('amount', 1)
    units = data.get('units', 'pcs')
    expiration_date_str = data.get('expiration_date', '2024-12-31')

    # Convert string to datetime object
    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')

    if not barcode:
        return jsonify({"error": "Barcode is required"}), 400

    user_id = current_user.id

    if add_food_item_to_inventory(user_id, barcode, amount, units, expiration_date):
        return jsonify({"success": "Food item added successfully"})
    else:
        return jsonify({"error": "Failed to add food item"}), 500

# Route to update a food item in the inventory
@inventory_bp.route('/update_food_item', methods=['POST'])
@login_required
def update_food_item_route():
    food_id = request.form.get('food_id')
    amount = request.form.get('amount', type=float)
    units = request.form.get('units')
    expiration_date_str = request.form.get('expiration_date')

    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')

    if not food_id or not amount or not units or not expiration_date:
        logger.error(
            f"Missing required fields: food_id={food_id}, amount={amount}, units={units}, expiration_date={expiration_date}")
        return jsonify({"error": "Missing required fields"}), 400

    if update_food_item(food_id, amount, units, expiration_date):
        return jsonify({"success": "Food item updated successfully"})
    else:
        return jsonify({"error": "Failed to update food item"}), 500

# Route to add a custom food item to the inventory
@inventory_bp.route('/account/add_custom_food_item', methods=['POST'])
@login_required
def add_custom_food_item():
    name = request.form.get('name')
    amount = request.form.get('amount', type=float)
    units = request.form.get('units')
    expiration_date_str = request.form.get('expiration_date')
    image_url = request.form.get('image_url')

    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')

    if not name or not amount or not units or not expiration_date:
        flash('All fields are required')
        return redirect(url_for('inventory_bp.inventory'))

    if add_custom_food_item_to_inventory(current_user.id, name, amount, units, expiration_date, image_url):
        flash('Custom food item added successfully')
    else:
        flash('Failed to add custom food item')

    return redirect(url_for('inventory_bp.inventory'))

# Route to remove a custom food item from the inventory
@inventory_bp.route('/account/remove_custom_food_item', methods=['POST'])
@login_required
def remove_custom_food_item():
    cfood_id = request.form.get('cfood_id')

    if not cfood_id:
        flash('Custom Food ID is required')
        return redirect(url_for('inventory_bp.inventory'))

    if remove_custom_food_item_from_inventory(current_user.id, cfood_id):
        flash('Custom food item removed successfully')
    else:
        flash('Failed to remove custom food item')

    return redirect(url_for('inventory_bp.inventory'))

# Route to update a custom food item in the inventory
@inventory_bp.route('/update_custom_food_item', methods=['POST'])
@login_required
def update_custom_food_item_route():
    cfood_id = request.form.get('cfood_id')
    amount = request.form.get('amount', type=float)
    units = request.form.get('units')
    expiration_date_str = request.form.get('expiration_date')

    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')

    if not cfood_id or not amount or not units or not expiration_date:
        logger.error(
            f"Missing required fields: cfood_id={cfood_id}, amount={amount}, units={units}, expiration_date={expiration_date}")
        return jsonify({"error": "Missing required fields"}), 400

    if update_custom_food_item(cfood_id, amount, units, expiration_date):
        return jsonify({"success": "Custom food item updated successfully"})
    else:
        return jsonify({"error": "Failed to update custom food item"}), 500
