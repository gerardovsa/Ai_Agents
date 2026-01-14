"""
Stripe Payment API Implementation
Handles payments, subscriptions, invoices, and customer management
"""
import stripe
import os

class StripeTools:
    def __init__(self):
        """Initialize Stripe API"""
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    def create_payment_intent(self, amount, currency, **kwargs):
        """Create payment intent"""
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=kwargs.get('customer_id'),
            description=kwargs.get('description'),
            metadata=kwargs.get('metadata', {}),
            payment_method_types=kwargs.get('payment_method_types', ['card']),
            receipt_email=kwargs.get('receipt_email')
        )
    
    def confirm_payment(self, payment_intent_id, **kwargs):
        """Confirm payment intent"""
        return stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method=kwargs.get('payment_method'),
            return_url=kwargs.get('return_url')
        )
    
    def create_refund(self, payment_intent_id, **kwargs):
        """Create refund"""
        return stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=kwargs.get('amount'),
            reason=kwargs.get('reason'),
            metadata=kwargs.get('metadata', {})
        )
    
    def create_customer(self, email, **kwargs):
        """Create customer"""
        return stripe.Customer.create(
            email=email,
            name=kwargs.get('name'),
            phone=kwargs.get('phone'),
            description=kwargs.get('description'),
            metadata=kwargs.get('metadata', {}),
            payment_method=kwargs.get('payment_method')
        )
    
    def get_customer(self, customer_id, **kwargs):
        """Get customer details"""
        return stripe.Customer.retrieve(customer_id)
    
    def update_customer(self, customer_id, **kwargs):
        """Update customer"""
        return stripe.Customer.modify(
            customer_id,
            email=kwargs.get('email'),
            name=kwargs.get('name'),
            phone=kwargs.get('phone'),
            metadata=kwargs.get('metadata')
        )
    
    def create_subscription(self, customer_id, items, **kwargs):
        """Create subscription"""
        return stripe.Subscription.create(
            customer=customer_id,
            items=items,
            trial_period_days=kwargs.get('trial_period_days'),
            metadata=kwargs.get('metadata', {}),
            proration_behavior=kwargs.get('proration_behavior', 'create_prorations')
        )
    
    def create_invoice(self, customer_id, **kwargs):
        """Create invoice"""
        return stripe.Invoice.create(
            customer=customer_id,
            description=kwargs.get('description'),
            auto_advance=kwargs.get('auto_advance', True),
            collection_method=kwargs.get('collection_method', 'charge_automatically'),
            metadata=kwargs.get('metadata', {})
        )
    
    def list_payment_methods(self, customer_id, type='card', **kwargs):
        """List customer payment methods"""
        return stripe.PaymentMethod.list(
            customer=customer_id,
            type=type
        )

# Export tool functions
def stripe_create_payment_intent(**kwargs):
    tools = StripeTools()
    return tools.create_payment_intent(**kwargs)

def stripe_confirm_payment(**kwargs):
    tools = StripeTools()
    return tools.confirm_payment(**kwargs)

def stripe_create_refund(**kwargs):
    tools = StripeTools()
    return tools.create_refund(**kwargs)

def stripe_create_customer(**kwargs):
    tools = StripeTools()
    return tools.create_customer(**kwargs)

def stripe_get_customer(**kwargs):
    tools = StripeTools()
    return tools.get_customer(**kwargs)

def stripe_update_customer(**kwargs):
    tools = StripeTools()
    return tools.update_customer(**kwargs)

def stripe_create_subscription(**kwargs):
    tools = StripeTools()
    return tools.create_subscription(**kwargs)

def stripe_create_invoice(**kwargs):
    tools = StripeTools()
    return tools.create_invoice(**kwargs)
