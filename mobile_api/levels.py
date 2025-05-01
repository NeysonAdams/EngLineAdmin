import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import Exesize, Levels, LevelsStat, User, LessonSchedler, Exesesizes, UserLevelExp, Useranalytickinfo, Subscription, Dateanalyticks, date_analyticks
from sqlalchemy.sql.expression import func
from mobile_api.aicomponent import check_translation, check_grammar, check_answer, check_text_question, speach_to_text
import json

from server_init import db
from datetime import datetime as dt, timedelta
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


@level_blueprint.route('/levels/main', methods=['POST'])
@jwt_required()
def main():
    date_str = request.form.get("date")
    language = request.form.get("language")

    if date_str is None:
        return jsonify({"message": "Необходимо передать 'date'"}), 400

    try:
        date_obj = dt.strptime(date_str, '%Y-%m-%d')  # Формат даты: ГГГГ-ММ-ДД
    except ValueError:
        return jsonify({"message": "Некорректный формат даты. Используйте 'ГГГГ-ММ-ДД'"}), 400

    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    record = LevelsStat.query.filter_by(user_id=user_id).order_by(LevelsStat.number.desc()).first()
    subscription = Subscription.query.filter_by(user_id=user_id).first()

    page = 1
    min = 0
    max = 50

    if record is not None:
        min, max, page = get_number(record.number)

    stats = LevelsStat.query.filter((LevelsStat.user_id==user_id) & (LevelsStat.number >= min) & (LevelsStat.number <max)).all()

    if len (stats) == 0 :
        lvl = LevelsStat()
        lvl.user_id = user_id
        lvl.level_id = 1 if language=="ru" else 2
        lvl.number = 1
        lvl.passed_count = 0
        lvl.errors_count = 0
        db.session.add(lvl)
        db.session.commit()
        stats.append(lvl)

    user_info = Useranalytickinfo.query.filter_by(user_id=user_id).first()

    if user_info:
        records = sorted(user_info.date_link, key=lambda x: x.date, reverse=True)[:31]
        data = [record.serialize for record in records]
    else:
        # Если user_info отсутствует, задаем data пустым массивом или другим значением по умолчанию
        data = []

    previous_day = date_obj - timedelta(days=1)

    if user_info:
        date_record = Dateanalyticks.query.filter(
            date_analyticks.c.useranalytickinfo_id == user_info.id,
            Dateanalyticks.date == date_obj
        ).first()

        pdate_record = Dateanalyticks.query.filter(
            date_analyticks.c.useranalytickinfo_id == user_info.id,
            Dateanalyticks.date == previous_day
        ).first()

        if not date_record and not pdate_record:
            user.days = 0
            db.session.commit()

    return jsonify(
        user=user.serialize,
        stats = [s.serialize for s in stats],
        analyticks = data,
        page=page,
        subscription=subscription
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
        number = int(request.form.get("number"))
        errors = request.form.get("errors")
        ex_number = request.form.get("ex_number")
        expirience = int (request.form.get("expirience"))

        level = Levels.query.filter_by(id=level_id).first()
        user = User.query.filter_by(id=user_id).first()

        if user.current_level==0:
            user.current_level =1
            db.session.commit()

        lvl_info = UserLevelExp.query.filter_by(level=user.current_level).first()

        if user.experiance + expirience > lvl_info.max:
            user.experiance = user.experiance + expirience - lvl_info.max
            user.current_level = user.current_level+1
        else:
            user.experiance = user.experiance + expirience

        record = LevelsStat.query.filter_by(user_id=user_id, number=number).first()

        if record is None:
            return jsonify(message="No Record"), 404

        record.errors_count = int(errors)
        record.passed_count = int(ex_number)

        if record.passed_count == len(level.exesizes_link):
            next_level = Levels.query.filter_by(language=level.language, number=number+1).first()

            next_record = LevelsStat.query.filter_by(user_id=user_id, number=number+1).first()

            if not next_record:
                stat = LevelsStat()
                stat.user_id = user_id
                stat.level_id = next_level.id
                stat.number = number+1
                stat.errors_count = 0
                stat.passed_count = 0
                stat.max_count = len(next_level.exesizes_link)
                db.session.add(stat)

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

    subscription = Subscription.query.filter_by(user_id=user_id).first()

    return jsonify(level=level.serialize,
                   stat=record.serialize,
                   subscription={} if not subscription else subscription.serialize), 200
