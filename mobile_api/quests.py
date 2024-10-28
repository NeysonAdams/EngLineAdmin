import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import User, Quests, Userquest
from sqlalchemy.sql.expression import func
from mobile_api.aicomponent import check_translation, check_grammar, check_answer, check_text_question, speach_to_text
import json

import datetime

from server_init import db
quests_blueprint = Blueprint('quests_blueprint', __name__)

@quests_blueprint.route('/quests/get', methods=['POST'])
@jwt_required()
def get():
    user_id = get_jwt_identity()
    date_str = request.form.get("date")
    language = request.form.get("language")

    if date_str is None:
        return jsonify({"message": "Необходимо передать 'date'"}), 400

    # Парсинг даты
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Формат даты: ГГГГ-ММ-ДД
    except ValueError:
        return jsonify({"message": "Некорректный формат даты. Используйте 'ГГГГ-ММ-ДД'"}), 400

    uquests = Userquest.query.filter(Userquest.user_id == user_id).all()

    if uquests:
        for uq in uquests:
            if uq.date != date_obj:
                db.session.delete(uq)
        db.session.commit()

    uquests = Userquest.query.filter(Userquest.user_id == user_id).all()

    if len(uquests) > 0:
        return jsonify(quests=[q.seralize(language) for q in uquests]), 200

    quests = Quests.query.order_by(func.random()).limit(5).all()
    uquests = []
    for q in quests:
        uq = Userquest()
        uq.quest_id = q.id
        uq.date = date_obj
        uq.user_id = user_id
        uq.current_count = 0
        uquests.append(uq)
        db.session.add(uq)
    db.session.commit()

    return jsonify(quests=[q.seralize(language) for q in uquests]), 200

@quests_blueprint.route('/quests/update', methods=['POST'])
@jwt_required()
def update():
    #user_id = get_jwt_identity()
    quest_id = request.form.get("quest_id")
    count = request.form.get("count", type=int)

    quest = Userquest.query.filter_by(id=quest_id).first()
    quest.current_count = count
    db.session.commit()

    return jsonify(msg="Sawed"), 200

@quests_blueprint.route('/quests/update/all', methods=['POST'])
@jwt_required()
def update_all():
    quest_id = request.form.get("quest_id")
    count = request.form.get("count", type=int)