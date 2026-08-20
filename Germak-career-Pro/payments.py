from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database import db
from models import Payment, User
from paypal import PayPalService
from mtn import MTNMoMoService

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payment')

@payments_bp.route('/paypal/create', methods=['POST'])
@login_required
def paypal_create():
    order = PayPalService.create_order(amount=10.00, currency="USD")
    if order and 'id' in order:
        return jsonify({'order_id': order['id'], 'details': order}), 200
    return jsonify({'error': 'Failed to create PayPal order. Check server credentials.'}), 500

@payments_bp.route('/paypal/capture', methods=['POST'])
@login_required
def paypal_capture():
    data = request.get_json() or {}
    order_id = data.get('order_id')
    if not order_id:
        return jsonify({'error': 'Order ID is required.'}), 400

    # Prevent duplicate payment handling
    existing_payment = Payment.query.filter_by(transaction_id=order_id, status='successful').first()
    if existing_payment:
        return jsonify({'message': 'Payment already verified.', 'status': 'successful'}), 200

    capture_res = PayPalService.capture_order(order_id)
    if capture_res and capture_res.get('status') == 'COMPLETED':
        payment = Payment(
            user_id=current_user.id,
            provider='paypal',
            transaction_id=order_id,
            amount=10.00,
            currency='USD',
            status='successful',
            completed_at=datetime.utcnow()
        )
        current_user.is_premium = True
        db.session.add(payment)
        db.session.commit()

        return jsonify({'message': 'Payment successful! Premium access unlocked.', 'status': 'successful'}), 200
    
    return jsonify({'error': 'Payment verification failed or not completed.'}), 400

@payments_bp.route('/mtn/create', methods=['POST'])
@login_required
def mtn_create():
    data = request.get_json() or {}
    phone_number = data.get('phone_number', '').strip()
    if not phone_number:
        return jsonify({'error': 'Phone number is required.'}), 400

    res = MTNMoMoService.request_to_pay(phone_number, amount=10.00)
    
    if res.get('status') in ['PENDING', 'SUCCESS']:
        tx_id = res.get('transaction_id') or res.get('reference_id')
        payment = Payment(
            user_id=current_user.id,
            provider='mtn',
            transaction_id=tx_id,
            amount=10.00,
            currency='GHS',
            status='successful' if res.get('status') == 'SUCCESS' else 'pending'
        )
        if res.get('status') == 'SUCCESS':
            current_user.is_premium = True
            payment.completed_at = datetime.utcnow()

        db.session.add(payment)
        db.session.commit()

        return jsonify({
            'message': 'MTN Mobile Money payment initiated successfully.',
            'transaction_id': tx_id,
            'status': payment.status
        }), 200

    return jsonify({'error': 'MTN Payment initiation failed.', 'details': res.get('error')}), 400

@payments_bp.route('/status/<transaction_id>', methods=['GET'])
@login_required
def payment_status(transaction_id):
    payment = Payment.query.filter_by(transaction_id=transaction_id, user_id=current_user.id).first()
    if not payment:
        return jsonify({'error': 'Transaction not found.'}), 404

    if payment.status == 'pending' and payment.provider == 'mtn':
        res = MTNMoMoService.check_status(transaction_id)
        if res.get('status') == 'SUCCESSFUL':
            payment.status = 'successful'
            payment.completed_at = datetime.utcnow()
            current_user.is_premium = True
            db.session.commit()

    return jsonify(payment.to_dict()), 200