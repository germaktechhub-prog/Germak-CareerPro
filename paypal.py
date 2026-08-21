import requests
from flask import current_app

class PayPalService:
    @staticmethod
    def _get_api_base():
        mode = current_app.config.get('PAYPAL_MODE', 'sandbox')
        return 'https://api-m.sandbox.paypal.com' if mode == 'sandbox' else 'https://api-m.paypal.com'

    @staticmethod
    def _get_access_token():
        client_id = current_app.config.get('PAYPAL_CLIENT_ID')
        client_secret = current_app.config.get('PAYPAL_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("PayPal credentials are not configured in environment variables.")

        url = f"{PayPalService._get_api_base()}/v1/oauth2/token"
        headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
        data = {'grant_type': 'client_credentials'}

        response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret), timeout=10)
        if response.status_code == 200:
            return response.json()['access_token']
        raise Exception(f"Failed to obtain PayPal Access Token: {response.text}")

    @classmethod
    def create_order(cls, amount, currency="USD"):
        """Creates a PayPal order for $10 USD."""
        try:
            token = cls._get_access_token()
            url = f"{cls._get_api_base()}/v2/checkout/orders"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}"
                    },
                    "description": "Germak CareerPro Lifetime Unlimited Access"
                }]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            current_app.logger.error(f"PayPal create order exception: {str(e)}")
            return None

    @classmethod
    def capture_order(cls, order_id):
        """Captures payment for an authorized PayPal order."""
        try:
            token = cls._get_access_token()
            url = f"{cls._get_api_base()}/v2/checkout/orders/{order_id}/capture"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            response = requests.post(url, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            current_app.logger.error(f"PayPal capture order exception: {str(e)}")
            return None