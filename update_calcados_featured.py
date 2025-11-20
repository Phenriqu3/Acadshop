from app import app, db
from models import Product, Category

def update_calcados_featured():
    with app.app_context():
        # Buscar categorias que devem ser automaticamente em destaque
        featured_categories = ['acessorios', 'calcados', 'chuteiras']

        for slug in featured_categories:
            category = Category.query.filter_by(slug=slug).first()
            if category:
                # Atualizar produtos desta categoria para serem em destaque
                products = Product.query.filter_by(category_id=category.id).all()
                for product in products:
                    if not product.is_featured:
                        product.is_featured = True
                        print(f"Produto '{product.name}' da categoria '{category.name}' marcado como em destaque.")
                db.session.commit()
                print(f"Categoria '{category.name}' processada.")
            else:
                print(f"Categoria '{slug}' não encontrada.")

if __name__ == '__main__':
    update_calcados_featured()
