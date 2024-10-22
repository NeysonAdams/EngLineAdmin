import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import Exesize, Levels, LevelsStat, User, LessonSchedler, Exesesizes, UserLevelExp
from sqlalchemy.sql.expression import func
from mobile_api.aicomponent import check_translation, check_grammar, check_answer, check_text_question, speach_to_text
import json

from server_init import db
level_blueprint = Blueprint('level_blueprint', __name__)

def get_number(current_number:int):
    page = 1
    min = 0
    max = 50
    cn = current_number
    while cn >50:
        cn -= 50
        page +=1

    if page == 1:
        return 0, 50, 1

    if cn > 40:
        min = 0 + 50*page-1
        max = 50*page+1
    elif cn <10 and page > 2:
        min = 0 + 50 * page - 2
        max = 50*page
    else:
        min = 0 + 50 * page - 1
        max = 50 * page

    return min, max, page


@level_blueprint.route('/levels/main', methods=['GET'])
@jwt_required()
def main():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    record = LevelsStat.query.filter_by(user_id=user_id).order_by(LevelsStat.number.desc()).first()

    page = 1
    min = 0
    max = 50

    if record is not None:
        min, max, page = get_number(record.number)

    stats = LevelsStat.query.filter((LevelsStat.user_id==user_id) & (LevelsStat.number >= min) & (LevelsStat.number <max)).all()

    if len (stats) == 0 :
        lvl = LevelsStat()
        lvl.user_id = user_id
        lvl.level_id = 0;
        lvl.number = 1
        lvl.passed_count = 0
        lvl.errors_count = 0
        db.session.add(lvl)
        db.session.commit()
        stats.append(lvl)

    return jsonify(
        user=user.serialize,
        stats = [s.serialize for s in stats],
        page=page
    ), 200

@level_blueprint.route('/levels/page/<int:page>', methods=['GET'])
@jwt_required()
def page(page:int):
    user_id = get_jwt_identity()
    min = 50 * page - 1
    max = 50 * page

    stats = LevelsStat.query.filter(
        (LevelsStat.user_id == user_id) & (LevelsStat.number >= min) & (LevelsStat.number < max)).all()

    return jsonify(
        stats=[s.serialize for s in stats],
        page=page
    ), 200

@level_blueprint.route('/levels/update', methods=['POST'])
@jwt_required()
def update():
    user_id = get_jwt_identity()
    level_id = request.form.get("level_id")
    number = request.form.get("number")
    errors = request.form.get("errors")
    ex_number = request.form.get("ex_number")
    expirience = request.form.get("expirience")

    user = User.query.filter_by(id=user_id).first()

    lvl_info = UserLevelExp.query.filter_by(level = user.level).first()

    if user.experiance + expirience > lvl_info.max:
        user.experiance = user.experiance + expirience - lvl_info.max
        user.current_level = user.current_level+1
    else:
        user.experiance = user.experiance + expirience

    record = LevelsStat.query.filter_by(user_id=user_id, number=number).first()

    if record == None:
        jsonify(message="No Record"), 404

    record.errors_count = errors
    record.passed_count = ex_number

    db.session.commit()

    return jsonify(user=user.serialize,
                   info=lvl_info.serialize,
                   level=record.serialize), 200

@level_blueprint.route('/levels/get', methods=['POST'])
@jwt_required()
def get():
    user_id = get_jwt_identity()

    language = request.form.get("language")
    number = request.form.get("number")

    level = Levels.query.filter_by(language=language, number=number).first()

    if level is None:
        return jsonify(message="No Lesson"), 404

    record = LevelsStat.query.filter_by(user_id=user_id, number=number).first()

    if not record:
        stat = LevelsStat()
        stat.user_id = user_id
        stat.level_id = level.id
        stat.number = number
        stat.errors_count = 0
        stat.passed_count = 0
        stat.max_count = len(level.exesizes_link)
        db.session.add(stat)
        db.session.commit()

    return jsonify(level.serialize), 200
