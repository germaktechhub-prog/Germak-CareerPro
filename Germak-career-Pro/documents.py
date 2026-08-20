from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from database import db
from models import Document
from auth import premium_required
from ai_service import AIService
from pdf_generator import PDFGenerator

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

@documents_bp.route('', methods=['GET'])
@login_required
def get_documents():
    docs = Document.query.filter_by(user_id=current_user.id).order_by(Document.updated_at.desc()).all()
    return jsonify([doc.to_dict() for doc in docs]), 200

@documents_bp.route('/<int:doc_id>', methods=['GET'])
@login_required
def get_document(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    return jsonify(doc.to_dict()), 200

@documents_bp.route('', methods=['POST'])
@login_required
@premium_required
def create_document():
    data = request.get_json() or {}
    doc_type = data.get('type')
    title = data.get('title', 'Untitled Document')
    content = data.get('content', {})
    template = data.get('template', 'modern')

    if not doc_type:
        return jsonify({'error': 'Document type is required.'}), 400

    doc = Document(
        user_id=current_user.id,
        type=doc_type,
        title=title,
        content=content,
        template=template
    )
    db.session.add(doc)
    db.session.commit()

    return jsonify({'message': 'Document saved successfully.', 'document': doc.to_dict()}), 201

@documents_bp.route('/<int:doc_id>', methods=['PUT'])
@login_required
@premium_required
def update_document(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}

    doc.title = data.get('title', doc.title)
    doc.content = data.get('content', doc.content)
    doc.template = data.get('template', doc.template)

    db.session.commit()
    return jsonify({'message': 'Document updated successfully.', 'document': doc.to_dict()}), 200

@documents_bp.route('/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    db.session.delete(doc)
    db.session.commit()
    return jsonify({'message': 'Document deleted successfully.'}), 200

@documents_bp.route('/<int:doc_id>/duplicate', methods=['POST'])
@login_required
@premium_required
def duplicate_document(doc_id):
    original = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    new_doc = Document(
        user_id=current_user.id,
        type=original.type,
        title=f"{original.title} (Copy)",
        content=original.content,
        template=original.template
    )
    db.session.add(new_doc)
    db.session.commit()
    return jsonify({'message': 'Document duplicated successfully.', 'document': new_doc.to_dict()}), 201

@documents_bp.route('/ai-enhance', methods=['POST'])
@login_required
@premium_required
def ai_enhance():
    data = request.get_json() or {}
    prompt_type = data.get('prompt_type', 'summary')
    text_input = data.get('text', '')
    context = data.get('context', {})

    enhanced_text = AIService.enhance_content(prompt_type, text_input, context)
    return jsonify({'enhanced_text': enhanced_text}), 200

@documents_bp.route('/<int:doc_id>/pdf', methods=['GET'])
@login_required
@premium_required
def download_pdf(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()
    pdf_buffer = PDFGenerator.generate_pdf(
        doc_title=doc.title,
        doc_type=doc.type,
        content=doc.content,
        template_style=doc.template
    )
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{doc.title.replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )