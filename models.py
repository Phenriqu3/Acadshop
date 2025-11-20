from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(600), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    profile_picture = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', lazy=True, cascade='all, delete-orphan')
    cart = db.relationship('Cart', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        try:
            return check_password_hash(self.password_hash, password)
        except ValueError:
            return False

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', back_populates='category', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'image': self.image,
            'is_active': self.is_active,
            'product_count': len(self.products) if self.products else 0
        }

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(300))
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image = db.Column(db.String(200))
    images = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)  
    stock_sizes = db.Column(db.Text)  
    sizes = db.Column(db.String(100))
    colors = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship('Category', back_populates='products')

    def get_stock_sizes(self):
        if self.stock_sizes:
            try:
                return json.loads(self.stock_sizes)
            except:
                return {}
        return {}

    def set_stock_sizes(self, stock_dict):
        self.stock_sizes = json.dumps(stock_dict)

    def get_total_stock(self):
        stock_sizes = self.get_stock_sizes()
        if stock_sizes:
            return sum(stock_sizes.values())
        return self.stock

    def get_stock_for_size(self, size):
        stock_sizes = self.get_stock_sizes()
        return stock_sizes.get(size, 0) if stock_sizes else self.stock

    def get_available_sizes(self):
        if self.category and self.category.slug == 'calcados':
            return ['36', '37', '38', '39', '40', '41', '42', '43', '44']
        else:
            return ['P', 'M', 'G', 'GG']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'short_description': self.short_description,
            'price': self.price,
            'old_price': self.old_price,
            'category': self.category.name if self.category else None,
            'image': self.image,
            'images': self.images.split(',') if self.images else [],
            'stock': self.get_total_stock(),  
            'stock_sizes': self.get_stock_sizes(),
            'sizes': self.get_available_sizes(),
            'colors': self.colors.split(',') if self.colors else [],
            'brand': self.brand,
            'is_featured': self.is_featured,
            'is_new': self.is_new,
            'rating': self.rating,
            'review_count': self.review_count
        }

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    size = db.Column(db.String(20))
    color = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='cart_items')

    @property
    def total_price(self):
        return self.product.price * self.quantity

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(50), default='credit_card')
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    stripe_payment_id = db.Column(db.String(100))  # PaymentIntent ID do Stripe
    stripe_payment_method_id = db.Column(db.String(100))  # PaymentMethod ID
    shipping_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def get_status_display(self):
        status_map = {
            'pending': 'Pendente',
            'processing': 'Processando',
            'shipped': 'Enviado',
            'delivered': 'Entregue',
            'cancelled': 'Cancelado'
        }
        return status_map.get(self.status, self.status)

    def get_payment_method_display(self):
        payment_map = {
            'credit_card': 'Cartão de Crédito',
            'debit_card': 'Cartão de Débito',
            'pix': 'PIX',
            'boleto': 'Boleto'
        }
        return payment_map.get(self.payment_method, self.payment_method)

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    size = db.Column(db.String(20))
    color = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='order_items')

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    comment = db.Column(db.Text)
    is_verified_purchase = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='reviews')
    product = db.relationship('Product', backref='reviews')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_review'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'is_verified_purchase': self.is_verified_purchase,
            'is_approved': self.is_approved,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': {
                'username': self.user.username,
                'full_name': self.user.full_name
            }
        }

class SiteReview(db.Model):
    __tablename__ = 'site_reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Allow anonymous reviews
    name = db.Column(db.String(100))  # For anonymous users
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)  # Auto-approve for now
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='site_reviews')

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'name': self.name or (self.user.full_name if self.user else 'Anônimo'),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_approved': self.is_approved
        }

class ReviewHelpfulVote(db.Model):
    __tablename__ = 'review_helpful_votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='helpful_votes')
    review = db.relationship('Review', backref='helpful_votes')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'review_id', name='unique_user_review_helpful'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'review_id': self.review_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Wishlist(db.Model):
    __tablename__ = 'wishlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='wishlist_items')
    product = db.relationship('Product', backref='wishlist_items')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_wishlist'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product': {
                'id': self.product.id,
                'name': self.product.name,
                'price': self.product.price,
                'image': self.product.image,
                'slug': self.product.slug
            }
        }
