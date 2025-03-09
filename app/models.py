from app import db

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    logo = db.Column(db.String(200), nullable=True)  # Path to brand logo image
    products = db.relationship('Product', backref='brand', lazy=True)  # Relationship with Product

    def __repr__(self):
        return f"<Brand {self.name}>"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    product_picture = db.Column(db.String(200), nullable=False)  # Store image path
    old_price = db.Column(db.Float, nullable=False)  # Renamed from previous_price
    color = db.Column(db.String(15))
    rating = db.Column(db.Integer, default=0)
    category = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    sale = db.Column(db.Boolean, default=True)
    size_small = db.Column(db.Integer, default=0)
    size_medium = db.Column(db.Integer, default=0)
    size_large = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=0)  # Newly added column ✅

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)

    # Define relationships with different backrefs
    carts = db.relationship('Cart', backref='cart_product', lazy=True, cascade="all, delete-orphan")
    wishlists = db.relationship('Wishlist', backref='wishlist_product', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.product_name}, Price: {self.current_price}>"

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Cart Item: {self.product_id}, Quantity: {self.quantity}>"

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Wishlist Item: {self.product_id}>"
