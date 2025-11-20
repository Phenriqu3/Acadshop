from flask import session
from flask_login import current_user
from models import db, User, Category, Product, Cart, CartItem
import uuid

def get_or_create_cart():
    """Obtém ou cria carrinho para usuário logado ou sessão"""
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
    else:
        session_id = session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['cart_session_id'] = session_id
        cart = Cart.query.filter_by(session_id=session_id).first()
        if not cart:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
    return cart

def get_products():
    products = Product.query.filter_by(is_active=True).all()
    return [p.to_dict() for p in products]

def get_cart_data(cart):
    """Retorna dados do carrinho formatados"""
    items = []
    subtotal = 0

    for item in cart.items:
        product_dict = item.product.to_dict()
        if item.product.short_description:
            product_dict['short_description'] = item.product.short_description
        elif item.product.description:
            product_dict['short_description'] = item.product.description[:50] + '...' if len(item.product.description) > 50 else item.product.description

        item_data = {
            'id': item.id,
            'product': product_dict,
            'quantity': item.quantity,
            'size': item.size,
            'color': item.color,
            'total_price': item.total_price
        }
        items.append(item_data)
        subtotal += item.total_price

    shipping = 15.90 if subtotal < 199 else 0
    total = subtotal + shipping

    return {
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'total_items': cart.total_items
    }
