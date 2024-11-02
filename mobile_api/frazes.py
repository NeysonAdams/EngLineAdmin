import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import Exesize, Levels, LevelsStat, User, LessonSchedler, Exesesizes, Frazes, Theory
from sqlalchemy.sql.expression import func
from mobile_api.aicomponent import check_translation, check_grammar, check_answer, check_text_question, speach_to_text
import json

from server_init import db
fraze_blueprint = Blueprint('fraze_blueprint', __name__)

@fraze_blueprint.route('/frazes/get', methods=['POST'])
@jwt_required()
def get():

    user_id = get_jwt_identity()
    date_str = request.form.get("date")
    language = request.form.get("language")

    if date_str is None:
        return jsonify({"message": "Необходимо передать 'date'"}), 400

    # Парсинг даты
    try:
        date_obj = dt.strptime(date_str, '%Y-%m-%d')  # Формат даты: ГГГГ-ММ-ДД
    except ValueError:
        return jsonify({"message": "Некорректный формат даты. Используйте 'ГГГГ-ММ-ДД'"}), 400

    frazes = Theory.query.filter_by(observing_date=date_obj).first()

    if not frazes:
        return jsonify({"message": "Данные отсутствуют"}), 400

    return jsonify(frazes.serialize(language)), 200

