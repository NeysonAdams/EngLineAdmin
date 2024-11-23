from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from database.models import User, Levels, Exesesizes, Exesize, Question, Inputquestion, Audioquestion
from flask_security.utils import hash_password, verify_password
from server_init import db
from flask_cors import cross_origin


newadmin = Blueprint('newadmin', __name__)

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()

            if user is None:
                return jsonify({"msg": "User not found"}), 404

            is_superuser = False
            for role in user.roles:
                 if required_role == role.name:
                    is_superuser = True

            if not is_superuser:
                return jsonify({"msg": "Insufficient role"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

@newadmin.route('/admin/api/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()  # Получение данных из JSON-запроса
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not verify_password(password, user.password):
        return jsonify(Error="Wrong password"), 404

    is_superuser = False
    for role in user.roles:
        if 'superuser' == role.name:
            is_superuser = True

    if not is_superuser:
        return jsonify(Error="This User has No Access"), 404

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.admin_user_info(access_token, refresh_token)), 200

@newadmin.route('/admin/api/auth', methods=['GET'])
@cross_origin()
@role_required('superuser')
def auth():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.admin_user_info(access_token, refresh_token)), 200

@newadmin.route('/admin/api/refresh_token', methods=["GET"])
@cross_origin()
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=user_id),
        'refresh_token': create_refresh_token(identity=user_id)
    }
    return jsonify(ret), 200
@newadmin.route('/admin/api/users', methods=['GET', 'POST', 'PUT'])
@cross_origin()
@role_required('superuser')
def get_users():
    if request.method == 'GET':
        users = User.query.all()
        return jsonify([user.admin_serialize for user in users]), 200

    if request.method == 'POST':
        id = request.form.get('id')
        email = request.form.get('email')
        name = request.form.get('name')
        img_url = request.form.get('img_url')
        phone_number = request.form.get('phone_number')
        #password = request.form.get('password')
        level = request.form.get('level')
        active = request.form.get('active')
        confirmed_at = request.form.get('confirmed_at')
        role = request.form.get('role')

        user = User.query.filter_by(id=id).first()
        user.email = email
        user.name = name
        user.img_url = img_url
        user.phone_number = phone_number
        user.level = level
        user.active = active
        user.confirmed_at = confirmed_at
        user.role = [role]
    if request.method == 'PUT':
        email = request.form.get('email')
        name = request.form.get('name')
        img_url = request.form.get('img_url')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        level = request.form.get('level')
        active = request.form.get('active')
        confirmed_at = request.form.get('confirmed_at')
        role = request.form.get('role')

        user = User()
        user.email = email,
        user.name = name,
        user.img_url = img_url,
        user.password = hash_password(password)
        user.phone_number = phone_number,
        user.level = level,
        user.active = active,
        user.confirmed_at = confirmed_at
        user.role = [role]
        db.session.add(user)
        db.session.commit()

@newadmin.route('/admin/api/users/<id>', methods=['DELETE'])
@cross_origin()
@role_required('superuser')
def deleteUser(id):
    user = User.query.filter_by(id=id).first()

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"User {id} has been deleted"}), 200


@newadmin.route('/admin/api/levels', methods=['GET', 'POST', 'PUT'])
@cross_origin()
@role_required('superuser')
def level():
    if request.method == 'GET':
        levels = Levels.query.all()
        return jsonify([level.api_serialize_all for level in levels]), 200
    if request.method == 'POST':
        data = request.get_json()
        level_id = data.get('level_id')

        if level_id == -1:
            level = Levels()
            level.number = data.get('number')
            level.language = data.get('language')
            db.session.add(level)
            db.session.commit()
        else:
            level = Levels.query.filter_by(id=level_id).first()

        packages = data.get('packages')

        for package in packages:
            if package["id"] == -1:
                exesizes = Exesesizes()
                exesizes.name = package['name']
                exesizes.type = package['type']
                exesizes.level = package["level"]
                exesizes.lenguage = data.get('language')

                db.session.add(exesizes)
                db.session.commit()
            else:
                exesizes = Exesesizes.query.filter_by(id=package["id"]).first()

            for exec in package['exesize']:
                if exec["id"] == -1:
                    exesize = Exesize()
                    exesize.type = exec['type']
                    exesize.level = package["level"]

                    db.session.add(exesize)
                    db.session.commit()
                else:
                    exesize = Exesize.query.filter_by(id=exec["id"]).first()

                if exec['type'] == 'test_question':
                    if exec['question']['id'] == -1:
                        question = Question()
                        question.question = exec['question']['question']
                        question.var1 = exec['question']['var1']
                        question.var2 = exec['question']['var2']
                        question.var3 = exec['question']['var3']
                        question.var4 = exec['question']['var4']
                        question.right_var = exec['question']['right_var']
                        question.var_dif = exec['question']['var_dif']

                        db.session.add(question)
                        db.session.commit()

                        exesize.question = question
                        db.session.commit()
                    else:
                        exesize.question.question = exec['question']['question']
                        exesize.question.var1 = exec['question']['var1']
                        exesize.question.var2 = exec['question']['var2']
                        exesize.question.var3 = exec['question']['var3']
                        exesize.question.var4 = exec['question']['var4']
                        exesize.question.right_var = exec['question']['right_var']
                        exesize.question.var_dif = exec['question']['var_dif']
                        db.session.commit()

                if exec['type'] == 'input_question':
                    if exec['inputquestion']['id'] == -1:
                        inputquestion = Inputquestion()
                        inputquestion.question = exec['inputquestion']['question']
                        inputquestion.answer = exec['inputquestion']['answer']
                        inputquestion.level = exec['inputquestion']['level']
                        inputquestion.type = exec['inputquestion']['type']
                        inputquestion.isrecord = exec['inputquestion']['isrecord']

                        db.session.add(inputquestion)
                        db.session.commit()

                        exesize.input = inputquestion
                        db.session.commit()
                    else:
                        exesize.input.question = exec['inputquestion']['question']
                        exesize.input.answer = exec['inputquestion']['answer']
                        exesize.input.level = exec['inputquestion']['level']
                        exesize.input.type = exec['inputquestion']['type']
                        exesize.input.isrecord = exec['inputquestion']['isrecord']
                        db.session.commit()

                if exec['type'] == 'audio_question':
                    if exec['audio']['id'] == -1:
                        audio = Audioquestion()



            level.exesizes_link.append(exesizes)

#[, '', '', 'video_question', 'word_pair_exesize', 'record_question', 'translate_exesize']
@newadmin.route('/admin/api/levels/<id>', methods=['GET'])
@cross_origin()
@role_required('superuser')
def getlevel(id):
        level = Levels.query.filter_by(id=id).first()

        if not level:
            return jsonify(msg="Level not exist"), 404

        return jsonify(level.serialize_max), 200