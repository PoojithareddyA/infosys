from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, flash,json
from app.models import Product, Brand, Cart, Wishlist,User, Order, OrderItem
from app import db
import random,string

views = Blueprint('views', __name__)

@views.route('/')
def homepage():
    brands_list = Brand.query.all()
    return render_template('home.html', brands=brands_list)

@views.route('/brand/<int:brand_id>')
def brand_info(brand_id):
    brand_data = Brand.query.get_or_404(brand_id)
    brand_items = Product.query.filter_by(brand_id=brand_id).all()
    return render_template('brand_details.html', brand=brand_data, products=brand_items)

@views.route('/product/<int:product_id>')
def product_info(product_id):
    product_data = Product.query.get_or_404(product_id)
    return render_template('product_details.html', product=product_data)

@views.route('/category/<string:category_name>')
def products_by_category(category_name):
    products = Product.query.filter_by(category=category_name).all()
    return render_template('category.html', products=products, category_name=category_name)




@views.route('/cart')
def show_cart():
    cart = session.get("cart", {})  # Get cart or empty dict
    total_mrp = sum(item["price"] * item["quantity"] for item in cart.values())
    discount_mrp = int(total_mrp * 0.56)  # Apply 56% discount
    total_amount = int(total_mrp - discount_mrp)
    
    return render_template(
        'cart.html',
        cart_items=cart,
        total_mrp=total_mrp,
        discount_mrp=discount_mrp,
        total_amount=total_amount
    )

@views.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    cart = session.get("cart", {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]  # Remove item from cart

    session.modified = True
    return redirect(url_for('views.show_cart'))

@views.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def wishlist_add(product_id):
    product_data = Product.query.get_or_404(product_id)
    
    if "wishlist" not in session:
        session["wishlist"] = {}

    wishlist = session["wishlist"]

    if str(product_id) not in wishlist:
        wishlist[str(product_id)] = {
            "product_name": product_data.product_name,
            "price": product_data.current_price,
            "image": product_data.product_picture
        }

    session.modified = True
    return redirect(url_for('views.show_wishlist'))

@views.route('/wishlist')
def show_wishlist():
    wishlist = db.session.query(Product).join(Wishlist, Wishlist.product_id == Product.id).all()
    
    # Debugging
    for item in wishlist:
        print(f"Product ID: {item.id}")  # Make sure product_id exists
    
    return render_template('wishlist.html', wishlist_items=wishlist)



@views.route('/wishlist/remove/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    wishlist_item = Wishlist.query.filter_by(product_id=product_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
    return jsonify({'message': 'Removed from wishlist'}), 200




@views.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    category_name = request.args.get('category', '').strip()  # Fixed from category_id
    brand_id = request.args.get('brand_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    color = request.args.get('color', '').strip()

    search_query = Product.query
    filters = []

    if color:
        filters.append(Product.color.ilike(f"%{color}%"))
    if query:
        filters.append((Product.product_name.ilike(f"%{query}%")) | (Product.description.ilike(f"%{query}%")))
    if category_name:
        filters.append(Product.category.ilike(f"%{category_name}%"))  # Fixed filtering
    if brand_id:
        filters.append(Product.brand_id == brand_id)
    if min_price is not None:
        filters.append(Product.current_price >= min_price)
    if max_price is not None:
        filters.append(Product.current_price <= max_price)

    if filters:
        search_query = search_query.filter(*filters)

    search_results = search_query.all()
    
    # Ensure Category is imported
    from app.models import Category  

    categories = Category.query.all()
    brands = Brand.query.all()

    return render_template('search_results.html', products=search_results, categories=categories, brands=brands)




#

@views.route('/cart')
def cart_add():
    cart_items = session.get('cart', [])
    subtotal = sum(item['price'] for item in cart_items) if cart_items else 0
    shipping = 50 if subtotal > 0 else 0  # Example shipping cost
    tax = round(subtotal * 0.05, 2)  # 5% tax
    total = subtotal + shipping + tax

    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, tax=tax, total=total)

@views.route('/checkout')
def checkout():
    cart_items = session.get('cart', [])
    if not cart_items:
        return render_template('checkout.html', cart_items=[], subtotal=0, shipping=0, tax=0, total=0)

    subtotal = sum(item['price'] for item in cart_items)
    shipping = 50 if subtotal > 0 else 0
    tax = round(subtotal * 0.05, 2)
    total = subtotal + shipping + tax

    return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, tax=tax, total=total)

@views.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    cart = session.get('cart', [])

    # Check if product is already in cart
    for item in cart:
        if item['id'] == product.id:
            item['quantity'] += 1
            break
    else:
        cart.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': 1
        })

    session['cart'] = cart
    session.modified = True  # Ensures session updates

    return jsonify({'success': True, 'cart_count': len(cart)})

