import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import User, Theory, Frazes
from sqlalchemy.sql.expression import func
from mobile_api.aicomponent import check_translation, check_grammar, check_answer, check_text_question, speach_to_text
import json

from server_init import db
theory_blueprint = Blueprint('theory_blueprint', __name__)

@theory_blueprint.route('/theory/get', methods=['POST'])
@jwt_required()
def get():
    user_id = get_jwt_identity()
    date = request.form.get("date")

    theory = Theory.query.filter_by(observing_date=date).first()

    if not theory:
        return jsonify({"message": "Данные отсутствуют"}), 400

    return jsonify(theory=theory.serialize), 200