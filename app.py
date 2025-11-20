from flask import Flask, render_template, redirect, url_for, request, flash, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func, or_
import os
import uuid
import time
import webbrowser
import threading
import stripe
from dotenv import load_dotenv
from models import db, User, Category, Product, Cart, CartItem, Review, SiteReview, Order, OrderItem, ReviewHelpfulVote

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Custom Jinja2 filter for strftime
def strftime_filter(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

# --- Configuração do App ---
app = Flask(__name__)
# Use variáveis de ambiente quando disponível
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:290703@localhost:5432/acadshop_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecret')

# Register the custom strftime filter
app.jinja_env.filters['strftime'] = strftime_filter

db.init_app(app)

# --- Login manager ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

# --- Context processor ---
@app.context_processor
def inject_globals():
    try:
        categories = Category.query.filter_by(is_active=True).all()
    except Exception:
        categories = []
    return dict(current_user=current_user, categories=categories)

# --- Rotas de autenticação ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if User.query.filter_by(username=username).first():
            flash('Usuário já existe.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
        elif password != confirm_password:
            flash('As senhas não coincidem.', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

# --- Rotas principais ---
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # Calcular estatísticas para o hero
    total_products = Product.query.filter_by(is_active=True).count()
    total_clients = User.query.filter_by(is_admin=False, is_active=True).count()

    # Calcular avaliação média do site
    site_reviews = SiteReview.query.filter_by(is_approved=True).all()
    site_rating = 0
    if site_reviews:
        total_rating = sum(review.rating for review in site_reviews)
        site_rating = round(total_rating / len(site_reviews), 1)

    # Get featured products
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(9).all()

    new_products = Product.query.filter_by(is_new=True, is_active=True).limit(6).all()

    categories = Category.query.filter_by(is_active=True).all()

    # Add product count to each category
    for category in categories:
        category.product_count = Product.query.filter_by(category_id=category.id, is_active=True).count()

    return render_template('index.html',
                           featured_products=featured_products,
                           new_products=new_products,
                           categories=categories,
                           total_products=total_products,
                           total_clients=total_clients,
                           site_rating=site_rating)

@app.route('/produtos')
def products_page():
    search_query = request.args.get('search', '')
    category_slugs = request.args.get('categories', '')
    category_slug = request.args.get('category', '')
    sort_by = request.args.get('sort', '')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    slugs_list = []
    if category_slugs:
        slugs_list.extend([slug.strip() for slug in category_slugs.split(',') if slug.strip()])
    if category_slug:
        slugs_list.append(category_slug.strip())

    # Build query with filters
    query = Product.query.filter(Product.is_active == True)

    # Filter by categories if specified
    if slugs_list:
        # Get category IDs for the slugs
        category_ids = Category.query.filter(Category.slug.in_(slugs_list)).with_entities(Category.id).all()
        category_ids = [cid[0] for cid in category_ids]
        if category_ids:
            query = query.filter(Product.category_id.in_(category_ids))

    # Filter by search query (case-insensitive search in name, description, and category name)
    if search_query:
        search_term = f"%{search_query}%"
        query = query.join(Category, Product.category_id == Category.id).filter(or_(
            Product.name.ilike(search_term),
            Product.description.ilike(search_term),
            Category.name.ilike(search_term)
        ))

    # Filter by price range
    if min_price:
        try:
            min_price_val = float(min_price)
            query = query.filter(Product.price >= min_price_val)
        except ValueError:
            pass  # Ignore invalid min_price

    if max_price:
        try:
            max_price_val = float(max_price)
            query = query.filter(Product.price <= max_price_val)
        except ValueError:
            pass  # Ignore invalid max_price

    # Apply sorting
    if sort_by == 'name_asc':
        query = query.order_by(Product.name.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(Product.name.desc())
    elif sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:
        # Default sorting (newest first)
        query = query.order_by(Product.created_at.desc())

    products = query.all()
    categories = Category.query.all()

    # Add product count to each category
    for category in categories:
        category.product_count = Product.query.filter_by(category_id=category.id, is_active=True).count()

    return render_template('products.html', products=products, categories=categories, search_query=search_query, category_slugs_list=slugs_list, sort_by=sort_by, min_price=min_price, max_price=max_price)

@app.route('/produto/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()

    # Get reviews for this product
    reviews = Review.query.filter_by(product_id=product.id, is_approved=True).order_by(Review.created_at.desc()).all()

    # Use stored rating and review count from product model
    average_rating = product.rating or 0
    review_count = product.review_count or 0

    # Calculate rating distribution
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_distribution[review.rating] += 1

    return render_template('product_detail.html',
                           product=product,
                           related_products=related_products,
                           reviews=reviews,
                           average_rating=average_rating,
                           review_count=review_count,
                           rating_distribution=rating_distribution)

# --- Admin ---
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    products = Product.query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('admin_dashboard.html', products=products, categories=categories)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            flash('Login administrativo realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas ou usuário não é administrador.', 'error')

    return render_template('admin_login.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        admin_code = request.form.get('admin_code', '')

        # Verificar código de administrador (pode ser configurado)
        if admin_code != 'ADMIN2024':
            flash('Código de administrador inválido.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Usuário já existe.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
        elif password != confirm_password:
            flash('As senhas não coincidem.', 'error')
        else:
            user = User(username=username, email=email, is_admin=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Administrador cadastrado com sucesso! Faça login.', 'success')
            return redirect(url_for('admin_login'))

    return render_template('admin_register.html')

# --- Produtos/Admin utilitários (add/edit/delete) ---
@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        abort(403)

    categories = Category.query.all()

    if request.method == 'POST':
        try:
            # Validações básicas
            name = request.form.get('name', '').strip()
            price_str = request.form.get('price', '').strip()
            category_id_str = request.form.get('category_id', '').strip()

            if not name:
                flash('Nome do produto é obrigatório.', 'danger')
                return render_template('add_product.html', categories=categories)

            if not price_str:
                flash('Preço do produto é obrigatório.', 'danger')
                return render_template('add_product.html', categories=categories)

            try:
                price = float(price_str)
            except ValueError:
                flash('Preço deve ser um número válido.', 'danger')
                return render_template('add_product.html', categories=categories)

            if not category_id_str:
                flash('Categoria é obrigatória.', 'danger')
                return render_template('add_product.html', categories=categories)

            try:
                category_id = int(category_id_str)
            except ValueError:
                flash('Categoria inválida.', 'danger')
                return render_template('add_product.html', categories=categories)

            # Processar links de imagens
            image_urls = request.form.getlist('image_urls[]')
            image_urls = [url.strip() for url in image_urls if url.strip()]

            if image_urls:
                # Validar URLs (básico)
                for url in image_urls:
                    if not url.startswith(('http://', 'https://')):
                        flash('Todos os links devem começar com http:// ou https://', 'danger')
                        return render_template('add_product.html', categories=categories)

                images_str = ','.join(image_urls)
                main_image = image_urls[0]
            else:
                # Set default image if none provided
                images_str = 'uploads/default_product.jpg'
                main_image = 'uploads/default_product.jpg'

            # Gerar slug único
            base_slug = name.lower().replace(' ', '-').replace('/', '-')
            slug = base_slug
            counter = 1
            while Product.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Verificar se a categoria é uma das que devem ser automaticamente em destaque
            category = Category.query.get(category_id)
            auto_featured = category and category.slug in ['calcados', 'chuteiras']

            product = Product(
                name=name,
                slug=slug,
                description=request.form.get('description', ''),
                price=price,
                stock=int(request.form.get('stock', 0)),
                category_id=category_id,
                sizes=request.form.get('sizes', '').strip(),
                colors=request.form.get('colors', '').strip(),
                image=main_image,  # Main image
                images=images_str,  # All images
                is_featured='is_featured' in request.form or auto_featured,
                is_new='is_new' in request.form,
                created_at=datetime.now()
            )
            db.session.add(product)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar produto: {str(e)}', 'danger')

    return render_template('add_product.html', categories=categories)

@app.route('/admin/delete_product/<product_id>', methods=['GET', 'POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        abort(403)

    try:
        product_id = int(product_id)
    except ValueError:
        abort(404)

    product = Product.query.get_or_404(product_id)

    # Delete all cart items associated with this product first
    for cart_item in product.cart_items:
        db.session.delete(cart_item)

    # Delete all reviews associated with this product
    for review in product.reviews:
        db.session.delete(review)

    db.session.delete(product)
    db.session.commit()
    flash(f'🗑 Produto "{product.name}" foi removido com sucesso.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        abort(403)

    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        try:
            # Validações básicas
            name = request.form.get('name', '').strip()
            price_str = request.form.get('price', '').strip()
            category_id_str = request.form.get('category_id', '').strip()

            if not name:
                flash('Nome do produto é obrigatório.', 'danger')
                return render_template('edit_product.html', product=product, categories=categories)

            if not price_str:
                flash('Preço do produto é obrigatório.', 'danger')
                return render_template('edit_product.html', product=product, categories=categories)

            try:
                price = float(price_str)
            except ValueError:
                flash('Preço deve ser um número válido.', 'danger')
                return render_template('edit_product.html', product=product, categories=categories)

            if not category_id_str:
                flash('Categoria é obrigatória.', 'danger')
                return render_template('edit_product.html', product=product, categories=categories)

            try:
                category_id = int(category_id_str)
            except ValueError:
                flash('Categoria inválida.', 'danger')
                return render_template('edit_product.html', product=product, categories=categories)

            # Processar links de imagens
            image_urls = request.form.getlist('image_urls[]')
            image_urls = [url.strip() for url in image_urls if url.strip()]

            if image_urls:
                # Validar URLs (básico)
                for url in image_urls:
                    if not url.startswith(('http://', 'https://')):
                        flash('Todos os links devem começar com http:// ou https://', 'danger')
                        return render_template('edit_product.html', product=product, categories=categories)

                images_str = ','.join(image_urls)
                main_image = image_urls[0]
            else:
                # Manter imagens existentes se nenhum link foi fornecido
                images_str = product.images
                main_image = product.image

            # Gerar slug único se o nome mudou
            if product.name != name:
                base_slug = name.lower().replace(' ', '-').replace('/', '-')
                slug = base_slug
                counter = 1
                while Product.query.filter(Product.slug == slug, Product.id != product_id).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                product.slug = slug

            product.name = name
            product.description = request.form.get('description', '')
            product.price = price
            product.stock = int(request.form.get('stock', 0))
            product.category_id = category_id
            product.sizes = request.form.get('sizes', '').strip()
            product.colors = request.form.get('colors', '').strip()
            product.image = main_image  # Main image
            product.images = images_str  # All images
            product.is_featured = 'is_featured' in request.form
            product.is_new = 'is_new' in request.form

            db.session.commit()
            flash(f'✅ Produto "{product.name}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar produto: {str(e)}', 'danger')

    return render_template('edit_product.html', product=product, categories=categories)

# --- Carrinho ---
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

@app.route('/carrinho')
@login_required
def cart_page():
    cart = get_or_create_cart()
    items = []
    total_price = 0

    for ci in cart.items:
        if not ci.product:
            continue
        subtotal = ci.product.price * ci.quantity
        total_price += subtotal

        # Construir string de opções selecionadas
        selected_options = []
        if ci.size:
            selected_options.append(f"Tamanho: {ci.size}")
        if ci.color:
            selected_options.append(f"Cor: {ci.color}")
        selected_options_str = " | ".join(selected_options) if selected_options else None

        items.append({
            'id': ci.id,
            'name': ci.product.name,
            'description': ci.product.description,
            'price': ci.product.price,
            'quantity': ci.quantity,
            'image': ci.product.image,
            'subtotal': subtotal,
            'selected_options': selected_options_str
        })

    return render_template('cart.html', items=items, total_price=total_price)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle profile picture upload
        profile_picture_url = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    # Validate file size (50MB max)
                    file.seek(0, 2)
                    file_size = file.tell()
                    file.seek(0)
                    if file_size <= 50 * 1024 * 1024:
                        # Create uploads directory if it doesn't exist
                        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
                        os.makedirs(upload_dir, exist_ok=True)

                        # Generate unique filename
                        filename = f"profile_{current_user.id}_{uuid.uuid4().hex}.{file.filename.rsplit('.', 1)[1].lower()}"
                        file_path = os.path.join(upload_dir, filename)
                        file.save(file_path)

                        # Update user profile picture
                        current_user.profile_picture = f'uploads/{filename}'
                        profile_picture_url = url_for('static', filename=current_user.profile_picture)
                    else:
                        error_msg = 'Arquivo muito grande. Máximo 50MB.'
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({'success': False, 'error': error_msg})
                        flash(error_msg, 'error')
                        return redirect(url_for('profile'))
                else:
                    error_msg = 'Tipo de arquivo não permitido. Use PNG, JPG, JPEG, GIF ou WebP.'
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'error': error_msg})
                    flash(error_msg, 'error')
                    return redirect(url_for('profile'))

        # Handle other profile updates
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()

        if username and username != current_user.username:
            if User.query.filter(User.username == username, User.id != current_user.id).first():
                error_msg = 'Nome de usuário já está em uso.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('profile'))
            else:
                current_user.username = username

        if email and email != current_user.email:
            if User.query.filter(User.email == email, User.id != current_user.id).first():
                error_msg = 'Email já está em uso.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('profile'))
            else:
                current_user.email = email

        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone = phone

        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response = {'success': True, 'message': 'Perfil atualizado com sucesso!'}
            if profile_picture_url:
                response['profile_picture'] = profile_picture_url
            return jsonify(response)
        else:
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('profile'))

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)

@app.route('/checkout')
@login_required
def checkout_page():
    cart = get_or_create_cart()
    if not cart.items:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('cart_page'))

    items = []
    total_price = 0

    for ci in cart.items:
        if not ci.product:
            continue
        subtotal = ci.product.price * ci.quantity
        total_price += subtotal

        # Construir string de opções selecionadas
        selected_options = []
        if ci.size:
            selected_options.append(f"Tamanho: {ci.size}")
        if ci.color:
            selected_options.append(f"Cor: {ci.color}")
        selected_options_str = " | ".join(selected_options) if selected_options else None

        items.append({
            'id': ci.id,
            'name': ci.product.name,
            'description': ci.product.description,
            'price': ci.product.price,
            'quantity': ci.quantity,
            'image': ci.product.image,
            'subtotal': subtotal,
            'selected_options': selected_options_str
        })

    return render_template('checkout.html', items=items, total_price=total_price, stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY'))

@app.route('/api/payment/create-intent', methods=['POST'])
@login_required
def create_payment_intent():
    """Create a Stripe PaymentIntent for the current cart"""
    try:
        cart = get_or_create_cart()
        if not cart.items:
            return jsonify({'success': False, 'error': 'Carrinho vazio'})

        items, total_price = calculate_cart_totals(cart)
        shipping = 10.00  # Fixed shipping cost
        total_amount = int((total_price + shipping) * 100)  # Convert to cents

        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='brl',
            metadata={
                'user_id': current_user.id,
                'cart_id': cart.id
            }
        )

        return jsonify({
            'success': True,
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'amount': total_amount
        })

    except Exception as e:
        print(f"Error creating payment intent: {e}")
        return jsonify({'success': False, 'error': 'Erro ao criar intenção de pagamento'})

@app.route('/api/checkout', methods=['POST'])
@login_required
def api_checkout():
    data = request.get_json()
    payment_intent_id = data.get('payment_intent_id')
    shipping_data = data.get('shipping', {})

    if not payment_intent_id:
        return jsonify({'success': False, 'error': 'ID do pagamento é obrigatório'})

    try:
        # Retrieve the PaymentIntent to confirm it's succeeded
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status != 'succeeded':
            return jsonify({'success': False, 'error': 'Pagamento não foi processado com sucesso'})

        cart = get_or_create_cart()
        if not cart.items:
            return jsonify({'success': False, 'error': 'Carrinho vazio'})

        # Calculate totals
        items, subtotal = calculate_cart_totals(cart)
        shipping = 10.00
        total_amount = subtotal + shipping

        # Create the order
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            payment_method='credit_card',
            payment_status='paid',
            stripe_payment_id=intent.id,
            stripe_payment_method_id=intent.payment_method,
            shipping_address=f"{shipping_data.get('name', '')}, {shipping_data.get('address', '')}, {shipping_data.get('city', '')}, {shipping_data.get('state', '')}, {shipping_data.get('zip', '')}"
        )

        db.session.add(order)
        db.session.flush()  # Get order ID

        # Create order items
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price'],
                size=item.get('selected_options', '').split(' | ')[0].replace('Tamanho: ', '') if 'Tamanho:' in item.get('selected_options', '') else None,
                color=item.get('selected_options', '').split(' | ')[1].replace('Cor: ', '') if 'Cor:' in item.get('selected_options', '') and len(item.get('selected_options', '').split(' | ')) > 1 else None
            )
            db.session.add(order_item)

        # Clear the cart
        for item in cart.items:
            db.session.delete(item)

        db.session.commit()

        order_id = f"ORDER-{order.id}"

        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Pedido realizado com sucesso!'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error processing checkout: {e}")
        return jsonify({'success': False, 'error': 'Erro ao processar pedido'})

@app.route('/pedido/<order_id>')
@login_required
def order_success(order_id):
    return render_template('order_success.html', order_id=order_id)

def calculate_cart_totals(cart):
    items_data = []
    total_price = 0

    for ci in cart.items:
        if not ci.product:
            continue
        subtotal = ci.product.price * ci.quantity
        total_price += subtotal

        selected_options = []
        if ci.size:
            selected_options.append(f"Tamanho: {ci.size}")
        if ci.color:
            selected_options.append(f"Cor: {ci.color}")
        selected_options_str = " | ".join(selected_options) if selected_options else None

        items_data.append({
            'cart_item_id': ci.id,
            'product_id': ci.product.id,
            'name': ci.product.name,
            'price': ci.product.price,
            'quantity': ci.quantity,
            'image': ci.product.image,
            'subtotal': round(subtotal, 2),
            'selected_options': selected_options_str
        })

    return items_data, round(total_price, 2)

@app.route('/api/cart')
def get_cart():
    cart = get_or_create_cart()
    items, total_price = calculate_cart_totals(cart)
    total_items = sum(item['quantity'] for item in items)

    return jsonify({
        'items': items,
        'total_items': total_items,
        'total_price': total_price
    })

@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    size = data.get('size', '').strip()
    color = data.get('color', '').strip()

    if not product_id:
        return jsonify({'success': False, 'error': 'ID do produto é obrigatório'})

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Produto não encontrado'})

    if product.colors and not color:
        return jsonify({'success': False, 'error': 'Cor é obrigatória para este produto'})

    available_stock = 0
    if size and product.stock_sizes:
        available_stock = product.get_stock_for_size(size)
    else:
        available_stock = product.get_total_stock()

    cart = get_or_create_cart()
    query = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id)
    if size:
        query = query.filter_by(size=size)
    if color:
        query = query.filter_by(color=color)
    total_quantity_in_cart = sum(item.quantity for item in query.all())

    if total_quantity_in_cart + quantity > available_stock:
        return jsonify({
            'success': False,
            'error': f'Estoque insuficiente. Disponível: {available_stock - total_quantity_in_cart} unidades'
        })

    existing_item = query.first()
    if existing_item:
        existing_item.quantity += quantity
        cart_item = existing_item
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            size=size if size else None,
            color=color if color else None
        )
        db.session.add(cart_item)

    db.session.commit()

    items, total_price = calculate_cart_totals(cart)
    total_items = sum(item['quantity'] for item in items)

    return jsonify({
        'success': True,
        'message': 'Produto adicionado ao carrinho',
        'total_items': total_items,
        'total_price': total_price,
        'items': items
    })

@app.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    quantity = data.get('quantity', 1)

    if not cart_item_id:
        return jsonify({'success': False, 'error': 'ID do item do carrinho é obrigatório'})

    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item:
        return jsonify({'success': False, 'error': 'Item do carrinho não encontrado'})

    cart = get_or_create_cart()
    if cart_item.cart_id != cart.id:
        return jsonify({'success': False, 'error': 'Acesso negado'})

    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.session.commit()

    items, total_price = calculate_cart_totals(cart)
    total_items = sum(item['quantity'] for item in items)

    return jsonify({
        'success': True,
        'message': 'Carrinho atualizado',
        'total_items': total_items,
        'total_price': total_price,
        'items': items
    })

@app.route('/api/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')

    if not cart_item_id:
        return jsonify({'success': False, 'error': 'ID do item do carrinho é obrigatório'})

    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item:
        return jsonify({'success': False, 'error': 'Item do carrinho não encontrado'})

    cart = get_or_create_cart()
    if cart_item.cart_id != cart.id:
        return jsonify({'success': False, 'error': 'Acesso negado'})

    db.session.delete(cart_item)
    db.session.commit()

    items, total_price = calculate_cart_totals(cart)
    total_items = sum(item['quantity'] for item in items)

    return jsonify({
        'success': True,
        'message': 'Item removido',
        'total_items': total_items,
        'total_price': total_price,
        'items': items
    })

# --- Reviews API ---
@app.route('/api/reviews/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """Get all approved reviews for a product"""
    reviews = Review.query.filter_by(product_id=product_id, is_approved=True).order_by(Review.created_at.desc()).all()

    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'id': review.id,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'created_at': review.created_at.isoformat() if review.created_at else None,
            'user': {
                'username': review.user.username,
                'full_name': review.user.full_name
            },
            'helpful_count': review.helpful_count
        })

    return jsonify({
        'success': True,
        'reviews': reviews_data,
        'count': len(reviews_data)
    })



@app.route('/api/reviews/submit', methods=['POST'])
@login_required
def submit_review():
    data = request.get_json()
    product_id = data.get('product_id')
    rating = data.get('rating')
    title = data.get('title', '').strip()
    comment = data.get('comment', '').strip()

    if not product_id or not rating or not comment:
        return jsonify({'success': False, 'error': 'Dados obrigatórios faltando'})

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Avaliação deve ser entre 1 e 5'})
    except ValueError:
        return jsonify({'success': False, 'error': 'Avaliação inválida'})

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Produto não encontrado'})

    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_review:
        return jsonify({'success': False, 'error': 'Você já avaliou este produto'})

    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=rating,
        title=title,
        comment=comment,
        is_approved=True  # Auto-approve for now
    )

    db.session.add(review)

    # Update product rating and review count
    all_reviews = Review.query.filter_by(product_id=product_id, is_approved=True).all()
    total_rating = sum(r.rating for r in all_reviews) + rating
    review_count = len(all_reviews) + 1
    average_rating = total_rating / review_count

    product.rating = round(average_rating, 1)
    product.review_count = review_count

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Avaliação enviada com sucesso!',
        'new_rating': product.rating,
        'new_review_count': product.review_count
    })

