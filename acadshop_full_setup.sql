-- =============================================
-- ACADSHOP - CRIAÇÃO COMPLETA DO BANCO DE DADOS
-- Baseado em: models.py + seed.py
-- Banco: PostgreSQL
-- =============================================

-- Remover banco se existir (opcional, use com cuidado)
-- DROP DATABASE IF EXISTS acadshop_db;
-- CREATE DATABASE acadshop_db WITH ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C' TEMPLATE template0;

-- Conectar ao banco: \c acadshop_db

-- =============================================
-- 1. CRIAÇÃO DAS TABELAS
-- =============================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(600),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    profile_picture VARCHAR(200),
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    image VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    short_description VARCHAR(300),
    price NUMERIC(10,2) NOT NULL,
    old_price NUMERIC(10,2),
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    image VARCHAR(200),
    images TEXT,
    stock INTEGER DEFAULT 0,
    stock_sizes TEXT, -- JSON string
    sizes VARCHAR(100),
    colors VARCHAR(100),
    brand VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_new BOOLEAN DEFAULT FALSE,
    rating NUMERIC(3,1) DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_one_not_null CHECK (
        user_id IS NOT NULL OR session_id IS NOT NULL
    ),
    UNIQUE(user_id),
    UNIQUE(session_id)
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1 CHECK (quantity >= 1),
    size VARCHAR(20),
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);

-- =============================================
-- 2. DADOS INICIAIS (SEED)
-- =============================================

-- Usuário Admin
INSERT INTO users (username, email, password_hash, is_admin, created_at)
VALUES (
    'admin',
    'admin@acadshop.com',
    '$pbkdf2-sha256$30000$...admin123...', -- Senha: admin123 (gerada com generate_password_hash)
    TRUE,
    CURRENT_TIMESTAMP
) ON CONFLICT (username) DO NOTHING;

-- Categorias
INSERT INTO categories (name, slug, description, image, is_active, created_at) VALUES
('Camisetas', 'camisetas', 'Camisetas de algodão e estampas exclusivas', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', TRUE, CURRENT_TIMESTAMP),
('Calças', 'calcas', 'Calças jeans, moletom e social', 'https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', TRUE, CURRENT_TIMESTAMP),
('Casacos', 'casacos', 'Casacos e jaquetas para todas as estações', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', TRUE, CURRENT_TIMESTAMP),
('Acessórios', 'acessorios', 'Acessórios fashion e utilitários', 'https://images.unsplash.com/photo-1549499093-8e749c2d21b6?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', TRUE, CURRENT_TIMESTAMP),
('Calçados', 'calcados', 'Tênis, sapatos e sandálias', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', TRUE, CURRENT_TIMESTAMP),
('Chuteiras', 'chuteiras', 'Chuteiras de alta performance para diversos esportes', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80', TRUE, CURRENT_TIMESTAMP)
ON CONFLICT (slug) DO NOTHING;

-- Produtos (com JSON em stock_sizes)
INSERT INTO products (
    name, slug, description, short_description, price, old_price, category_id,
    image, images, stock, stock_sizes, sizes, colors, brand,
    is_active, is_featured, is_new, rating, review_count, created_at, updated_at
) VALUES
(
    'Camiseta Premium Algodão', 'camiseta-premium-algodao',
    'Camiseta de alta qualidade, ideal para o dia a dia.',
    'Camiseta 100% algodão egípcio, conforto superior',
    89.90, 129.90,
    (SELECT id FROM categories WHERE slug = 'camisetas'),
    'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0,
    '{"P": 10, "M": 15, "G": 8, "GG": 5}',
    NULL, 'Preto,Branco,Cinza', 'AcadWear',
    TRUE, TRUE, TRUE, 4.8, 152, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Camiseta Básica Branca', 'camiseta-basica-branca',
    'Camiseta básica de algodão, perfeita para combinar.',
    'Camiseta básica branca, essencial no guarda-roupa',
    49.90, NULL,
    (SELECT id FROM categories WHERE slug = 'camisetas'),
    'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    'P,M,G,GG', 'Branco', 'BasicWear',
    TRUE, FALSE, FALSE, 4.5, 98, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Jeans Slim Fit', 'jeans-slim-fit',
    'Jeans confortável com ajuste perfeito.',
    'Jeans de corte slim, material stretch',
    159.90, 199.90,
    (SELECT id FROM categories WHERE slug = 'calcas'),
    'https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    '38,40,42,44', 'Azul Escuro,Azul Claro,Preto', 'DenimCo',
    TRUE, TRUE, FALSE, 4.6, 89, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Calça Moletom Comfort', 'calca-moletom-comfort',
    'Calça moletom macia e confortável.',
    'Calça moletom confortável para o dia a dia',
    119.90, NULL,
    (SELECT id FROM categories WHERE slug = 'calcas'),
    'https://images.unsplash.com/photo-1542272604-787c3835535d?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    'P,M,G,GG', 'Preto,Cinza,Azul', 'ComfortWear',
    TRUE, FALSE, FALSE, 4.4, 76, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Casaco Impermeável', 'casaco-impermeavel',
    'Casaco resistente à água, perfeito para todas as estações.',
    'Casaco impermeável com capuz, ideal para chuva',
    299.90, NULL,
    (SELECT id FROM categories WHERE slug = 'casacos'),
    'https://images.unsplash.com/photo-1551028719-00167b16eac5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    'P,M,G,GG', 'Verde,Preto,Azul', 'OutdoorPro',
    TRUE, TRUE, TRUE, 4.9, 203, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Jaqueta Jeans Clássica', 'jaqueta-jeans-classica',
    'Jaqueta jeans tradicional, combina com tudo.',
    'Jaqueta jeans clássica, peça versátil',
    189.90, NULL,
    (SELECT id FROM categories WHERE slug = 'casacos'),
    'https://images.unsplash.com/photo-1551028719-00167b16eac5?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    'P,M,G,GG', 'Azul Escuro,Azul Claro', 'DenimCo',
    TRUE, FALSE, FALSE, 4.7, 134, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Tênis Casual', 'tenis-casual',
    'Tênis versátil para uso diário.',
    'Tênis casual confortável para o dia a dia',
    229.90, 279.90,
    (SELECT id FROM categories WHERE slug = 'calcados'),
    'https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    '36,38,40,42,44', 'Branco,Preto,Azul', 'StepEasy',
    TRUE, TRUE, FALSE, 4.7, 167, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Sandália Conforto', 'sandalia-conforto',
    'Sandália leve e confortável.',
    'Sandália confortável para o verão',
    79.90, NULL,
    (SELECT id FROM categories WHERE slug = 'calcados'),
    'https://images.unsplash.com/photo-1542291026-7eec264c27ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    '36,38,40,42', 'Preto,Marrom,Bege', 'SummerFeet',
    TRUE, FALSE, FALSE, 4.3, 45, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Bolsa Crossbody', 'bolsa-crossbody',
    'Bolsa crossbody com design moderno.',
    'Bolsa crossbody elegante e prática',
    149.90, NULL,
    (SELECT id FROM categories WHERE slug = 'acessorios'),
    'https://images.unsplash.com/photo-1549499093-8e749c2d21b6?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    'Único', 'Preto,Marrom,Vermelho', 'BagStyle',
    TRUE, FALSE, TRUE, 4.8, 112, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    'Relógio Analógico', 'relogio-analogico',
    'Relógio analógico com design clássico.',
    'Relógio analógico elegante para o dia a dia',
    199.90, NULL,
    (SELECT id FROM categories WHERE slug = 'acessorios'),
    'https://images.unsplash.com/photo-1549499093-8e749c2d21b6?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
    NULL, 0, NULL,
    'Único', 'Preto,Prata,Dourado', 'TimeMaster',
    TRUE, FALSE, FALSE, 4.6, 89, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
)
ON CONFLICT (slug) DO NOTHING;

-- =============================================
-- 3. CONSULTAS DE VERIFICAÇÃO (opcional)
-- =============================================

-- SELECT 'Usuários' AS tabela, COUNT(*) FROM users
-- UNION ALL
-- SELECT 'Categorias', COUNT(*) FROM categories
-- UNION ALL
-- SELECT 'Produtos', COUNT(*) FROM products
-- UNION ALL
-- SELECT 'Carrinhos', COUNT(*) FROM carts
-- UNION ALL
-- SELECT 'Itens no Carrinho', COUNT(*) FROM cart_items;

-- =============================================
-- FIM DO SCRIPT
-- =============================================