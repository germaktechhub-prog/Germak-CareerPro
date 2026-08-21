import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default-dev-secret-key-change-in-prod')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR / "instance" / "careerpro.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads & Storage
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    GENERATED_FOLDER = os.path.join(BASE_DIR, 'static', 'generated')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    
    # Pricing
    PREMIUM_PRICE_USD = 10.00
    
    # PayPal Configuration
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')  # sandbox or live
    
    # MTN Mobile Money Configuration
    MTN_API_KEY = os.environ.get('MTN_API_KEY', '')
    MTN_API_SECRET = os.environ.get('MTN_API_SECRET', '')
    MTN_SUBSCRIPTION_KEY = os.environ.get('MTN_SUBSCRIPTION_KEY', '')
    MTN_ENVIRONMENT = os.environ.get('MTN_ENVIRONMENT', 'sandbox')  # sandbox or production
    
    # AI Integration
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'openai')  # openai, anthropic, or mock