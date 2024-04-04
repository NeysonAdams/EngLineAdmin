from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import Exesize, Lesson, User, Inputquestion, Audioquestion, Videoquestion, LessonSchedler
from sqlalchemy.sql.expression import func

from server_init import db
exesize_blueprint = Blueprint('exesize_blueprint', __name__)

@exesize_blueprint.route('/exesize/get', methods=['POST'])
@jwt_required()
def get():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    lesson_name = request.form.get("lesson_name")

    if not user:
        return jsonify(message="User not exist"), 400

    level = user.level

    exesizes = Exesize.query.filter_by(level=level, lesson_name=lesson_name).order_by(func.random()).limit(10).all()

    return jsonify([i.serialize for i in exesizes]), 200

@exesize_blueprint.route('/exesize/check_input', methods=['POST'])
@jwt_required()
def check_input():
    id = request.form.get("question_id")
    answer = request.form.get("answer")

    question = Inputquestion.query.filter_by(id=id).first()

    if not question:
        return jsonify(message="Question not exist"), 404

    return jsonify(message=(answer == question.answer)), 200


@exesize_blueprint.route('/exesize/check_audio', methods=['POST'])
@jwt_required()
def check_audio():
    id = request.form.get("question_id")
    answer = request.form.get("answer")

    question = Audioquestion.query.filter_by(id=id).first()

    if not question:
        return jsonify(message="Question not exist"), 404

    answers = question.answer.split(',')

    is_right = False
    for a in answers:
        if a==answer:
            is_right = True
            break

    return jsonify(message=is_right), 200




@exesize_blueprint.route('/exesize/check_video', methods=['POST'])
@jwt_required()
def check_video():
    id = request.form.get("question_id")
    answer = request.form.get("answer")

    question = Videoquestion.query.filter_by(id=id).first()

    if not question:
        return jsonify(message="Question not exist"), 404

    answers = question.answer.split(',')

    is_right = False
    for a in answers:
        if a == answer:
            is_right = True
            break

    return jsonify(message=is_right), 200


@exesize_blueprint.route('/exesize/registr_speach_lesson', methods=['POST'])
@jwt_required()
def registr_speach_lesson():

    user_id = get_jwt_identity()

    duration = request.form.get("duration")
    date = request.form.get("date")
    topic = request.form.get("topic")
    telegram_contact_phone = request.form.get("telegram_contact_phone")
    level = request.form.get("level")

    lesson_schedul = LessonSchedler()
    lesson_schedul.duration = duration
    lesson_schedul.date = date
    lesson_schedul.topic = topic
    lesson_schedul.telegram_contact_phone = telegram_contact_phone
    lesson_schedul.level = level
    lesson_schedul.user_id = user_id

    db.session.add(lesson_schedul)
    db.session.commit()

    return jsonify(message="Success"), 200

