import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import Cource, User, Cstat, UserStatistic, Reiting
from server_init import db

statistic_blueprint = Blueprint('statistic_blueprint', __name__)


@statistic_blueprint.route('/statistic/user_statistic', methods=['GET'])
@jwt_required()
def user_statistic():
    user_id = get_jwt_identity()
    user_stat = UserStatistic.query.filter_by(user_id=user_id).first()
    if not user_stat:
        new_user_stat = UserStatistic()
        new_user_stat.user_id = user_id
        db.session.add(new_user_stat)
        db.session.commit()

        return jsonify(new_user_stat.serialize), 200

    return jsonify(user_stat.serialize), 200
@statistic_blueprint.route('/statistic/user_add_hour', methods=['GET'])
@jwt_required()
def user_add_hour():
    user_id = get_jwt_identity()

    user_stat = UserStatistic.query.filter_by(user_id=user_id).first()

    if not user_stat:
        new_user_stat = UserStatistic()
        new_user_stat.user_id = user_id
        new_user_stat.days = 0
        new_user_stat.hours = 1
        db.session.add(new_user_stat)
        db.session.commit()
    else:
        user_stat.hours+=1
        db.session.commit()

    return jsonify(msg="Success"), 200


@statistic_blueprint.route('/statistic/user_add_day', methods=['GET'])
@jwt_required()
def user_add_day():
    user_id = get_jwt_identity()
    user_stat = UserStatistic.query.filter_by(user_id=user_id).first()

    if not user_stat:
        new_user_stat = UserStatistic()
        new_user_stat.user_id = user_id
        user_stat.days = 1
        new_user_stat.hours=0
        db.session.add(new_user_stat)
        db.session.commit()
    else:
        user_stat.days+=1
        db.session.commit()

    return jsonify(msg="Success"), 200

@statistic_blueprint.route('/statistic/user_add_exesize', methods=['POST'])
@jwt_required()
def user_add_exesize():
    user_id = get_jwt_identity()
    exec = request.form.get('exec_id')
    user_stat = UserStatistic.query.filter_by(user_id=user_id).first()
    if not user_stat:
        new_user_stat = UserStatistic()
        new_user_stat.user_id = user_id
        user_stat.days = 0
        new_user_stat.hours = 0
        new_user_stat.exesizes = str(exec)
        db.session.add(new_user_stat)
        db.session.commit()
    else:
        lexcs  = user_stat.exesizes.split(',')
        if exec not in lexcs:
            user_stat.exesizes += ','+str(exec)
        db.session.commit()

    return jsonify(msg="Success"), 200

@statistic_blueprint.route('/statistic/user_add_words', methods=['POST'])
@jwt_required()
def user_add_words():
    user_id = get_jwt_identity()
    words = request.form.getlist('words[]')
    user_stat = UserStatistic.query.filter_by(user_id=user_id).first()

    if not user_stat:
        new_user_stat = UserStatistic()
        new_user_stat.user_id = user_id
        user_stat.days = 0
        new_user_stat.hours = 0
        new_user_stat.words = words
        db.session.add(new_user_stat)
        db.session.commit()
    else:
        ww = user_stat.words.split(',')
        for word in words:
            if word not in ww:
                user_stat.words += ','+word
        db.session.commit()
    return jsonify(msg="Success"), 200



@statistic_blueprint.route('/statistic/send_course_rating', methods=['POST'])
@jwt_required()
def course_rating():
    user_id = get_jwt_identity()
    course_id = request.form.get('cource_id')
    mark = request.form.get('mark')

    stat = Cstat.query.filter_by(user_id=user_id, cource_id=course_id).first()
    if not stat:
        new_stat = Cstat()
        new_stat.user_id = user_id
        new_stat.cource_id = course_id
        new_stat.mark = mark
        db.session.add(new_stat)
        db.session.commit()
    else:
        stat.mark = mark
        db.session.commit()

    stats = Cstat.query.filter_by( cource_id=course_id).all()
    count = len(stats)
    raiting = 0
    for stat in stats:
        raiting+=stat.mark

    course = Cource.query.filter_by(id=course_id).first()
    course.reiting = raiting/count
    db.session.commit()

    return jsonify(id=course_id, raiting=raiting/count), 200

@statistic_blueprint.route('/statistic/set_reiting', methods=['POST'])
@jwt_required()
def set_reiting():
    user_id = get_jwt_identity()
    score = request.form.get('score')
    lesson_id = request.form.get('lesson_id')

    reiting = Reiting.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if not reiting:
        reiting = Reiting()
        reiting.user_id = user_id
        reiting.lesson_id = lesson_id
        reiting.score = score
        db.session.add(reiting)
    else:
        reiting.score = score

    db.session.commit()
    return jsonify(msg="Success"), 200