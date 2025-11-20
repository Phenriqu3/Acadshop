from flask import Blueprint, jsonify
from flask_login import login_required
from models import db, User, Category, Product, Cart, CartItem
from sqlalchemy import inspect
from utils import get_products, get_or_create_cart, get_cart_data

api = Blueprint('api', __name__)

@api.route('/health')
def health_check():
    return jsonify({'status': 'OK', 'message': 'AcadShop API está funcionando!'})

@api.route('/db/health')
def db_health_check():
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        expected_tables = ['users', 'categories', 'products', 'carts', 'cart_items']

        missing_tables = [table for table in expected_tables if table not in tables]

        if missing_tables:
            return jsonify({
                'status': 'ERROR',
                'message': f'Tabelas faltando: {missing_tables}',
                'tables': tables
            }), 500

        user_count = User.query.count()
        category_count = Category.query.count()
        product_count = Product.query.count()

        return jsonify({
            'status': 'OK',
            'message': 'Banco de dados saudável',
            'tables': tables,
            'data_counts': {
                'users': user_count,
                'categories': category_count,
                'products': product_count
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': f'Erro na verificação do banco: {str(e)}'
        }), 500

@api.route('/products')
def api_products():
    return jsonify(get_products())

@api.route('/categories')
def api_categories():
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify([c.to_dict() for c in categories])

@api.route('/cart', methods=['GET'])
def api_get_cart():
    cart = get_or_create_cart()
    cart_data = get_cart_data(cart)
    cart_data['session_id'] = cart.session_id if cart.session_id else None
    return jsonify(cart_data)

@api.route('/cart/add', methods=['POST'])
@login_required
def api_add_to_cart():
    from flask import request
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    size = data.get('size')
    color = data.get('color')

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Verificar estoque se tamanho foi especificado
    if size:
        stock_sizes = product.get_stock_sizes()
        if size in stock_sizes:
            available_stock = stock_sizes[size]
            if available_stock <= 0:
                return jsonify({'error': f'Tamanho {size} está esgotado'}), 400
            # Verificar se quantidade solicitada está disponível
            if quantity > available_stock:
                return jsonify({'error': f'Apenas {available_stock} unidades disponíveis para o tamanho {size}'}), 400

    cart = get_or_create_cart()

    # Verificar se item já existe no carrinho
    existing_item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id,
        size=size,
        color=color
    ).first()

    if existing_item:
        new_quantity = existing_item.quantity + quantity
        # Verificar estoque total se tamanho foi especificado
        if size:
            stock_sizes = product.get_stock_sizes()
            if size in stock_sizes:
                available_stock = stock_sizes[size]
                if new_quantity > available_stock:
                    return jsonify({'error': f'Apenas {available_stock} unidades disponíveis para o tamanho {size}'}), 400
        existing_item.quantity = new_quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            size=size,
            color=color
        )
        db.session.add(new_item)

    db.session.commit()

    cart_data = get_cart_data(cart)
    return jsonify(cart_data)

@api.route('/cart/update', methods=['POST'])
@login_required
def api_update_cart():
    from flask import request
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)

    if not item_id:
        return jsonify({'error': 'Item ID is required'}), 400

    cart = get_or_create_cart()
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()

    if not item:
        return jsonify({'error': 'Item not found'}), 404

    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity

    db.session.commit()

    cart_data = get_cart_data(cart)
    return jsonify(cart_data)

@api.route('/cart/remove', methods=['POST'])
@login_required
def api_remove_from_cart():
    from flask import request
    data = request.get_json()
    item_id = data.get('item_id')

    if not item_id:
        return jsonify({'error': 'Item ID is required'}), 400

    cart = get_or_create_cart()
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()

    if not item:
        return jsonify({'error': 'Item not found'}), 404

    db.session.delete(item)
    db.session.commit()

    cart_data = get_cart_data(cart)
    return jsonify(cart_data)
