# Implementação da API de Pagamento - Acadshop

## Tarefas Pendentes

### 1. Instalar Dependências
- [ ] Instalar Stripe SDK (`pip install stripe`)
- [ ] Instalar python-dotenv para variáveis de ambiente
- [ ] Criar arquivo .env com chaves do Stripe

### 2. Atualizar Modelos
- [ ] Modificar modelo Order para incluir campos de pagamento (stripe_payment_id, payment_status, etc.)
- [ ] Adicionar campos necessários no OrderItem se preciso

### 3. Criar Endpoints de API
- [ ] `/api/payment/create-intent` - Criar PaymentIntent do Stripe
- [ ] `/api/payment/confirm` - Confirmar pagamento
- [ ] `/api/payment/webhook` - Webhook para confirmações assíncronas
- [ ] Atualizar `/api/checkout` para incluir dados de pagamento

### 4. Modificar Frontend
- [ ] Atualizar checkout.html para incluir campos de cartão de crédito
- [ ] Integrar Stripe Elements para captura segura de dados
- [ ] Adicionar validação de formulário de pagamento
- [ ] Implementar JavaScript para processar pagamento

### 5. Configuração e Segurança
- [ ] Configurar chaves do Stripe (test mode inicialmente)
- [ ] Implementar validação de webhook signature
- [ ] Adicionar logs de transação
- [ ] Testar fluxo completo de pagamento

### 6. Testes e Validação
- [ ] Testar pagamentos com cartões de teste do Stripe
- [ ] Verificar tratamento de erros
- [ ] Testar webhooks
- [ ] Validar atualização de status dos pedidos
