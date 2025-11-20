from django import forms

class CheckoutForm(forms.Form):
    PAYMENT_METHODS = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('bank_slip', 'Boleto Bancário'),
    ]
    
    shipping_address = forms.CharField(
        label='Endereço de Entrega',
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Digite seu endereço completo'})
    )
    payment_method = forms.ChoiceField(
        label='Método de Pagamento',
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect
    )
    terms = forms.BooleanField(
        label='Aceito os termos e condições',
        error_messages={'required': 'Você deve aceitar os termos e condições'}
    )