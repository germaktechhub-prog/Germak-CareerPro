import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_login import LoginManager, current_user, login_required

from config import Config
from database import db
from models import User, UploadedFile
from auth import auth_bp
from payments import payments_bp
from documents import documents_bp
from admin import admin_bp

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Ensure required asset directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

    db.init_app(app)

    # Login Manager Setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(admin_bp)

    # Secure Upload Endpoint
    @app.route('/api/upload', methods=['POST'])
    @login_required
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request.'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected.'}), 400

        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in app.config['ALLOWED_EXTENSIONS']:
            return jsonify({'error': f'Invalid file extension. Allowed: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'}), 400

        # Generate secure random filename
        random_name = f"{os.urandom(8).hex()}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
        file.save(file_path)

        relative_path = f"/static/uploads/{random_name}"
        upload_record = UploadedFile(
            user_id=current_user.id,
            filename=file.filename,
            file_type=file.content_type or ext,
            file_path=relative_path
        )
        db.session.add(upload_record)
        db.session.commit()

        return jsonify({'message': 'File uploaded successfully.', 'file_path': relative_path}), 201

    # Serve index.html SPA
    @app.route('/')
    def index():
        return render_template('index.html', paypal_client_id=app.config['PAYPAL_CLIENT_ID'])

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)