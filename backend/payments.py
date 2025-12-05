"""
Stripe payment processing for Listify credit purchases.
"""
import os
from typing import Dict, Optional
from datetime import datetime
import stripe
from dotenv import load_dotenv

load_dotenv()

# Initialize Stripe with secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Credit Package Definitions
CREDIT_PACKAGES = {
    "starter": {
        "name": "Starter Pack",
        "credits": 10,
        "price": 999,  # in cents ($9.99)
        "description": "Perfect for testing the platform"
    },
    "creator": {
        "name": "Creator Pack",
        "credits": 50,
        "price": 3999,  # in cents ($39.99)
        "description": "Great for regular users"
    },
    "business": {
        "name": "Business Pack",
        "credits": 200,
        "price": 12999,  # in cents ($129.99)
        "description": "Ideal for professional sellers"
    },
    "enterprise": {
        "name": "Enterprise Pack",
        "credits": 1000,
        "price": 49999,  # in cents ($499.99)
        "description": "Built for large operations"
    }
}


def create_checkout_session(package_id: str, user_id: str, user_email: str) -> Dict:
    """
    Create a Stripe Checkout session for credit purchase.
    
    Args:
        package_id: ID of the credit package (starter, creator, business, enterprise)
        user_id: User's ID from the database
        user_email: User's email address
        
    Returns:
        Dictionary with checkout session URL and session ID
    """
    if package_id not in CREDIT_PACKAGES:
        raise ValueError(f"Invalid package_id: {package_id}")
    
    package = CREDIT_PACKAGES[package_id]
    
    try:
        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': package['name'],
                        'description': f"{package['credits']} credits - {package['description']}",
                    },
                    'unit_amount': package['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{FRONTEND_URL}/credits/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/credits/cancel",
            customer_email=user_email,
            metadata={
                'user_id': user_id,
                'package_id': package_id,
                'credits': str(package['credits']),
            },
        )
        
        return {
            'url': session.url,
            'session_id': session.id
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")


def verify_webhook_signature(payload: bytes, signature: str) -> Dict:
    """
    Verify Stripe webhook signature and parse event.
    
    Args:
        payload: Raw request body
        signature: Stripe-Signature header value
        
    Returns:
        Parsed Stripe event
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError as e:
        raise ValueError(f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        raise ValueError(f"Invalid signature: {str(e)}")


def process_successful_payment(session: Dict) -> Dict:
    """
    Extract payment information from successful Stripe session.
    
    Args:
        session: Stripe checkout session object
        
    Returns:
        Dictionary with user_id, credits, and payment details
    """
    metadata = session.get('metadata', {})
    
    return {
        'user_id': metadata.get('user_id'),
        'package_id': metadata.get('package_id'),
        'credits': int(metadata.get('credits', 0)),
        'amount_paid': session.get('amount_total', 0) / 100,  # Convert cents to dollars
        'stripe_session_id': session.get('id'),
        'customer_email': session.get('customer_email'),
        'payment_status': session.get('payment_status'),
    }


def get_package_info(package_id: str) -> Optional[Dict]:
    """Get credit package information by ID."""
    return CREDIT_PACKAGES.get(package_id)


def get_all_packages() -> Dict:
    """Get all available credit packages."""
    return CREDIT_PACKAGES
