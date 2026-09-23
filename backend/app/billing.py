import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

STRIPE_CHECKOUT_URL = 'https://api.stripe.com/v1/checkout/sessions'

def _price_id(plan: str) -> str:
    plan = (plan or 'monthly').strip().lower()
    if plan == 'monthly':
        return os.getenv('STRIPE_MONTHLY_PRICE_ID', '').strip() or os.getenv('STRIPE_PRICE_ID', '').strip()
    return ''

def checkout_configured(plan: str | None = None) -> bool:
    common = all(os.getenv(name, '').strip() for name in ('STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET', 'PUBLIC_APP_URL'))
    if not common:
        return False
    if plan and (plan or '').strip().lower() != 'monthly':
        return False
    return bool(_price_id('monthly'))

def checkout_options() -> dict:
    return {
        'checkout_configured': checkout_configured(),
        'monthly_available': checkout_configured('monthly'),
        'annual_available': False,
        'monthly_label': os.getenv('MEMBERSHIP_MONTHLY_LABEL', '$14.99 / month').strip() or '$14.99 / month',
    }

def create_checkout(user_id: int, email: str, plan: str = 'monthly') -> dict:
    plan = (plan or 'monthly').strip().lower()
    if plan != 'monthly':
        raise RuntimeError('Only the monthly subscription plan is available')
    secret = os.getenv('STRIPE_SECRET_KEY', '').strip()
    price = _price_id('monthly')
    base = os.getenv('PUBLIC_APP_URL', '').rstrip('/')
    if not secret or not price or not base.startswith('https://'):
        raise RuntimeError('Paid checkout is not configured for the monthly plan')
    data = urllib.parse.urlencode({
        'mode': 'subscription',
        'customer_email': email,
        'client_reference_id': str(user_id),
        'success_url': base + '/?membership=success&session_id={CHECKOUT_SESSION_ID}',
        'cancel_url': base + '/?membership=cancelled',
        'line_items[0][price]': price,
        'line_items[0][quantity]': '1',
        'subscription_data[metadata][user_id]': str(user_id),
        'metadata[user_id]': str(user_id),
        'metadata[plan]': 'monthly',
        'subscription_data[metadata][plan]': 'monthly',
        'allow_promotion_codes': 'true',
    }).encode()
    request = urllib.request.Request(STRIPE_CHECKOUT_URL, data=data, method='POST', headers={
        'Authorization': 'Bearer ' + secret,
        'Content-Type': 'application/x-www-form-urlencoded',
    })
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace')
        raise RuntimeError('Checkout provider rejected the request: ' + detail[:300]) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError('Checkout provider is temporarily unavailable') from exc
    if not str(result.get('url', '')).startswith('https://checkout.stripe.com/'):
        raise RuntimeError('Checkout provider returned an invalid redirect')
    return {'checkout_url': result['url'], 'session_id': result.get('id'), 'plan': 'monthly'}

def verify_webhook(payload: bytes, signature_header: str, tolerance_seconds: int = 300) -> dict:
    secret = os.getenv('STRIPE_WEBHOOK_SECRET', '').strip()
    if not secret:
        raise ValueError('Webhook is not configured')
    values: dict[str, list[str]] = {}
    for item in signature_header.split(','):
        if '=' not in item: continue
        key, value = item.split('=', 1)
        values.setdefault(key.strip(), []).append(value.strip())
    try:
        timestamp = int(values['t'][0])
    except (KeyError, ValueError, IndexError) as exc:
        raise ValueError('Invalid webhook signature') from exc
    if abs(int(time.time()) - timestamp) > tolerance_seconds:
        raise ValueError('Expired webhook signature')
    signed = str(timestamp).encode() + b'.' + payload
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, candidate) for candidate in values.get('v1', [])):
        raise ValueError('Invalid webhook signature')
    try:
        return json.loads(payload.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid webhook payload') from exc
