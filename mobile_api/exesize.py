from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import Exesize, Lesson, User, Inputquestion, Audioquestion, Videoquestion
from sqlalchemy.sql.expression import func

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



