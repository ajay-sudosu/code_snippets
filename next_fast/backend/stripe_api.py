import stripe
from typing import Optional, List
from pydantic import BaseModel
from config import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


class SubscriptionItem(BaseModel):
    billing_thresholds: Optional[dict]
    metadata: Optional[dict]
    price: Optional[str]
    price_data: Optional[dict]
    quantity: Optional[int]
    tax_rates: Optional[List]


class Subscription(BaseModel):
    customer: str
    items: List[SubscriptionItem]
    cancel_at_period_end: Optional[bool]
    default_payment_method: Optional[str]
    metadata: Optional[dict]
    payment_behavior: Optional[str]


def create_subscription(data: Subscription):
    """Creates a new subscription on an existing customer.
    Each customer can have up to 500 active or scheduled subscriptions."""
    response = stripe.Subscription.create(
        customer=data.customer,
        items=data.items,
        cancel_at_period_end=data.cancel_at_period_end,
        default_payment_method=data.default_payment_method,
        metadata=data.metadata,
        payment_behavior=data.payment_behavior
    )

    return response


def get_subscription(subscription_id: str):
    """Retrieves the subscription with the given ID."""
    response = stripe.Subscription.retrieve(subscription_id)

    return response


def list_subscriptions(customer_id: Optional[str] = None,
                       price: Optional[str] = None,
                       status: Optional[str] = 'all',
                       limit: Optional[int] = 10,):
    """By default, returns a list of subscriptions that have not been canceled.
    In order to list canceled subscriptions, specify status=canceled."""
    response = stripe.Subscription.list(
        customer=customer_id,
        price=price,
        status=status,
        limit=limit
    )

    return response


def cancel_subscription(subscription_id: str):
    """Cancels a customer’s subscription immediately.
    The customer will not be charged again for the subscription."""
    response = stripe.Subscription.delete(subscription_id)

    return response


def update_subscription(subscription_id, metadata={}):
    """Updates an existing subscription to match the specified parameters."""
    response = stripe.Subscription.modify(
        subscription_id,
        metadata=metadata,
    )

    return response


def pause_subscription(subscription_id):
    """Pause an existing subscription."""
    response = stripe.Subscription.modify(
        subscription_id,
        pause_collection={"behavior": "void"},
    )

    return response


def get_product(product_id: str):
    """Cancels a customer’s subscription immediately.
    The customer will not be charged again for the subscription."""
    response = stripe.Product.retrieve(product_id)

    return response


def fetch_payment_intent(payment_intent_id: str):
    """Retrieves the details of a PaymentIntent that has previously been created."""
    response = stripe.PaymentIntent.retrieve(
        payment_intent_id
    )

    return response


def stripe_create_a_charge(amount: int, customer_id: str, receipt_email: str, description: str = ''):
    """To charge a credit card or other payment source, you create a Charge object. If your API key is in test mode,
    the supplied payment source (e.g., card) won’t actually be charged, although everything else will occur as
    if in live mode. (Stripe assumes that the charge would have completed successfully)."""
    response = stripe.Charge.create(
        amount=100*amount,
        currency="usd",
        customer=customer_id,
        description=description,
        receipt_email=receipt_email
    )
    return response


def retrieve_customer_cards(customer_id: str):
    """Retrieves All the Customer's Card."""
    response = stripe.Customer.list_sources(
        customer_id,
        object="card",
        limit=100
    )
    return response


def update_customer_default_card(customer_id: str, token: str):
    """Update Customer's Default Card"""
    response = stripe.Customer.modify(
        customer_id,
        default_source=token
    )
    return response


def create_customer_card_on_stripe(customer_id: str, token: str):
    """Create Customer's Card"""
    response = stripe.Customer.create_source(
        customer_id,
        source=token
    )
    return response


def retrieve_customer_card_by_token(token: str):
    """Retrieve Customer's Card from token"""
    response = stripe.Token.retrieve(
        source=token
    )
    return response


if __name__ == '__main__':
    # res = stripe_create_a_charge(100, 'cus_M7p0bzoy5aA2Hg', 'tarique@joinnextmed.com', 'No Show charge')
    # print(res)
    pass
