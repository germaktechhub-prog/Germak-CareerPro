import uuid
import requests
from flask import current_app

class MTNMoMoService:
    @staticmethod
    def _get_api_base():
        env = current_app.config.get('MTN_ENVIRONMENT', 'sandbox')
        return 'https://sandbox.momodeveloper.mtn.com' if env == 'sandbox' else 'https://proxy.momoapi.mtn.com'

    @classmethod
    def request_to_pay(cls, phone_number, amount, reference_id=None):
        """
        Initiates an MTN MoMo Collection request to pay (USSD Push prompt).
        In sandbox or fallback mode, returns structured transaction info.
        """
        if not reference_id:
            reference_id = str(uuid.uuid4())

        subscription_key = current_app.config.get('MTN_SUBSCRIPTION_KEY')
        
        # If API keys are not provided, operate in standard test sandbox simulation mode
        if not subscription_key:
            return {
                'status': 'SUCCESS',
                'transaction_id': f'MTN-SIM-{reference_id[:8]}',
                'reference_id': reference_id,
                'message': 'Sandbox test payment simulated successfully.'
            }

        url = f"{cls._get_api_base()}/collection/v1_0/requesttopay"
        headers = {
            'X-Reference-Id': reference_id,
            'X-Target-Environment': current_app.config.get('MTN_ENVIRONMENT', 'sandbox'),
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/json'
        }
        payload = {
            "amount": str(amount),
            "currency": "GHS",
            "externalId": reference_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_number
            },
            "payerMessage": "Germak CareerPro Upgrade",
            "payeeNote": "CareerPro Lifetime Payment"
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code == 202:
                return {'status': 'PENDING', 'reference_id': reference_id}
            return {'status': 'FAILED', 'error': res.text}
        except Exception as e:
            return {'status': 'FAILED', 'error': str(e)}

    @classmethod
    def check_status(cls, reference_id):
        """Checks transaction status for a MoMo reference ID."""
        if reference_id.startswith('MTN-SIM-'):
            return {'status': 'SUCCESSFUL', 'amount': '10.00'}

        subscription_key = current_app.config.get('MTN_SUBSCRIPTION_KEY')
        if not subscription_key:
            return {'status': 'SUCCESSFUL'}

        url = f"{cls._get_api_base()}/collection/v1_0/requesttopay/{reference_id}"
        headers = {
            'X-Target-Environment': current_app.config.get('MTN_ENVIRONMENT', 'sandbox'),
            'Ocp-Apim-Subscription-Key': subscription_key,
        }
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json()
            return {'status': 'FAILED'}
        except Exception:
            return {'status': 'FAILED'}