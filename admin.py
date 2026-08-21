from flask import Blueprint, jsonify, request
from flask_login import login_required
from database import db
from models import User, Payment, Document
from auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def get_stats():
    total_users = User.query.count()
    premium_users = User.query.filter_by(is_premium=True).count()
    total_payments = Payment.query.count()
    successful_payments = Payment.query.filter_by(status='successful').count()
    failed_payments = Payment.query.filter_by(status='failed').count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(Payment.status == 'successful').scalar() or 0.0
    total_documents = Document.query.count()

    return jsonify({
        'total_users': total_users,
        'premium_users': premium_users,
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'failed_payments': failed_payments,
        'total_revenue': total_revenue,
        'total_documents': total_documents
    }), 200

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200

@admin_bp.route('/users/<int:user_id>/toggle-premium', methods=['POST'])
@login_required
@admin_required
def toggle_user_premium(user_id):
    user = User.query.get_or_404(user_id)
    user.is_premium = not user.is_premium
    db.session.commit()
    return jsonify({'message': f"User premium status updated to {user.is_premium}.", 'user': user.to_dict()}), 200

@admin_bp.route('/payments', methods=['GET'])
@login_required
@admin_required
def list_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return jsonify([p.to_dict() for p in payments]), 200