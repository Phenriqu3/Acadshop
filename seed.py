from werkzeug.security import generate_password_hash
from models import db, User, Category, Product

def seed_database():
    """Seed the database with initial data"""
    if not User.query.first():
        user = User(
            username='admin',
            email='admin@acadshop.com',
            password_hash=generate_password_hash('admin'),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        print("✅ Admin user created")

    if not Category.query.first():
        categories = [
            Category(name='Camisetas', slug='camisetas', description='Camisetas de algodão e estampas exclusivas', image='https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Category(name='Calças', slug='calcas', description='Calças jeans, moletom e social', image='https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Category(name='Casacos', slug='casacos', description='Casacos e jaquetas para todas as estações', image='https://images.unsplash.com/photo-1551028719-00167b16eac5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Category(name='Acessórios', slug='acessorios', description='Acessórios fashion e utilitários', image='https://images.unsplash.com/photo-1549499093-8e749c2d21b6?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Category(name='Calçados', slug='calcados', description='Tênis, sapatos e sandálias', image='https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80'),
            Category(name='Chuteiras', slug='chuteiras', description='Chuteiras de alta performance para diversos esportes', image='https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80')
        ]
        for category in categories:
            db.session.add(category)
        db.session.commit()

    # Não adicionar produtos de exemplo - manter apenas os produtos existentes do usuário
    print("✅ Database seeded with categories only (preserving existing products)")
