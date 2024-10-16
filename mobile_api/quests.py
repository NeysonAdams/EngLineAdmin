import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import User, Quests, Userquest
from sqlalchemy.sql.expression import func
from mobile_api.aicomponent import check_translation, check_grammar, check_answer, check_text_question, speach_to_text
import json

from server_init import db
quests_blueprint = Blueprint('quests_blueprint', __name__)

@quests_blueprint.route('/quests/get', methods=['GET'])
@jwt_required()
def get():
    user_id = get_jwt_identity()

    quests = Quests.query.all()

    return jsonify(quests=[q.seralize(user_id) for q in quests]), 200

@quests_blueprint.route('/quests/update', methods=['POST'])
@jwt_required()
def update():
    user_id = get_jwt_identity()
    quest_id = request.form.get("quest_id")
    count = request.form.get("count", type=int)

    quest = Quests.query.filter_by(id=quest_id).first()

    uquests = quest.uquests.filter(Userquest.user_id == user_id).first()

    if uquests is None:
        uquests = Userquest()
        uquests.user_id = user_id
        uquests.current_count = count
        db.session.add(uquests)
    else:
        uquests.current_count = count

    db.session.commit()

    return jsonify(quest=quest.seralize(user_id)), 200

