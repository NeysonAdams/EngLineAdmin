from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import Question, Subscription, User, Englishword, db

others_blue_print = Blueprint('others_blue_print', __name__)

@others_blue_print.route('/others/test', methods=['GET'])
@jwt_required()
def test():

    questions = []

    for i in range(1, 6):
        query_quest = Question.query.filter_by(var_dif=i).limit(10).all()
        for question in query_quest:
            questions.append(question.serialize)

    return jsonify(questions=questions), 200

@others_blue_print.route('/others/subscriptions', methods=['GET'])
@jwt_required()
def subscriptions():
    subscriptions = Subscription.query.all()
    return jsonify(subscriptions= [i.serialize for i in subscriptions]), 200

@others_blue_print.route('/others/addwords', methods=['GET'])
@jwt_required()
def addwords():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    words = request.form.get('words')

    if not user:
        return jsonify(message="User not exist"), 400

    words = words.split(',')

    for word in words:
        eng_word = Englishword.query.filter_by(word=word).first()
        if eng_word:
            user.dictionary.append(eng_word)

    db.session.commit()

    return jsonify(message="Words added"), 200