@app.route('/api/reviews/<int:review_id>', methods=['PUT'])
@login_required
def edit_review(review_id):
    """Edit a review (user can edit their own review)"""
    review = Review.query.get_or_404(review_id)

    # Check if user owns this review or is admin
    if review.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'})

    data = request.get_json()
    rating = data.get('rating')
    title = data.get('title', '').strip()
    comment = data.get('comment', '').strip()

    if not rating or not comment:
        return jsonify({'success': False, 'error': 'Avaliação e comentário são obrigatórios'})

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Avaliação deve ser entre 1 e 5'})
    except ValueError:
        return jsonify({'success': False, 'error': 'Avaliação inválida'})

    # Store old rating for recalculation
    old_rating = review.rating

    # Update review
    review.rating = rating
    review.title = title
    review.comment = comment
    review.updated_at = datetime.utcnow()

    # Recalculate product rating and review count
    product = review.product
    all_reviews = Review.query.filter_by(product_id=product.id, is_approved=True).all()
    total_rating = sum(r.rating for r in all_reviews)
    review_count = len(all_reviews)
    average_rating = total_rating / review_count if review_count > 0 else 0

    product.rating = round(average_rating, 1)
    product.review_count = review_count

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Avaliação atualizada com sucesso!',
        'review': review.to_dict(),
        'new_rating': product.rating,
        'new_review_count': product.review_count
    })

