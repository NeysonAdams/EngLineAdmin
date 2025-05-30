import os

from flask import Blueprint, request, jsonify
from database.models import Exesize, Levels, Exesesizes
from server_init import db

free_blueprint = Blueprint('free_blueprint', __name__)

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

                if not exesize:
                    exesize = Exesize()
                    exesize.type = exec['type']
                    exesize.level = package["level"]

                    db.session.add(exesize)
                    db.session.commit()

                if exec['type'] == 'test_question':
                    if exec['question']['id'] == -1:
                        question = Question()
                        question.question = exec['question']['question']
                        question.var1 = exec['question']['test_answers'][0]
                        question.var2 = exec['question']['test_answers'][1]
                        question.var3 = exec['question']['test_answers'][2]
                        question.var4 = exec['question']['test_answers'][3]
                        question.right_var = exec['question']['right_var']

                        db.session.add(question)
                        db.session.commit()

                        exesize.question = question
                        db.session.commit()
                    else:
                        exesize.question.question = exec['question']['question']
                        exesize.question.var1 = exec['question']['test_answers'][0]
                        exesize.question.var2 = exec['question']['test_answers'][1]
                        exesize.question.var3 = exec['question']['test_answers'][2]
                        exesize.question.var4 = exec['question']['test_answers'][3]
                        exesize.question.right_var = exec['question']['right_var']
                        db.session.commit()

                if exec['type'] == 'input_question':
                    if exec['inputquestion']['id'] == -1:
                        inputquestion = Inputquestion()
                        inputquestion.question = exec['inputquestion']['question']
                        inputquestion.answer = exec['inputquestion']['answer']
                        inputquestion.type = exec['inputquestion']['type']
                        inputquestion.isrecord = exec['inputquestion']['isrecord']

                        db.session.add(inputquestion)
                        db.session.commit()

                        exesize.input = inputquestion
                        db.session.commit()
                    else:
                        exesize.input.question = exec['inputquestion']['question']
                        exesize.input.answer = exec['inputquestion']['answer']
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

                    exesize.audio = audio
                    db.session.commit()

                if exec['type'] == 'word_pair_exesize':
                    wordex = Wordexecesize.query.filter_by(id=exec['word_ex']['id']).first()

                    if not wordex:
                        wordex = Wordexecesize()
                        db.session.add(wordex)

                    for word in exec['word_ex']['words']:
                        w = Wordslink.query.filter_by(id=word["id"]).first()

                        if not w:
                            w = Wordslink(
                                eng_word=word["eng"],
                                rus_word=word["rus"],
                                uzb_word=word["uzb"]
                            )
                            db.session.add(w)
                            db.session.commit()
                            wordex.wordslink.append(w)

                        else:
                            w.eng_word = word["eng"]
                            w.rus_word = word["rus"]
                            w.uzb_word = word["uzb"]
                            db.session.commit()


                    exesize.wordexecesize = wordex
                    db.session.commit()

                exesizes.exesize.append(exesize)

            level.exesizes_link.append(exesizes)

        db.session.commit()
        return jsonify(level.serialize_max), 200

