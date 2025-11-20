from app import app, db
from models import Category

def add_chuteiras_category():
    with app.app_context():
        # Verificar se a categoria Chuteiras já existe
        chuteiras = Category.query.filter_by(slug='chuteiras').first()
        if not chuteiras:
            chuteiras = Category(
                name='Chuteiras',
                slug='chuteiras',
                description='Chuteiras de alta performance para diversos esportes'
            )
            db.session.add(chuteiras)
            db.session.commit()
            print("Categoria 'Chuteiras' adicionada com sucesso!")
        else:
            print("Categoria 'Chuteiras' já existe.")

        # Verificar se as outras categorias existem
        categories_to_check = [
            ('acessorios', 'Acessórios', 'Acessórios diversos para moda'),
            ('calcados', 'Calçados', 'Calçados diversos'),
            ('tenis', 'Tênis', 'Tênis esportivos e casuais')
        ]

        for slug, name, desc in categories_to_check:
            cat = Category.query.filter_by(slug=slug).first()
            if not cat:
                cat = Category(name=name, slug=slug, description=desc)
                db.session.add(cat)
                print(f"Categoria '{name}' adicionada.")
            else:
                print(f"Categoria '{name}' já existe.")

        db.session.commit()

if __name__ == '__main__':
    add_chuteiras_category()
