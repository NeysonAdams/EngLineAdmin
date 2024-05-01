import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import Exesize, Lesson, User, Inputquestion, Audioquestion, Videoquestion, LessonSchedler, TranslationQuestion, Exesesizes
from sqlalchemy.sql.expression import func
from mobile_api.aicomponent import check_translation, check_grammar, check_answer, check_text_question, speach_to_text
import json

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

@exesize_blueprint.route('/exesize/get_exesizes', methods=['POST'])
@jwt_required()
def get_exesizes():
    language = request.form.get("language")
    type = request.form.get("type")
    level = request.form.get("level")

    exesizes = Exesesizes.query.filter_by(lenguage=language, type=type, level=level).order_by(func.random()).first()

    if not exesizes:
        return jsonify(status="Fall"), 200

    return jsonify(status="Success", exesizes=exesizes), 200

@exesize_blueprint.route('/exesize/check_input', methods=['POST'])
@jwt_required()
def check_input():
    id = request.form.get("id")
    answer = request.form.get("answer")
    language = request.form.get("language")

    print(id)

    question = Inputquestion.query.filter_by(id=id).first()

    if not question:
        return jsonify(message="Question not exist"), 404

    if question.type == "check_grammar":
        ai_response = check_grammar(answer, language)
        j_obj = json.loads(ai_response.choices[0].message.content)
        print(j_obj)
        return jsonify(check_grammar=j_obj, check_answer=None, check_audio=None, check_translation=None), 200
    elif question.type == "check_answer":
        ai_response = check_answer(question.question, answer, language)
        j_obj = json.loads(ai_response.choices[0].message.content)
        return jsonify(check_answer=j_obj, check_grammar=None, check_audio=None, check_translation=None), 200

    return jsonify(message=(answer == question.answer)), 200

@exesize_blueprint.route('/exesize/check_translation', methods=['POST'])
@jwt_required()
def check_translation():
    id = request.form.get("id")
    answer = request.form.get("answer")

    translation = TranslationQuestion.query.filter_by(id=id).first()

    if not translation:
        return jsonify(message="Question not exist"), 404

    ai_response = check_translation(text=translation.original_text, translation=answer)
    j_obj = json.load(ai_response.choices[0].message.content)

    return jsonify(check_translation=j_obj, check_answer=None, check_grammar=None, check_audio=None), 200




@exesize_blueprint.route('/exesize/check_audio', methods=['POST'])
@jwt_required()
def check_audio():
    id = request.form.get("id")
    answer = request.form.get("answer")
    language = request.form.get("language")

    question = Audioquestion.query.filter_by(id=id).first()

    if not question:
        return jsonify(message="Question not exist"), 404

    ai_response = check_text_question(text=question.audio_query, questoion=question.question, answer=answer, language=language)
    j_obj = json.loads(ai_response.choices[0].message.content)
    return jsonify(check_audio=j_obj, check_answer=None, check_grammar=None, check_translation=None), 200

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

@exesize_blueprint.route('/exesize/get_situations', methods=['POST'])
@jwt_required()
def get_situations():

    lang = request.form.get('language')
    exesizes = Exesesizes.query.filter(Exesesizes.lenguage==lang and Exesesizes.type=="situation").all()

    return jsonify(exesizes=[i.serialize for i in exesizes]), 200

@exesize_blueprint.route('/exesize/check_recorded', methods=['POST'])
@jwt_required()
def check_recorded():
    if 'file' not in request.files:
        return jsonify(message="No audio file in form"), 404
    id = request.form.get("id")
    language = request.form.get("language")
    file = request.files['file']
    quesition_type = request.form.get("quesition_type")

    if file.content_type not in ['audio/flac', 'audio/m4a', 'audio/mp3', 'audio/mp4', 'audio/mpeg',
                                         'audio/mpga', 'audio/oga', 'audio/ogg', 'audio/wav', 'audio/webm']:
        return jsonify(message="Unsupported file format"), 400

    #try:
    with open("temp_file.mp3", "wb") as audio:
        audio.write(file.read())
    with open("temp_file.mp3", "rb") as audio:
        answer = speach_to_text(audio)

    if os.path.exists("temp_file.mp3"):
        os.remove("temp_file.mp3")

    if quesition_type == "input":
        question = Inputquestion.query.filter_by(id=id).first()

        if not question:
            return jsonify(message="Question not exist"), 404

        if question.type == "check_grammar":
            ai_response = check_grammar(answer, language)
            j_obj = json.loads(ai_response.choices[0].message.content)
            print(j_obj)
            return jsonify(check_grammar=j_obj, check_answer=None, check_audio=None), 200
        elif question.type == "check_answer":
            ai_response = check_answer(question.question, answer, language)
            j_obj = json.loads(ai_response.choices[0].message.content)
            return jsonify(check_answer=j_obj, check_grammar=None, check_audio=None), 200


    if quesition_type == "audio":
        question = Audioquestion.query.filter_by(id=id).first()

        if not question:
            return jsonify(message="Question not exist"), 404

        ai_response = check_text_question(text=question.audio_query, questoion=question.question, answer=answer,
                                          language=language)
        j_obj = json.loads(ai_response.choices[0].message.content)

        return jsonify(check_audio=j_obj, check_answer={}, check_grammar={}), 200
    ###except Exception as e:
    #    if os.path.exists("temp_file.mp3"):
    #        os.remove("temp_file.mp3")
    #    print(str(e))
    #    return jsonify(message=str(e)), 500