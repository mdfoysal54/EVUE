from decimal import Decimal
import requests
from django.conf import settings

class GatewayError(Exception):
    pass

def config():
    store_id = getattr(settings, 'SSLCOMMERZ_STORE_ID', '')
    password = getattr(settings, 'SSLCOMMERZ_STORE_PASSWORD', '')
    if not store_id or not password:
        raise GatewayError('SSLCommerz credentials are not configured')
    sandbox = getattr(settings, 'SSLCOMMERZ_SANDBOX', True)
    root = 'https://sandbox.sslcommerz.com' if sandbox else 'https://securepay.sslcommerz.com'
    return store_id, password, root

def initiate(attempt, delivery, base_url):
    store_id, password, root = config()
    data = {
        'store_id': store_id, 'store_passwd': password,
        'total_amount': str(attempt.amount), 'currency': attempt.currency,
        'tran_id': attempt.transaction_id, 'success_url': base_url + '/api/payments/return/',
        'fail_url': base_url + '/api/payments/return/',
        'cancel_url': base_url + '/api/payments/return/',
        'ipn_url': base_url + '/api/payments/ipn/',
        'shipping_method': 'Courier', 'product_name': 'EVU Fashion Order',
        'product_category': 'Fashion', 'product_profile': 'general',
        'cus_name': delivery.recipient, 'cus_email': attempt.purchase.user.email or 'customer@example.invalid',
        'cus_add1': delivery.address[:200], 'cus_city': delivery.city,
        'cus_country': 'Bangladesh', 'cus_phone': delivery.phone,
        'ship_name': delivery.recipient, 'ship_add1': delivery.address[:200],
        'ship_city': delivery.city, 'ship_country': 'Bangladesh',
    }
    try:
        response = requests.post(root + '/gwprocess/v4/api.php', data=data, timeout=15)
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise GatewayError('Payment gateway unavailable') from exc
    url = result.get('GatewayPageURL', '')
    session = result.get('sessionkey', '')
    if result.get('status') != 'SUCCESS' or not url.startswith('https://'):
        raise GatewayError('Payment session could not be created')
    return url, session

def validate(validation_id):
    store_id, password, root = config()
    if not isinstance(validation_id, str) or not 1 <= len(validation_id) <= 120:
        raise GatewayError('Missing validation ID')
    try:
        response = requests.get(root + '/validator/api/validationserverAPI.php', params={
            'val_id': validation_id, 'store_id': store_id,
            'store_passwd': password, 'v': '1', 'format': 'json',
        }, timeout=15)
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise GatewayError('Gateway verification unavailable') from exc
    if result.get('status') not in ('VALID', 'VALIDATED'):
        raise GatewayError('Payment not verified')
    return result
