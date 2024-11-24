from flask import Blueprint, request, send_file, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import datetime

file_loader_bluerpint = Blueprint('file_loader_bluerpint', __name__)

audio_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'audio'))
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

@file_loader_bluerpint.route('/file/audio', methods=["POST"])
@jwt_required()
def audio():
    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    f_name = f"audio_a_q_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}{file.filename[-4:]}"

    file_path = os.path.join(audio_folder, f_name)
    file.save(file_path)

    return url_for('static', filename=f"audio/{f_name}")

@file_loader_bluerpint.route('/file/localization', methods=["POST"])
def localization():
    leng = request.form.get('leng')
    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'localization'))
    return send_from_directory(directory, f'{leng}.xml', as_attachment=True)
