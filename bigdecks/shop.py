from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from datetime import datetime

bp = Blueprint('shop', __name__)

# Sample product data (in a real app, this would come from a database)
PRODUCTS = [
    {'id': 1, 'name': 'Murders at Karlov Manor', 'price': 4.99, 'cards_per_pack': 15, 'image': 'card-pack-1.jpg'},
    {'id': 2, 'name': 'Ravnica Remastered', 'price': 7.99, 'cards_per_pack': 15, 'image': 'card-pack-2.jpg'},
    {'id': 3, 'name': 'Lost Caverns of Ixalan', 'price': 29.99, 'cards_per_pack': 30, 'image': 'card-pack-3.jpg'},
    {'id': 4, 'name': 'Wilds of Eldraine', 'price': 5.99, 'cards_per_pack': 15, 'image': 'card-pack-4.jpg'}
]

@bp.route('/')
def index():
    """Shop index page showing products"""
    return render_template('shop.html', year=datetime.now().year, products=PRODUCTS)

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add a product to the cart"""
    # Initialize session cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}
    
    # Find the product
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('shop.index'))
    
    # Add to cart or increment quantity
    product_id_str = str(product_id)  # Convert to string for session dictionary key
    if product_id_str in session['cart']:
        session['cart'][product_id_str]['quantity'] += 1
    else:
        session['cart'][product_id_str] = {
            'id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': 1
        }
    
    # Save the session
    session.modified = True
    flash(f"{product['name']} added to cart!", 'success')
    return redirect(url_for('shop.index'))

@bp.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = []
    total = 0
    
    if 'cart' in session:
        for item in session['cart'].values():
            item_total = item['price'] * item['quantity']
            cart_items.append({
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'subtotal': item_total
            })
            total += item_total
    
    return render_template('cart.html', year=datetime.now().year, 
                          cart_items=cart_items, total=total)

@bp.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    """Update cart item quantity"""
    if 'cart' not in session:
        return redirect(url_for('shop.cart'))
    
    product_id_str = str(product_id)
    if product_id_str not in session['cart']:
        return redirect(url_for('shop.cart'))
    
    action = request.form.get('action')
    if action == 'increase':
        session['cart'][product_id_str]['quantity'] += 1
    elif action == 'decrease':
        session['cart'][product_id_str]['quantity'] -= 1
        if session['cart'][product_id_str]['quantity'] <= 0:
            session['cart'].pop(product_id_str)
    elif action == 'remove':
        session['cart'].pop(product_id_str)
    
    session.modified = True
    return redirect(url_for('shop.cart'))