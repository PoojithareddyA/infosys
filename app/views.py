from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from app.models import Product, Brand, Cart, Wishlist, Address
from app import db

views = Blueprint('views', __name__)

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
    db.session.delete(cart_entry)
    db.session.commit()
    return redirect(url_for('views.show_cart'))

@views.route('/update_cart_quantity/<int:cart_id>', methods=['POST'])
def update_cart_quantity(cart_id):
    cart_entry = Cart.query.get_or_404(cart_id)
    new_quantity = request.form.get("quantity", type=int)

    if new_quantity and new_quantity > 0:
        cart_entry.quantity = new_quantity
        db.session.commit()

    # Recalculate totals
    cart_list = Cart.query.all()
    total_mrp = sum(item.cart_product.current_price * item.quantity for item in cart_list)
    discount_mrp = int(total_mrp * 0.56)  # 56% discount as per your logic
    total_amount = int(total_mrp - discount_mrp)

    return jsonify({
        "total_mrp": total_mrp,
        "discount_mrp": discount_mrp,
        "total_amount": total_amount
    })


@views.route('/cart')
def show_cart():
    cart_list = Cart.query.all()
    total_mrp = int(sum(item.cart_product.current_price * item.quantity for item in cart_list))
    discount_mrp = int(total_mrp * 0.56)
    total_amount = int(total_mrp - discount_mrp)
    
    return render_template(
        'cart.html',
        cart_items=cart_list,
        total_mrp=total_mrp,
        discount_mrp=discount_mrp,
        total_amount=total_amount
    )



@views.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user_id = 1  # Temporary user ID, replace with actual logic later
    addresses = Address.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        selected_address_id = request.form.get('address_id')
        session['selected_address'] = selected_address_id
        return redirect(url_for('payment'))  # Redirect to payment page

    return render_template('checkout.html', addresses=addresses)


@views.route('/add_address', methods=['POST'])
def add_address():
    user_id = 1  # No login system, using a default user ID
    new_address = Address(
        user_id=user_id,
        name=request.form['name'],
        phone=request.form['phone'],
        address_line=request.form['address_line'],  # Changed from 'address' to 'address_line'
        city=request.form['city'],
        state=request.form['state'],
        pincode=request.form['pincode']
    )
    db.session.add(new_address)
    db.session.commit()
    return redirect(url_for('checkout'))


@views.route('/delete_address/<int:address_id>', methods=['POST'])
def delete_address(address_id):
    user_id = 1  # Temporary user ID

    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({'success': False, 'message': 'Address not found'}), 404

    db.session.delete(address)
    db.session.commit()
    return redirect(url_for('checkout'))


@views.route('/edit_address/<int:address_id>', methods=['POST'])
def edit_address(address_id):
    user_id = 1  # Temporary user ID

    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({'success': False, 'message': 'Address not found'}), 404

    # Updating address fields
    address.name = request.form['name']
    address.phone = request.form['phone']
    address.address_line = request.form['address_line']  # Changed from 'address'
    address.city = request.form['city']
    address.state = request.form['state']
    address.pincode = request.form['pincode']

    db.session.commit()
    return redirect(url_for('checkout'))


@views.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def wishlist_add(product_id):
    # Temporary workaround: Use a default user ID (e.g., 1)
    default_user_id = 1  # Change this when implementing authentication

    product_data = Product.query.get_or_404(product_id)
    wishlist_item = Wishlist.query.filter_by(product_id=product_id, user_id=default_user_id).first()
    
    if not wishlist_item:
        new_wishlist_entry = Wishlist(user_id=default_user_id, product_id=product_data.id)
        db.session.add(new_wishlist_entry)
        db.session.commit()
    
    return redirect(url_for('views.show_wishlist'))


@views.route('/remove_from_wishlist/<int:wishlist_id>', methods=['POST'])
def remove_from_wishlist(wishlist_id):
    wishlist_entry = Wishlist.query.get_or_404(wishlist_id)
    db.session.delete(wishlist_entry)
    db.session.commit()
    return redirect(url_for('views.show_wishlist'))

@views.route('/move_to_wishlist/<int:cart_id>', methods=['POST'])
def move_to_wishlist(cart_id):
    default_user_id = 1  # Temporary until authentication is implemented

    cart_item = Cart.query.get_or_404(cart_id)
    wishlist_item = Wishlist.query.filter_by(product_id=cart_item.product_id, user_id=default_user_id).first()
    
    if not wishlist_item:
        new_wishlist_item = Wishlist(user_id=default_user_id, product_id=cart_item.product_id)
        db.session.add(new_wishlist_item)
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return redirect(url_for('views.show_cart'))


@views.route('/wishlist')
def show_wishlist():
    wishlist_list = (
        db.session.query(Wishlist.id, Product.product_name, Product.current_price, Product.product_picture, Product.id.label("product_id"))
        .join(Product, Wishlist.product_id == Product.id)
        .all()
    )
    return render_template('wishlist.html', wishlist_items=wishlist_list)

@views.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    category = request.args.get('category', '').strip()
    brand = request.args.get('brand', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    color = request.args.get('color', '').strip()

    # Start query with all products
    search_query = Product.query.join(Brand)

    # Create a list for filters
    filters = []

    # ✅ If a color is selected first, show ALL products of that color (ignore other filters at first)
    if color:
        filters.append(Product.color.ilike(f"%{color}%"))

    # ✅ If other filters are applied after selecting a color, refine results
    if query:
        filters.append(
            (Product.product_name.ilike(f"%{query}%")) |
            (Product.category.ilike(f"%{query}%")) |
            (Product.description.ilike(f"%{query}%")) |
            (Brand.name.ilike(f"%{query}%")) |
            (Product.color.ilike(f"%{query}%"))  # ✅ Added Color to Search Query
        )

    if category:
        filters.append(Product.category.ilike(f"%{category}%"))

    if brand:
        filters.append(Brand.name.ilike(f"%{brand}%"))

    if min_price is not None and min_price > 0:
        filters.append(Product.current_price >= min_price)

    if max_price is not None and max_price > 0:
        filters.append(Product.current_price <= max_price)

    # Apply filters dynamically
    if filters:
        search_query = search_query.filter(*filters)

    # Get search results
    search_results = search_query.all()
    brands = Brand.query.all()  # Fetch all brands for filter dropdown
    colors = db.session.query(Product.color).distinct().all()  # Fetch unique colors

    return render_template(
        'search_results.html',
        products=search_results,
        query=query,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        color=color,
        brands=brands,
        colors=[c[0] for c in colors]
    )

@views.route('/category/<string:category_name>')
def category_page(category_name):
    category_products = Product.query.filter_by(category=category_name).all()
    return render_template('category.html', category=category_name, products=category_products)

