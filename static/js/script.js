$(document).ready(function() {
    // Inicializar badge do carrinho na carga da página
    updateCartBadgeOnLoad();

    // Adicionar ao carrinho com AJAX
    $('.add-to-cart-form').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const button = form.find('button[type="submit"]');

        button.addClass('btn-loading');

        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            success: function(response) {
                // Atualizar contador do carrinho via API
                fetch('/api/cart')
                    .then(res => res.json())
                    .then(cartData => {
                        updateCartBadge(cartData.total_items || 0);
                    })
                    .catch(err => console.error('Erro ao atualizar badge:', err));

                // Mostrar mensagem de sucesso
                showAlert('Produto adicionado ao carrinho!', 'success');
            },
            error: function() {
                showAlert('Erro ao adicionar produto ao carrinho.', 'danger');
            },
            complete: function() {
                button.removeClass('btn-loading');
            }
        });
    });

    // Função para mostrar alertas
    function showAlert(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const alert = $('<div class="alert ' + alertClass + ' alert-dismissible fade show position-fixed top-0 end-0 m-3" style="z-index: 9999">' +
            message +
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
            '</div>');

        $('body').append(alert);

        setTimeout(function() {
            alert.alert('close');
        }, 3000);
    }

    // Validação de formulários
    $('form').on('submit', function() {
        const submitButton = $(this).find('button[type="submit"]');
        submitButton.prop('disabled', true).addClass('btn-loading');
    });

    // Tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Contador de produtos
    $('.quantity-input').on('change', function() {
        const input = $(this);
        const min = parseInt(input.attr('min')) || 1;
        const max = parseInt(input.attr('max')) || 999;
        let value = parseInt(input.val()) || min;

        if (value < min) value = min;
        if (value > max) value = max;

        input.val(value);
    });

    // Smooth scroll para âncoras
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $($(this).attr('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 80
            }, 1000);
        }
    });

    // Loading lazy para imagens
    $('img').on('load', function() {
        $(this).addClass('loaded');
    }).each(function() {
        if (this.complete) $(this).load();
    });

    // Função para abrir o carrinho lateral
    window.openCart = function() {
        // Buscar itens do carrinho e abrir side cart
        fetch('/api/cart')
            .then(response => response.json())
            .then(data => {
                const cartItemsDiv = document.getElementById('sideCartItems');
                cartItemsDiv.innerHTML = '';

                if (data.items && data.items.length > 0) {
                    data.items.forEach(item => {
                        const itemDiv = document.createElement('div');
                        itemDiv.className = 'side-cart-item';
                        itemDiv.innerHTML = `
                            <img src="${item.product.image || '/static/images/placeholder.jpg'}" alt="${item.product.name}" onerror="this.src='/static/images/placeholder.jpg'">
                            <div class="side-cart-item-details">
                                <div class="side-cart-item-title">${item.product.name}</div>
                                <div class="side-cart-item-description text-muted small">${item.product.short_description || item.product.description.substring(0, 50)}...</div>
                                <div class="side-cart-item-price">R$ ${(item.product.price * item.quantity).toFixed(2).replace('.', ',')}</div>
                                <small class="text-muted">Quantidade: ${item.quantity}</small>
                            </div>
                            <button class="side-cart-item-remove" onclick="removeFromCart(${item.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        `;
                        cartItemsDiv.appendChild(itemDiv);
                    });

                    // Atualizar total
                    const totalDiv = document.getElementById('sideCartTotal');
                    if (totalDiv) {
                        totalDiv.textContent = `Total: R$ ${(data.total || 0).toFixed(2).replace('.', ',')}`;
                    }
                } else {
                    cartItemsDiv.innerHTML = `
                        <div class="side-cart-empty">
                            <i class="fas fa-shopping-cart"></i>
                            <p>Seu carrinho está vazio</p>
                        </div>
                    `;
                }

                // Mostrar side cart
                openSideCart();
            })
            .catch(error => {
                console.error('Erro ao carregar carrinho:', error);
                alert('Erro ao carregar o carrinho.');
            });
    };

    // Função para abrir o side cart
    function openSideCart() {
        const sideCart = document.getElementById('sideCart');
        const overlay = document.getElementById('sideCartOverlay');

        sideCart.classList.add('open');
        overlay.classList.add('active');

        // Prevenir scroll do body
        document.body.style.overflow = 'hidden';
    }

    // Função para fechar o side cart
    window.closeSideCart = function() {
        const sideCart = document.getElementById('sideCart');
        const overlay = document.getElementById('sideCartOverlay');

        sideCart.classList.remove('open');
        overlay.classList.remove('active');

        // Restaurar scroll do body
        document.body.style.overflow = '';
    };

    // Fechar side cart ao clicar no overlay
    document.addEventListener('DOMContentLoaded', function() {
        const overlay = document.getElementById('sideCartOverlay');
        if (overlay) {
            overlay.addEventListener('click', closeSideCart);
        }
    });

    // Função para atualizar o badge do carrinho
    function updateCartBadge(count) {
        const badge = document.getElementById('cartBadge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    // Função para atualizar o badge do carrinho na carga da página
    function updateCartBadgeOnLoad() {
        fetch('/api/cart')
            .then(response => response.json())
            .then(data => {
                updateCartBadge(data.total_items || 0);
            })
            .catch(error => {
                console.error('Erro ao carregar badge do carrinho:', error);
            });
    }

    // Function to open cart sidebar
    window.openCartSidebar = function() {
        const sidebar = document.getElementById('cartSidebar');
        const overlay = document.getElementById('cartOverlay');
        if (sidebar && overlay) {
            sidebar.style.transform = 'translateX(0)';
            overlay.style.display = 'block';
            document.body.style.overflow = 'hidden';
            updateCartSidebar();
        }
    }

    // Function to close cart sidebar
    window.closeCartSidebar = function() {
        const sidebar = document.getElementById('cartSidebar');
        const overlay = document.getElementById('cartOverlay');
        if (sidebar && overlay) {
            sidebar.style.transform = 'translateX(100%)';
            overlay.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    // Function to update cart sidebar content
    function updateCartSidebar() {
        fetch('/api/cart')
            .then(response => response.json())
            .then(data => {
                const cartContent = document.getElementById('cartContent');
                const cartFooter = document.getElementById('cartFooter');
                const cartSubtotal = document.getElementById('cartSubtotal');
                const cartShipping = document.getElementById('cartShipping');
                const cartTotal = document.getElementById('cartTotal');

                if (data.items && data.items.length > 0) {
                    let itemsHtml = '';
                    data.items.forEach(item => {
                        itemsHtml += `
                            <div class="cart-item d-flex align-items-center mb-3 p-2 border rounded">
                                <img src="${item.product.image || 'https://via.placeholder.com/60x60?text=Produto'}" alt="${item.product.name}" class="me-3" style="width: 60px; height: 60px; object-fit: cover;">
                                <div class="flex-grow-1">
                                    <h6 class="mb-1">${item.product.name}</h6>
                                    <p class="mb-1 text-muted small">Tamanho: ${item.size || 'Único'} | Cor: ${item.color || 'Única'}</p>
                                    <div class="d-flex align-items-center">
                                        <button class="btn btn-sm btn-outline-secondary me-2" onclick="updateCartItem(${item.id}, ${item.quantity - 1})">-</button>
                                        <span class="me-2">${item.quantity}</span>
                                        <button class="btn btn-sm btn-outline-secondary me-2" onclick="updateCartItem(${item.id}, ${item.quantity + 1})">+</button>
                                        <button class="btn btn-sm btn-outline-danger ms-auto" onclick="removeCartItem(${item.id})">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="text-end ms-2">
                                    <strong>R$ ${(item.total_price).toFixed(2).replace('.', ',')}</strong>
                                </div>
                            </div>
                        `;
                    });
                    cartContent.innerHTML = itemsHtml;
                    cartFooter.style.display = 'block';

                    cartSubtotal.textContent = `R$ ${(data.subtotal).toFixed(2).replace('.', ',')}`;
                    cartShipping.textContent = `R$ ${(data.shipping).toFixed(2).replace('.', ',')}`;
                    cartTotal.textContent = `R$ ${(data.total).toFixed(2).replace('.', ',')}`;
                } else {
                    cartContent.innerHTML = `
                        <div class="text-center py-5">
                            <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                            <p class="text-muted">Seu carrinho está vazio</p>
                            <a href="/produtos" class="btn btn-primary">Continuar Comprando</a>
                        </div>
                    `;
                    cartFooter.style.display = 'none';
                }
            })
            .catch(error => console.error('Erro ao atualizar sidebar do carrinho:', error));
    }

    // Function to update cart item quantity
    window.updateCartItem = function(itemId, quantity) {
        if (quantity <= 0) {
            removeCartItem(itemId);
            return;
        }

        fetch('/api/cart/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: itemId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Erro: ' + data.error);
            } else {
                updateCartBadge(data.total_items || 0);
                updateCartSidebar();
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao atualizar item do carrinho');
        });
    }

    // Function to remove cart item
    window.removeCartItem = function(itemId) {
        fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: itemId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Erro: ' + data.error);
            } else {
                updateCartBadge(data.total_items || 0);
                updateCartSidebar();
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao remover item do carrinho');
        });
    }

    // Função para remover item do carrinho
    window.removeFromCart = function(itemId) {
        fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ item_id: itemId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Erro: ' + data.error);
            } else {
                // Recarregar o carrinho
                openCart();
            }
        })
        .catch(error => {
            console.error('Erro ao remover item:', error);
            alert('Erro ao remover item do carrinho.');
        });
    };
});