@views.route('/place_order', methods=['POST'])
def place_order():
    # Retrieve customer details from form
    address_line_1 = request.form.get('address_line_1')
    state = request.form.get('state')
    city = request.form.get('city')
    pincode = request.form.get('pincode')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')

    # Retrieve cart from session
    cart = session.get('cart', [])

    if not cart:
        flash('Your cart is empty!', 'danger')
        return redirect(url_for('views.checkout'))

    # Generate a guest order ID
    guest_order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Create a new order (without user_id)
    new_order = Order(
        customer_id=None,  # No user ID for guest
        customer_name=f"{firstname} {lastname}",
        address_line_1=address_line_1,
        state=state,
        city=city,
        pincode=pincode,
        price=0,
        status="Pending",
        mail=email,
        guest_order_id=guest_order_id  # Save guest ID to track order
    )
    db.session.add(new_order)
    db.session.commit()

    # Iterate over cart items and add to order
    for cart_item in cart:
        product = Product.query.get(cart_item['product_id'])
        if not product:
            flash(f"Product with ID {cart_item['product_id']} not found.", 'danger')
            continue

        total_cost = product.price * cart_item['quantity']
        new_order.price += total_cost

        order_item = OrderItem(
            OrderID=new_order.id,
            ProductID=cart_item['product_id'],
            UserID=None,  # No user ID for guest
            Quantity=cart_item['quantity'],
            Price=total_cost
        )
        db.session.add(order_item)

        # Reduce product stock
        product.stock_quantity -= cart_item['quantity']

    db.session.commit()

    # Clear cart session after order placement
    session.pop('cart', None)

    return jsonify({"success": True, "order_id": guest_order_id})


@views.route('/my_orders')
def my_orders():
    orders = Order.query.all()
    orders_with_items = []
    for order in orders:
        order_items = OrderItem.query.filter_by(OrderID=order.id).all()
        items_data = [{'name': item.product.name, 'quantity': item.Quantity} for item in order_items]

        orders_with_items.append({
            'id': order.id,
            'status': order.status,
            'price': order.price,
            'order_items': items_data
        })

    return render_template('my_orders.html', orders=orders_with_items)

@views.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Cancelled'
    
    order_items = OrderItem.query.filter_by(OrderID=order_id).all()
    for order_item in order_items:
        product = Product.query.get(order_item.ProductID)
        product.stock_quantity += order_item.Quantity

    db.session.commit()
    return redirect(url_for('views.my_orders'))

@views.route('/order/<int:order_id>')
def view_order_items(order_id):
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('views.my_orders'))
    
    order_items = OrderItem.query.filter_by(OrderID=order.id).all()
    return render_template('view_order_items.html', order=order, order_items=order_items)

@views.route('/order/<int:order_id>/remove_item/<int:item_id>', methods=['POST'])
def remove_order_item(order_id, item_id):
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('views.view_order_items', order_id=order_id))
    
    order_item = OrderItem.query.filter_by(OrderItemID=item_id, OrderID=order.id).first()
    if not order_item:
        flash("Item not found.", "danger")
        return redirect(url_for('views.view_order_items', order_id=order_id))
    
    product = Product.query.get(order_item.ProductID)
    if product:
        product.stock_quantity += order_item.Quantity
    
    db.session.delete(order_item)
    db.session.commit()

    if not OrderItem.query.filter_by(OrderID=order.id).all():
        db.session.delete(order)
        db.session.commit()
        return redirect(url_for('views.my_orders'))
    
    return redirect(url_for('views.view_order_items', order_id=order_id))









