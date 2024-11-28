from functools import wraps
from flask import Blueprint, request, jsonify
from flask import make_response, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from database.models import User, Levels, Exesesizes, Exesize, Question, Inputquestion, Audioquestion, Wordexecesize, Wordslink
from flask_security.utils import hash_password, verify_password
from server_init import db
from flask_cors import cross_origin
from mobile_api.aicomponent import generate_test_question, generate_audio_question, text_to_speach, generate_text_question, generate_word_pair

import os
import json
import datetime

audio_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'audio'))

newadmin = Blueprint('newadmin', __name__)

@newadmin.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        response.status_code = 200
        return response

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
@role_required('superuser')
@cross_origin()
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


@newadmin.route('/admin/api/levels', methods=['GET', 'POST'])
@cross_origin()
@role_required('superuser')
def level():
    if request.method == 'GET':
        levels = Levels.query.all()
        return jsonify([level.api_serialize_all for level in levels]), 200
    if request.method == 'POST':
        data = request.get_json()
        level_id = data.get('id')

        if level_id == -1:
            level = Levels()
            level.number = data.get('number')
            level.language = data.get('language')
            db.session.add(level)
            db.session.commit()
        else:
            level = Levels.query.filter_by(id=level_id).first()

        packages = data.get('exesizes')

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
                exesizes.name = package['name']
                exesizes.type = package['type']
                exesizes.level = package["level"]
                exesizes.lenguage = data.get('language')

                db.session.commit()

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
                    else:
                        audio = Audioquestion.query.filter_by(id=exec['audio']['id']).first()
                    audio.question = exec['audio']['question']
                    audio.audio_query = exec['audio']['audio_query']
                    audio.audio_url = exec['audio']['audio_url']
                    audio.isrecord = exec['audio']['isrecord']

                    if exec['audio']['id'] == -1:
                        db.session.add(audio)
                    db.session.commit()

                if exec['type'] == 'word_pair_exesize':
                    if exec['word_ex']['id'] == -1:
                        wordex = Wordexecesize()
                    else:
                        wordex = Wordexecesize.query.filter_by(id=exec['word_ex']['id']).first()

                    for word in exec['word_ex']['words']:
                        if word["id"] == -1:
                            w = Wordslink()
                        else:
                            w = Wordslink.query.filter_by(words["id"]).first()
                        w.eng = word["eng"]
                        w.rus = word["rus"]
                        w.uzb = word["uzb"]

                        if words["id"] == -1:
                            db.session.add(w)
                            wordex.words.append(w)

                        db.session.commit()

            level.exesizes_link.append(exesizes)

        db.session.commit()
        return jsonify(level.serialize_max), 200


def removeExesize(id):
    esesize = Exesize.query.filter_by(id=id).first()

    if esesize.type == 'test_question':
        testQ = Question.query.filter_by(id=esesize.questions_id).first()
        db.session.delete(testQ)

    if esesize.type == 'input_question':
        testQ = Inputquestion.query.filter_by(id=esesize.input_id).first()
        db.session.delete(testQ)

    if esesize.type == 'audio_question':
        testQ = Audioquestion.query.filter_by(id=esesize.audio_id).first()
        db.session.delete(testQ)

    if esesize.type == 'word_pair_exesize':
        testQ = Wordexecesize.query.filter_by(id=esesize.word_ex_id).first()
        testQ.wordslink = []
        db.session.commit()
        db.session.delete(testQ)

    db.session.delete(esesize)
    db.session.commit()


def removePack(id):
    package = Exesesizes.query.filter_by(id=id).first()
    for ex in package.exesize:
        removeExesize(ex.id)
    package.exesize = []
    db.session.commit()

    db.session.delete(package)
    db.session.commit()

def removeLevel (id):
    level = Levels.query.filter_by(id=id).first()
    for pack in level.exesizes_link:
        removePack(pack.id)
    level.exesizes_link = []
    db.session.commit()

    db.session.delete(level)
    db.session.commit()


@newadmin.route('/admin/api/delete', methods=[ 'POST'])
@cross_origin()
@role_required('superuser')
def delete():
    data = request.get_json()

    object = data["object"]
    id = data["object_id"]

    if object == "exesize":
        removeExesize(id)

    if object == "package":
        removePack(id)

    if object == "level":
        removeLevel(id)


#[, '', '', 'video_question', 'word_pair_exesize', 'record_question', 'translate_exesize']
@newadmin.route('/admin/api/levels/<id>', methods=['GET'])
@cross_origin()
@role_required('superuser')
def getlevel(id):
        level = Levels.query.filter_by(id=id).first()

        if not level:
            return jsonify(msg="Level not exist"), 404

        return jsonify(level.serialize_max), 200

@newadmin.route('/admin/api/generate', methods=['POST'])
@cross_origin()
@role_required('superuser')
def generate():
    data = request.get_json()
    type = data.get("type")
    language = data.get("language")
    difficulty = data.get('difficulty')
    itype = data.get('itype')

    if type == "test_question":
        ai_response = generate_test_question(difficulty=difficulty, language=language)
        j_obj = json.loads(ai_response.choices[0].message.content)
        return jsonify(j_obj), 200

    if type == "audio_question":
        ai_response = generate_audio_question(difficulty=difficulty, language=language)
        j_obj = json.loads(ai_response.choices[0].message.content)
        f_name = f"audio_a_q_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}.mp3"
        audio_path = os.path.join(audio_folder, f_name)
        audio = text_to_speach(j_obj["audio_query"])
        if os.path.exists(os.path.join(audio_folder, f_name)):
            os.remove(os.path.join(audio_folder, f_name))
        audio.stream_to_file(audio_path)

        j_obj["audio_url"] = url_for('static', filename=f"audio/{f_name}")

        return jsonify(j_obj), 200

    if type == "input_question":
        ai_response = generate_text_question(difficulty=difficulty, language=language, type=itype)
        j_obj = json.loads(ai_response.choices[0].message.content)
        return jsonify(j_obj), 200

    if type == "word_pair_exesize":
        ai_response = generate_word_pair(difficulty=difficulty, type=itype)
        j_obj = json.loads(ai_response.choices[0].message.content)
        return jsonify(j_obj), 200

    return jsonify(msg="Unsupported Type"), 400