from flask import Blueprint, request, send_file, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

file_loader_bluerpint = Blueprint('file_loader_bluerpint', __name__)

@file_loader_bluerpint.route('/file/image', methods=["POST"])
@jwt_required()
def image():
    url = request.form.get('url')
    return send_file(url,  mimetype='image/jpeg')

@file_loader_bluerpint.route('/file/pdf', methods=["POST"])
@jwt_required()
def pdf():
    url = request.form.get('url')
    return send_file(url, mimetype='application/pdf')

@file_loader_bluerpint.route('/file/slides', methods=["POST"])
@jwt_required()
def slides():
    url = request.form.get('url')
    return send_file(url, mimetype='application/pdf')

@file_loader_bluerpint.route('/file/localization', methods=["POST"])
def localization():
    leng = request.form.get('leng')
    directory = os.path.join(os.getcwd(), 'static', 'localization')
    return send_from_directory(directory, f'{leng}.xml', as_attachment=True)
