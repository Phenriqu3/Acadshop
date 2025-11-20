with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the user menu dropdown items
content = content.replace(
    '''                                <li><a class="dropdown-item py-3 px-4" href="{{ url_for('cart_page') }}">
                                    <i class="fas fa-shopping-cart me-3 text-primary"></i>Meu Carrinho
                                </a></li>
                                <li><a class="dropdown-item py-3 px-4" href="{{ url_for('checkout_page') }}">
                                    <i class="fas fa-credit-card me-3 text-success"></i>Finalizar Compra
                                </a></li>
                                <li><hr class="dropdown-divider"></li>''',
    '''                                <li><a class="dropdown-item py-3 px-4" href="{{ url_for('cart_page') }}">
                                    <i class="fas fa-shopping-cart me-3 text-primary"></i>Meu Carrinho
                                </a></li>
                                <li><a class="dropdown-item py-3 px-4" href="{{ url_for('checkout_page') }}">
                                    <i class="fas fa-credit-card me-3 text-success"></i>Finalizar Compra
                                </a></li>
                                <li><a class="dropdown-item py-3 px-4" href="{{ url_for('profile') }}">
                                    <i class="fas fa-user me-3 text-info"></i>Meu Perfil
                                </a></li>
                                <li><hr class="dropdown-divider"></li>'''
)

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Profile link added to navbar successfully')