@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review(review_id):
    """Delete a review (user can delete their own, admin can delete any)"""
    review = Review.query.get_or_404(review_id)

    # Check if user owns this review or is admin
    if review.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'})

    product = review.product

    # Delete helpful votes for this review
    ReviewHelpfulVote.query.filter_by(review_id=review_id).delete()

    # Delete the review
    db.session.delete(review)

    # Recalculate product rating and review count
    all_reviews = Review.query.filter_by(product_id=product.id, is_approved=True).all()
    if all_reviews:
        total_rating = sum(r.rating for r in all_reviews)
        review_count = len(all_reviews)
        average_rating = total_rating / review_count
        product.rating = round(average_rating, 1)
        product.review_count = review_count
    else:
        product.rating = 0
        product.review_count = 0

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Avaliação removida com sucesso!',
        'new_rating': product.rating,
        'new_review_count': product.review_count
    })

@app.route('/api/reviews/<int:review_id>/moderate', methods=['PUT'])
@login_required
def moderate_review(review_id):
    """Moderate a review (admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado - apenas administradores'})

    review = Review.query.get_or_404(review_id)

    data = request.get_json()
    is_approved = data.get('is_approved')

    if is_approved is None:
        return jsonify({'success': False, 'error': 'Campo is_approved é obrigatório'})

    review.is_approved = bool(is_approved)
    review.updated_at = datetime.utcnow()

    product = review.product

    # Recalculate product rating and review count based on approved reviews only
    all_reviews = Review.query.filter_by(product_id=product.id, is_approved=True).all()
    if all_reviews:
        total_rating = sum(r.rating for r in all_reviews)
        review_count = len(all_reviews)
        average_rating = total_rating / review_count
        product.rating = round(average_rating, 1)
        product.review_count = review_count
    else:
        product.rating = 0
        product.review_count = 0

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Avaliação {"aprovada" if is_approved else "reprovada"} com sucesso!',
        'review': review.to_dict(),
        'new_rating': product.rating,
        'new_review_count': product.review_count
    })

@app.route('/api/reviews/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    """Get all reviews by a specific user"""
    user = User.query.get_or_404(user_id)

    reviews = Review.query.filter_by(user_id=user_id).order_by(Review.created_at.desc()).all()

    reviews_data = []
    for review in reviews:
        review_data = review.to_dict()
        review_data['product'] = {
            'id': review.product.id,
            'name': review.product.name,
            'slug': review.product.slug,
            'image': review.product.image
        }
        reviews_data.append(review_data)

    return jsonify({
        'success': True,
        'reviews': reviews_data,
        'count': len(reviews_data),
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name
        }
    })

@app.route('/api/reviews/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_review_helpful(review_id):
    """Mark a review as helpful (prevent duplicate votes)"""
    review = Review.query.get_or_404(review_id)

    # Check if user already voted for this review
    existing_vote = ReviewHelpfulVote.query.filter_by(
        user_id=current_user.id,
        review_id=review_id
    ).first()

    if existing_vote:
        return jsonify({'success': False, 'error': 'Você já marcou esta avaliação como útil'})

    # Create new helpful vote
    vote = ReviewHelpfulVote(
        user_id=current_user.id,
        review_id=review_id
    )
    db.session.add(vote)

    # Increment helpful count
    review.helpful_count += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Avaliação marcada como útil!',
        'new_helpful_count': review.helpful_count
    })

@app.route('/newsletter_subscribe', methods=['POST'])
def newsletter_subscribe():
    """Handle newsletter subscription"""
    email = request.form.get('email', '').strip()

    if not email:
        flash('Email é obrigatório.', 'error')
        return redirect(url_for('index'))

    # Basic email validation
    if '@' not in email or '.' not in email:
        flash('Email inválido.', 'error')
        return redirect(url_for('index'))

    # Here you could save to database or external service
    # For now, just show success message
    flash('Obrigado por se inscrever! Você receberá nossas novidades em breve.', 'success')
    return redirect(url_for('index'))

# --- Inicialização do banco (cria admin e categorias iniciais) ---
def init_db():
    with app.app_context():
        try:
            db.create_all()

            # Cria admin padrão se não existir
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', email='admin@acadshop.com', is_admin=True)
                # senha padrão: admin123
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Usuário admin criado com senha 'admin123'")

            # Cria categorias iniciais se não existirem
            if not Category.query.first():
                categories = [
                    Category(name='Camisetas', slug='camisetas', description='Camisetas de alta qualidade'),
                    Category(name='Calças', slug='calcas', description='Calças jeans e sociais'),
                    Category(name='Casacos', slug='casacos', description='Casacos e jaquetas'),
                    Category(name='Tênis', slug='tenis', description='Tênis esportivos e casuais'),
                    Category(name='Acessórios', slug='acessorios', description='Acessórios diversos'),
                    Category(name='Chuteiras', slug='chuteiras', description='Chuteiras de alta performance para diversos esportes')
                ]
                db.session.add_all(categories)
                db.session.commit()
                print("Categorias iniciais criadas")

            # Cria avaliações de exemplo do site se não existirem
            if not SiteReview.query.first():
                sample_reviews = [
                    SiteReview(name='Maria Silva', rating=5, comment='Excelente qualidade e atendimento. Recomendo a todos!', is_approved=True),
                    SiteReview(name='João Santos', rating=4, comment='Produtos chegam rapidamente e com qualidade incrível.', is_approved=True),
                    SiteReview(name='Ana Costa', rating=5, comment='Variedade incrível e preços competitivos. Minha loja favorita!', is_approved=True),
                    SiteReview(name='Pedro Oliveira', rating=5, comment='Atendimento ao cliente excepcional. Sempre prontos para ajudar.', is_approved=True),
                    SiteReview(name='Carla Mendes', rating=4, comment='Produtos de alta qualidade e entrega super rápida!', is_approved=True),
                    SiteReview(name='Lucas Ferreira', rating=5, comment='A AcadShop superou minhas expectativas. Com certeza voltarei!', is_approved=True),
                    SiteReview(name='Juliana Lima', rating=4, comment='Ótima experiência de compra. Site fácil de navegar.', is_approved=True),
                    SiteReview(name='Roberto Alves', rating=5, comment='Qualidade premium e preços justos. Recomendo!', is_approved=True)
                ]
                db.session.add_all(sample_reviews)
                db.session.commit()
                print("Avaliações de exemplo do site criadas")
        except Exception as e:
            # Não travar a aplicação na inicialização caso o DB não esteja disponível
            print(f"[init_db] aviso: falha ao inicializar o DB: {e}")

# roda a inicialização de forma segura
init_db()

if __name__ == '__main__':
    print("🚀 AcadShop iniciado em http://127.0.0.1:5000")
    print("👤 Admin: admin / admin123")
    app.run(debug=True, port=5000)
