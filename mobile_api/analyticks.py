import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import Exesize, Levels, LevelsStat, User, Exesesizes, Dateanalyticks, Useranalytickinfo
from sqlalchemy.sql.expression import func
from mobile_api.aicomponent import check_translation, check_grammar, check_answer, check_text_question, speach_to_text
import json
from datetime import datetime as dt
from server_init import db
analytiks_blueprint = Blueprint('analytiks_blueprint', __name__)

@analytiks_blueprint.route('/analytiks/add', methods=['POST'])
@jwt_required()
def add():
    user_id = get_jwt_identity()

    from_where = request.form.get("from_where")
    why_reason = request.form.get("why_reason")
    goal = request.form.get("goal")
    timing = request.form.get("timing")

    uai = Useranalytickinfo.query.filter_by(user_id=user_id).first()

    user = User.query.filter_by(id=user_id).first()
    user.timing = int(timing)
    if not uai:
        uai = Useranalytickinfo()
        uai.user_id = user_id
        uai.from_where = from_where
        uai.why_reason = why_reason
        uai.goal = goal
        db.session.add(uai)
    else:
        uai.user_id = user_id
        uai.from_where = from_where
        uai.why_reason = why_reason
        uai.goal = goal

    db.session.commit()

    return jsonify(uai.serialize), 200

@analytiks_blueprint.route('/analytiks/date', methods=['POST', 'GET'])
@jwt_required()
def date():
    user_id = get_jwt_identity()

    user_info = Useranalytickinfo.query.filter_by(user_id=user_id).first()
    user = User.query.filter_by(id=user_id).first()

    if request.method == 'GET':
        if not user_info:
            return jsonify({"message": "Пользователь не найден"}), 404

            # Получаем последние 31 запись из связи date_link
        records = user_info.date_link.order_by(Dateanalyticks.date.desc()).limit(31).all()

        # Сериализуем данные
        data = [record.serialize for record in records]

        return jsonify(data), 200

    if request.method == 'POST':
        # Получаем данные из запроса
        date_str = request.form.get("date")
        minutes = request.form.get("minutes", type=int)

        if date_str is None:
            return jsonify({"message": "Необходимо передать 'date'"}), 400

        try:
            date_obj = dt.strptime(date_str, '%Y-%m-%d')  # Формат даты: ГГГГ-ММ-ДД
        except ValueError:
            return jsonify({"message": "Некорректный формат даты. Используйте 'ГГГГ-ММ-ДД'"}), 400


        # Ищем запись Dateanalyticks с указанной датой, связанной с пользователем
        date_record = Dateanalyticks.query.join(date_analyticks).filter(
            date_analyticks.c.useranalytickinfo_id == user_info.id,
            Dateanalyticks.date == date_obj
        ).first()

        if date_record:
            # Если запись существует, обновляем 'minutes'
            date_record.minutes = minutes
        else:
            # Если записи нет, создаем новую и связываем с пользователем
            date_record = Dateanalyticks(date=date_obj, minutes=minutes)
            user_info.date_link.append(date_record)
            db.session.add(date_record)

        # Сохраняем изменения
        db.session.commit()

        previous_day = date_obj - timedelta(days=1)

        pdate_record = Dateanalyticks.query.join(date_analyticks).filter(
            date_analyticks.c.useranalytickinfo_id == user_info.id,
            Dateanalyticks.date == previous_day
        ).first()

        if pdate_record:
            user.days += 1
        else:
            user.days = 0

        db.session.commit()

        return jsonify({"message": "Данные успешно обновлены"}), 200