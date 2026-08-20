from functools import wraps
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def premium_required(f):
    """Decorator to enforce $10 one-time payment access control."""
    @wraps(f)

    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required. Please log in.', 'code': 'AUTH_REQUIRED'}), 401
        if not current_user.is_premium and current_user.role != 'admin':
            return jsonify({'error': 'Please complete your $10 payment to unlock this feature.', 'code': 'PAYMENT_REQUIRED'}), 402
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to enforce admin role requirement."""
    @wraps(f)

    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required.', 'code': 'AUTH_REQUIRED'}), 401
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin privileges required.', 'code': 'FORBIDDEN'}), 403
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not full_name or not email or not password:
        return jsonify({'error': 'Full name, email, and password are required.'}), 400
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists.'}), 409

    # First registered user becomes admin automatically for testing/admin setup
    is_first_user = User.query.count() == 0
    role = 'admin' if is_first_user else 'user'

    hashed_pw = generate_password_hash(password, method='scrypt')
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hashed_pw,
        role=role,
        is_premium=is_first_user # Auto-grant premium to first admin user
    )
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return jsonify({'message': 'Registration successful.', 'user': user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    login_user(user)
    return jsonify({'message': 'Logged in successfully.', 'user': user.to_dict()}), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully.'}), 200

@auth_bp.route('/me', methods=['GET'])

def get_current_user():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': current_user.to_dict()}), 200
    return jsonify({'authenticated': False, 'user': None}), 200