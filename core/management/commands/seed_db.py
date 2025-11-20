from django.core.management.base import BaseCommand
from core.models import Category, Product

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            {'name': 'Camisetas', 'slug': 'camisetas', 'description': 'Camisetas de algodão e estampas exclusivas'},
            {'name': 'Calças', 'slug': 'calcas', 'description': 'Calças jeans, moletom e social'},
            {'name': 'Casacos', 'slug': 'casacos', 'description': 'Casacos e jaquetas para todas as estações'},
            {'name': 'Acessórios', 'slug': 'acessorios', 'description': 'Acessórios fashion e utilitários'},
            {'name': 'Calçados', 'slug': 'calcados', 'description': 'Tênis, sapatos e sandálias'}
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create products
        products_data = [
            {
                'name': 'Camiseta Premium Algodão',
                'slug': 'camiseta-premium-algodao',
                'price': 89.90,
                'old_price': 129.90,
                'short_description': 'Camiseta 100% algodão egípcio, conforto superior',
                'description': 'Camiseta de alta qualidade, ideal para o dia a dia.',
                'category_slug': 'camisetas',
                'sizes': 'P,M,G,GG',
                'colors': 'Preto,Branco,Cinza',
                'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab',
                'is_featured': True,
                'is_new': True
            },
            {
                'name': 'Camiseta Básica Branca',
                'slug': 'camiseta-basica-branca',
                'price': 49.90,
                'short_description': 'Camiseta básica branca, essencial no guarda-roupa',
                'description': 'Camiseta básica de algodão, perfeita para combinar.',
                'category_slug': 'camisetas',
                'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab',
                'is_featured': False,
                'is_new': False
            },
            {
                'name': 'Jeans Slim Fit',
                'slug': 'jeans-slim-fit',
                'price': 159.90,
                'old_price': 199.90,
                'short_description': 'Jeans de corte slim, material stretch',
                'description': 'Jeans confortável com ajuste perfeito.',
                'category_slug': 'calcas',
                'image': 'https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'is_featured': True
            },
            {
                'name': 'Calça Moletom Comfort',
                'slug': 'calca-moletom-comfort',
                'price': 119.90,
                'short_description': 'Calça moletom confortável para o dia a dia',
                'description': 'Calça moletom macia e confortável.',
                'category_slug': 'calcas',
                'image': 'https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'is_featured': False,
                'is_new': False
            },
            {
                'name': 'Casaco Impermeável',
                'slug': 'casaco-impermeavel',
                'price': 299.90,
                'short_description': 'Casaco impermeável com capuz, ideal para chuva',
                'description': 'Casaco resistente à água, perfeito para todas as estações.',
                'category_slug': 'casacos',
                'image': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'is_featured': True,
                'is_new': True
            },
            {
                'name': 'Jaqueta Jeans Clássica',
                'slug': 'jaqueta-jeans-classica',
                'price': 189.90,
                'short_description': 'Jaqueta jeans clássica, peça versátil',
                'description': 'Jaqueta jeans tradicional, combina com tudo.',
                'category_slug': 'casacos',
                'image': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'is_featured': False,
                'is_new': False
            },
            {
                'name': 'Tênis Casual',
                'slug': 'tenis-casual',
                'price': 229.90,
                'old_price': 279.90,
                'short_description': 'Tênis casual confortável para o dia a dia',
                'description': 'Tênis versátil para uso diário.',
                'category_slug': 'calcados',
                'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'is_featured': True
            },
            {
                'name': 'Sandália Conforto',
                'slug': 'sandalia-conforto',
                'price': 79.90,
                'short_description': 'Sandália confortável para o verão',
                'description': 'Sandália leve e confortável.',
                'category_slug': 'calcados',
                'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'is_featured': False,
                'is_new': False
            },
            {
                'name': 'Bolsa Crossbody',
                'slug': 'bolsa-crossbody',
                'price': 149.90,
                'short_description': 'Bolsa crossbody elegante e prática',
                'description': 'Bolsa crossbody com design moderno.',
                'category_slug': 'acessorios',
                'image': 'https://images.unsplash.com/photo-1549499093-8e749c2d21b6?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'is_featured': False,
                'is_new': True
            },
            {
                'name': 'Relógio Analógico',
                'slug': 'relogio-analogico',
                'price': 199.90,
                'short_description': 'Relógio analógico elegante para o dia a dia',
                'description': 'Relógio analógico com design clássico.',
                'category_slug': 'acessorios',
                'image': 'https://images.unsplash.com/photo-1549499093-8e749c2d21b6?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
                'is_featured': False,
                'is_new': False
            }
        ]

        for prod_data in products_data:
            category = Category.objects.get(slug=prod_data['category_slug'])
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'name': prod_data['name'],
                    'description': prod_data['description'],
                    'short_description': prod_data['short_description'],
                    'price': prod_data['price'],
                    'old_price': prod_data.get('old_price'),
                    'category': category,
                    'sizes': prod_data.get('sizes', ''),
                    'colors': prod_data.get('colors', ''),
                    'image': prod_data['image'],
                    'is_featured': prod_data['is_featured'],
                    'is_new': prod_data.get('is_new', False)
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
