from flask import Blueprint, render_template, request, redirect, url_for
from app.models import Product, Brand, Cart, Wishlist
from app import db

views = Blueprint('views', __name__)  # Blueprint for views

@views.route('/')
def homepage():
    brands_list = Brand.query.all()
    return render_template('home.html', brands=brands_list)

@views.route('/brand/<int:brand_id>')
def brand_info(brand_id):
    brand_data = Brand.query.get(brand_id)
    if not brand_data:
        return "Brand not found", 404
    brand_items = Product.query.filter_by(brand_id=brand_id).all()
    return render_template('brand_details.html', brand=brand_data, products=brand_items)

@views.route('/product/<int:product_id>')
def product_info(product_id):
    product_data = Product.query.get_or_404(product_id)
    return render_template('product_details.html', product=product_data)

@views.route('/add_to_cart/<int:product_id>', methods=['POST'])
def cart_add(product_id):
    product_data = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        new_cart_item = Cart(product_id=product_data.id, quantity=1)
        db.session.add(new_cart_item)
    db.session.commit()
    return redirect(url_for('views.show_cart'))

@views.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def cart_remove(cart_id):
    cart_entry = Cart.query.get_or_404(cart_id)
    if cart_entry.quantity > 1:
        cart_entry.quantity -= 1
    else:
        db.session.delete(cart_entry)
    db.session.commit()
    return redirect(url_for('views.show_cart'))

@views.route('/cart')
def show_cart():
    cart_list = Cart.query.all()
    total_mrp = sum(item.cart_product.price * item.quantity for item in cart_list)
    discount_mrp = total_mrp * 0.56  # Assuming 56% discount as per the image
    total_amount = total_mrp - discount_mrp

    return render_template(
        'cart.html',
        cart_items=cart_list,
        total_mrp=total_mrp,
        discount_mrp=discount_mrp,
        total_amount=total_amount
    )

@views.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def wishlist_add(product_id):
    product_data = Product.query.get_or_404(product_id)
    wishlist_item = Wishlist.query.filter_by(product_id=product_id).first()
    if not wishlist_item:
        new_wishlist_entry = Wishlist(product_id=product_data.id)
        db.session.add(new_wishlist_entry)
    db.session.commit()
    return redirect(url_for('views.show_wishlist'))

@views.route('/move_to_wishlist/<int:cart_id>', methods=['POST'])
def move_to_wishlist(cart_id):
    # Get the cart item
    cart_item = Cart.query.get_or_404(cart_id)
    
    # Check if the product is already in the wishlist
    wishlist_item = Wishlist.query.filter_by(product_id=cart_item.product_id).first()
    
    if not wishlist_item:
        # Add the product to the wishlist
        new_wishlist_item = Wishlist(product_id=cart_item.product_id)
        db.session.add(new_wishlist_item)
    
    # Remove the product from the cart
    db.session.delete(cart_item)
    db.session.commit()
    
    return redirect(url_for('views.show_cart'))

@views.route('/remove_from_wishlist/<int:wishlist_id>', methods=['POST'])
def wishlist_remove(wishlist_id):
    wishlist_entry = Wishlist.query.get_or_404(wishlist_id)
    db.session.delete(wishlist_entry)
    db.session.commit()
    return redirect(url_for('views.show_wishlist'))

@views.route('/wishlist')
def show_wishlist():
    wishlist_list = (
        db.session.query(Wishlist.id, Product.name, Product.price, Product.image_file, Product.id.label("product_id"))
        .join(Product, Wishlist.product_id == Product.id)
        .all()
    )
    return render_template('wishlist.html', wishlist_items=wishlist_list)