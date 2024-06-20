from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import Cource, User, Lesson, Question, Inputquestion, Audioquestion, Videoquestion, Exesesizes, LessonSchedler, Reiting
from server_init import db

cources_bluepprint = Blueprint('cources_bluepprint', __name__)

@cources_bluepprint.route('/cource/get_test_questions', methods=['GET'])
@jwt_required()
def get_test_questions():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()
    questions = Question.query.filter_by(var_dif=user.level).all()

    return jsonify(questions=[q.serialize_lesson for q in questions]), 200

@cources_bluepprint.route('/cource/get_gramar_questions', methods=['GET'])
@jwt_required()
def get_gramar_questions():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()
    questions = Inputquestion.query.filter_by(level=user.level).all()

    return jsonify(inputquestion=[q.serialize for q in questions]), 200

@cources_bluepprint.route('/cource/get_listen_questions', methods=['GET'])
@jwt_required()
def get_listen_questions():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()
    aquestions = Audioquestion.query.filter_by(level=user.level).all()
    vquestions = Videoquestion.query.filter_by(level=user.level).all()

    return jsonify(audio=[q.serialize for q in aquestions],
                   video=[v.serialize for v in vquestions]), 200

@cources_bluepprint.route('/cource/get_speking_questions', methods=['GET'])
@jwt_required()
def get_speking_questions():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()
    aquestions = Audioquestion.query.filter_by(level=user.level).all()
    vquestions = Videoquestion.query.filter_by(level=user.level).all()

    return jsonify(audio=[q.serialize for q in aquestions],
                   video=[v.serialize for v in vquestions]), 200

@cources_bluepprint.route('/cource/all', methods=['GET'])
@jwt_required()
def all():
    cources = Cource.query.all()

    return jsonify(cources= [i.data for i in cources]), 200

@cources_bluepprint.route('/cource/bylevel', methods=['GET'])
@jwt_required()
def bylevel():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()
    if not user:
        return  jsonify(msg="Mo user"), 400
    cources = Cource.query.filter_by(level=user.level).all()

    return jsonify(cources= [i.data for i in cources]), 200

@cources_bluepprint.route('/cource/get_lessons', methods=['POST'])
@jwt_required()
def get_lessons():
    cource_id = request.form.get('cource_id')
    cource = Cource.query.filter_by(id=cource_id).first()

    if not cource:
        return jsonify(msg="Cource not exist"), 404

    return jsonify(cource.serialize_lesons), 200

@cources_bluepprint.route('/cource/get_lesson', methods=['POST'])
@jwt_required()
def get_lesson():
    uid = get_jwt_identity()
    lesson_id=request.form.get('lesson_id')
    lesson = Lesson.query.filter_by(id=lesson_id).first()

    reiting = Reiting.query.filter_by(user_id=uid, lesson_id=lesson_id).first()

    if not reiting:
        reiting = {"score":1}

    if not lesson:
        return jsonify(msg="Lesson not exist"), 404

    return jsonify(lesson.serialize), 200

@cources_bluepprint.route('/cource/inprogress', methods=['GET'])
@jwt_required()
def inprogress():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    if not user:
        return jsonify(msg="User is not exist"), 401

    cources = user.cources_in_progress

    return jsonify(cources= [i.serialize for i in cources]), 200

@cources_bluepprint.route('/cource/passed', methods=['GET'])
@jwt_required()
def passed():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    if not user:
        return jsonify(msg="User is not exist"), 401

    cources = user.cources_pased

    return jsonify(cources= [i.serialize for i in cources]), 200

@cources_bluepprint.route('/cource/add_progress', methods=['POST'])
@jwt_required()
def add_progress():
    uid = get_jwt_identity()
    cource_id = request.form.get('name')

    user = User.query.filter_by(id=uid).first()

    if not user:
        return jsonify(msg="User is not exist"), 401

    course = Cource.query.filter_by(id=cource_id).first()

    if not course:
        return jsonify(msg="Course is not exist"), 401

    user.cources_in_progress.append(course)

    db.session.commit()

    return jsonify(message="Course Started"), 200

@cources_bluepprint.route('/cource/compleate', methods=['POST'])
@jwt_required()
def compleate():
    uid = get_jwt_identity()
    cource_id = request.form.get('cource_id')

    user = User.query.filter_by(id=uid).first()

    if not user:
        return jsonify(msg="User is not exist"), 401

    course = Cource.query.filter_by(id=cource_id).first()

    if not course:
        return jsonify(msg="Course is not exist"), 401

    user.cources_pased.append(course)

    db.session.commit()

    return jsonify(message="Course Started"), 200

@cources_bluepprint.route('/cource/lessons', methods=['POST'])
@jwt_required()
def lessons():
    cource_id = request.form.get('cource_id')
    lessons = Lesson.query.filter_by(cource_id=cource_id).all()

    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    if user:
        cource  = Cource.query.filter_by(id=cource_id).first()
        if cource not in user.cources_in_progress:
            user.cources_in_progress.append(cource)
            db.session.commit()


    return jsonify(lessons=[i.serialize for i in lessons]), 200

@cources_bluepprint.route('/cource/get_home_page', methods=['POST'])
@jwt_required()
def get_home_page():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    lang  = request.form.get('Lang')

    if not user:
        return jsonify(msg="User is not exist"), 401

    cources = Cource.query.filter(Cource.lenguage==lang).all()
    exesizes = Exesesizes.query.filter(Exesesizes.lenguage==lang).all()


    return jsonify(cources=[i.serialize for i in cources],
                   exesizes=[i.serialize for i in exesizes],
                   my_cources=[i.serialize for i in user.cources_in_progress],
                   user=user.serialize), 200


@cources_bluepprint.route('/cource/set_search_lesson', methods=['POST'])
@jwt_required()
def set_search_lesson():

    uid = get_jwt_identity()
    duration = request.form.get('duration')
    date = str(request.form.get('date'))
    telegram_contact_phone = request.form.get('telegram_contact_phone')
    topic = str(request.form.get('topic'))
    level = str(request.form.get('level'))

    lesson = LessonSchedler()
    lesson.duration = int(duration)
    lesson.user_id = int(uid)
    lesson.date = date
    lesson.telegram_contact_phone = telegram_contact_phone
    lesson.topic = topic
    lesson.level = level

    db.session.add(lesson)
    db.session.commit()

    return jsonify(msg="Success"), 200


@cources_bluepprint.route('/cource/search', methods=['POST'])
@jwt_required()
def search():
    query = request.form.get('query')
    config = str(request.form.get('config'))

    cources = []
    exesizes = []

    if config == "all" or config == "c":
        cources = Cource.query.filter(Cource.title.contains(query)).all()

    if config == "all" or config == "e":
        exesizes = Exesesizes.query.filter(Exesesizes.name.contains(query)).all()

    if config == "c":
        return jsonify(cources=[i.serialize for i in cources]), 200
    if config == "e":
        return  jsonify(exesizes=[i.serialize for i in exesizes]),200


    return jsonify(cources=[i.serialize for i in cources],
                   exesizes=[i.serialize for i in exesizes]), 200