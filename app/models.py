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
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(200), nullable=False)  # Store image path
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)

    # Define relationships with different backrefs
    carts = db.relationship('Cart', backref='cart_product', lazy=True, cascade="all, delete-orphan")
    wishlists = db.relationship('Wishlist', backref='wishlist_product', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}, Price: {self.price}>"

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