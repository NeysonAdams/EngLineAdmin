from flask import Blueprint, jsonify, request, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import User, Chattopic, Chat
from server_init import db
from mobile_api.aicomponent import chat_start, text_to_speach, chat_answer, speach_to_text
from datetime import datetime
import json
import os


audio_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'chat'))

chat_blueprint = Blueprint('chat_blueprint', __name__)

@chat_blueprint.route('/chat/get', methods=['GET'])
@jwt_required()
def get_chat():
    uid = get_jwt_identity()

    topics = Chattopic.query.all()

    chats = Chat.query.filter_by(user_id=uid).all()

    return jsonify(topics=[t.serialize for t in topics],
                   chats = [ch.serialize for ch in chats]), 200


def generate_ai_speach(text):
    f_name = f"audio_a_q_{str(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f'))}.mp3"
    audio_path = os.path.join(audio_folder, f_name)
    audio = text_to_speach(text)
    if os.path.exists(os.path.join(audio_folder, f_name)):
        os.remove(os.path.join(audio_folder, f_name))
    audio.stream_to_file(audio_path)
    return url_for('static', filename=f"audio/{f_name}")

@chat_blueprint.route('/chat/add', methods=['POST'])
@jwt_required()
def add_chat():
    uid = get_jwt_identity()

    user = User.query.filter_by(id=uid).first()

    topic_id = request.form.get('topic_id')

    topic = Chattopic.query.filter_by(id=topic_id).first()

    ai_response = chat_start(topic.title, topic.description, user.name)
    j_obj = json.loads(ai_response.choices[0].message.content)

    audio_url = generate_ai_speach(j_obj["message"])

    data = [
            {
                "author": "AI",
                "message": j_obj["message"],
                "audio": audio_url
            }
        ]

    chat = Chat(
        user_id =uid,
        chat_data=str(data),
        topic=topic
    )
    db.session.add(chat)
    db.session.commit()

    return jsonify(chat.serialize), 200

@chat_blueprint.route('/chat/open', methods=['POST'])
@jwt_required()
def open_chat():
    chat_id = request.form.get('chat_id')
    chat = Chat.query.filter_by(id=chat_id).first()
    if not chat:
        return jsonify(msg="Chat Room not Exist"), 404

    return jsonify(chat.serialize), 200
@chat_blueprint.route('/chat/send', methods=['POST'])
@jwt_required()
def send():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    chat_id = request.form.get('chat_id')
    user_message = request.form.get('message')

    chat = Chat.query.filter_by(id=chat_id).first()

    chat_data = json.loads(chat.chat_data)

    ai_response = chat_answer(chat.topic.title, chat.topic.description, user.name, chat.chat_data, user_message)
    j_obj = json.loads(ai_response.choices[0].message.content)

    audio_url = generate_ai_speach(j_obj["message"])

    user_answer = {
        "author": "USER",
        "message": user_message,
    }

    ai_answer = {
        "author": "AI",
        "message": j_obj["message"],
        "audio": audio_url
    }
    chat_data.append(user_answer)
    chat_data.append(ai_answer)

    chat.chat_data = str(chat_data)
    db.session.commit()

    return jsonify(answer=ai_answer), 200

@chat_blueprint.route('/chat/send/audio', methods=['POST'])
@jwt_required()
def audio():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()
    if 'file' not in request.files:
        return jsonify(message="No audio file in form"), 404
    chat_id = request.form.get('chat_id')
    file = request.files['file']

    if file.content_type not in ['audio/flac', 'audio/m4a', 'audio/mp3', 'audio/mp4', 'audio/mpeg',
                                         'audio/mpga', 'audio/oga', 'audio/ogg', 'audio/wav', 'audio/webm']:
        return jsonify(message="Unsupported file format"), 400

    #try:
    with open("chat_temp_file.mp3", "wb") as audio:
        audio.write(file.read())
    with open("chat_temp_file.mp3", "rb") as audio:
        user_message = speach_to_text(audio)

    if os.path.exists("chat_temp_file.mp3"):
        os.remove("chat_temp_file.mp3")

    chat = Chat.query.filter_by(id=chat_id).first()

    chat_data = json.loads(chat.chat_data)

    ai_response = chat_answer(chat.topic.title, chat.topic.description, user.name, chat.chat_data, user_message)
    j_obj = json.loads(ai_response.choices[0].message.content)

    audio_url = generate_ai_speach(j_obj["message"])

    user_answer = {
        "author": "USER",
        "message": user_message,
    }

    ai_answer = {
        "author": "AI",
        "message": j_obj["message"],
        "audio": audio_url
    }
    chat_data.append(user_answer)
    chat_data.append(ai_answer)

    chat.chat_data = str(chat_data)
    db.session.commit()

    return jsonify(answer=ai_answer), 200