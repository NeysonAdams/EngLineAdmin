import os

from flask import Blueprint, request, jsonify,send_from_directory
from database.models import Exesize, Levels, Exesesizes, Question, Inputquestion, Audioquestion, Wordexecesize, Wordslink
from server_init import db
from sqlalchemy import func
from werkzeug.utils import secure_filename

free_blueprint = Blueprint('free_blueprint', __name__)

AUDIO_FOLDER = os.path.join(os.getcwd(), 'static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@free_blueprint.route('/free/audio/list', methods=['GET'])
def list_audio_files():
    files = [f for f in os.listdir(AUDIO_FOLDER) if os.path.isfile(os.path.join(AUDIO_FOLDER, f))]
    return jsonify({"files": files})

@free_blueprint.route('/free/audio/download/<filename>', methods=['GET'])
def download_audio_file(filename):
    return send_from_directory(AUDIO_FOLDER, filename, as_attachment=True)

@free_blueprint.route('/free/audio/upload', methods=['POST'])
def upload_audio_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file.save(os.path.join(AUDIO_FOLDER, filename))
    return jsonify({"message": f"File '{filename}' uploaded successfully"})

@free_blueprint.route('/free/levels', methods=['GET'])
def get_max_level_by_language():
    language = request.args.get("language")

    if not language:
        return jsonify({"error": "Missing language parameter"}), 400

    max_level = (
        Levels.query
        .with_entities(func.max(Levels.number))
        .filter(Levels.language == language)
        .scalar()
    )
    if max_level is None:
        return jsonify({"error": "No levels found for this language"}), 404

    return jsonify({"max_level": max_level})

@free_blueprint.route('/free/add', methods=['POST'])
def level():
    data = request.get_json()

    level = Levels()
    level.number = data.get('number')
    level.language = data.get('language')
    db.session.add(level)

    for package in data.get('exesizes', []):
        exesizes = Exesesizes()
        exesizes.name = package['name']
        exesizes.type = package['type']
        exesizes.level = package["level"]
        exesizes.lenguage = data.get('language')
        db.session.add(exesizes)

        for exec in package['exesize']:
            exesize = Exesize()
            exesize.type = exec['type']
            exesize.level = package["level"]
            db.session.add(exesize)

            if exec['type'] == 'test_question':
                q = exec['question']
                question = Question(
                    question=q['question'],
                    var1=q['test_answers'][0],
                    var2=q['test_answers'][1],
                    var3=q['test_answers'][2],
                    var4=q['test_answers'][3],
                    right_var=q['right_var']
                )
                db.session.add(question)
                exesize.question = question

            elif exec['type'] == 'input_question':
                iq = exec['inputquestion']
                inputquestion = Inputquestion(
                    question=iq['question'],
                    answer=iq['answer'],
                    type=iq['type'],
                    isrecord=iq['isrecord']
                )
                db.session.add(inputquestion)
                exesize.input = inputquestion

            elif exec['type'] == 'audio_question':
                a = exec['audio']
                audio = Audioquestion(
                    question=a['question'],
                    audio_query=a['audio_query'],
                    audio_url=a['audio_url'],
                    isrecord=a['isrecord']
                )
                db.session.add(audio)
                exesize.audio = audio

            elif exec['type'] == 'word_pair_exesize':
                wordex = Wordexecesize()
                db.session.add(wordex)

                for word in exec['word_ex']['words']:
                    w = Wordslink(
                        eng_word=word["eng"],
                        rus_word=word["rus"],
                        uzb_word=word["uzb"]
                    )
                    db.session.add(w)
                    wordex.wordslink.append(w)

                exesize.wordexecesize = wordex

            exesizes.exesize.append(exesize)

        level.exesizes_link.append(exesizes)

    db.session.commit()
    return jsonify(level.serialize_max), 200




