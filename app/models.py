from app import db

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    addresses = db.relationship('Address', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

# Address Model
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address_line = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Address {self.address_line}, {self.city}>"

# Brand Model
class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    logo = db.Column(db.String(200), nullable=True)
    products = db.relationship('Product', backref='brand', lazy=True)

    def __repr__(self):
        return f"<Brand {self.name}>"

# ✅ Updated Product Model (Now Uses String-Based Category)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    product_picture = db.Column(db.String(200), nullable=False)
    color = db.Column(db.String(15))
    rating = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    sale = db.Column(db.Boolean, default=True)
    size_small = db.Column(db.Integer, default=0)
    size_medium = db.Column(db.Integer, default=0)
    size_large = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=0)

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # ✅ Now category is a string field

    carts = db.relationship('Cart', backref='cart_product', lazy=True, cascade="all, delete-orphan")
    wishlists = db.relationship('Wishlist', backref='wishlist_product', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.product_name}, Price: {self.current_price}, Category: {self.category}>"

# Cart Model
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Cart Item: {self.product_id}, Quantity: {self.quantity}>"

# Wishlist Model
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Wishlist Item: {self.product_id}>"
