from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import Cource, User, Lesson
from server_init import db

cources_bluepprint = Blueprint('cources_bluepprint', __name__)

@cources_bluepprint.route('/cource/all', methods=['GET'])
@jwt_required()
def all():
    cources = Cource.query.all()

    return jsonify(cources= [i.serialize for i in cources]), 200


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

    return jsonify(lessons=[i.serialize for i in lessons]), 200



