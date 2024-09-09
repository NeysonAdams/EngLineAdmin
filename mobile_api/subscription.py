from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import User, Lesson, Inputquestion, Videoquestion, Subscription, Promo
from server_init import db
from config import ENKRKEY

import hashlib
import datetime
import json

subscription_blueprint = Blueprint('subscription_blueprint', __name__)


def encrypt(string: str, key1: str, key2: int) -> str:
    encrypted_chars = []
    for i, char in enumerate(string):
        # Шифруем символ, используя два ключа последовательно
        encrypted_char = chr(ord(char) ^ key1)  # XOR с первым ключом
        encrypted_char = chr(ord(encrypted_char) ^ key2)  # XOR со вторым ключом
        encrypted_chars.append(encrypted_char)
    return ''.join(encrypted_chars)

def decrypt(encrypted_string: str, key1: int, key2: int) -> str:
    decrypted_chars = []
    for i, char in enumerate(encrypted_string):
        # Расшифровываем символы, используя два ключа в обратном порядке
        decrypted_char = chr(ord(char) ^ key2)  # XOR со вторым ключом
        decrypted_char = chr(ord(decrypted_char) ^ key1)  # XOR с первым ключом
        decrypted_chars.append(decrypted_char)
    return ''.join(decrypted_chars)

def generate_unique_code(email: str) -> str:
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    base_string = email + current_date

    hash_object = hashlib.sha256(base_string.encode())

    unique_code = hash_object.hexdigest()[:15]

    return unique_code


def add_months(source_date, months):
    # Получаем новый месяц и год
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1

    # Корректируем день, если результат выходит за пределы месяца
    day = min(source_date.day,
              [31, 29 if year % 4 == 0 and year % 100 != 0 or year % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31,
               30, 31][month - 1])

    return datetime(year, month, day)

def addSubscription(user:User, type:str, payment:str):

    current_date = datetime.datetime.now()
    s = Subscription.query.filter_by(user_id=user.id, is_active=True).first()

    if s.type == "SUB":
        if s.is_active:
            current_date = s.expiration_date
        db.session.delete(s)
    else:
        return None,  False

    if type == "MONTH" or type == "SUB":
        current_date = add_months(current_date, 1)
    elif type == "3MONTH":
        current_date = add_months(current_date, 3)
    elif type == "YEAR":
        current_date = add_months(current_date, 12)

    subscription = Subscription()
    subscription.type = type
    subscription.code = generate_unique_code(user.email)
    subscription.expiration_date = current_date
    subscription.is_active = True
    subscription.user_id =user.id
    subscription.paymentdata = payment
    subscription.status = "ACTIVE"

    db.session.add(subscription)
    db.session.commit()

    return subscription, True

@subscription_blueprint.route('/subscription/create', methods=['POST'])
@jwt_required()
def create():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    type = request.form.get('type')
    paymentdata = request.form.get('paymentdata')

    if not user:
        return jsonify(msg="No user"), 400

    subscription, is_created = addSubscription(user, type, paymentdata)

    if not is_created:
        return jsonify(msg="This User Have Subscription"), 404

    return jsonify(subscription.serialize), 200

@subscription_blueprint.route('/subscription/validate', methods=['POST'])
@jwt_required()
def validate():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    code = request.form.get('code')

    if not user:
        return jsonify(msg="No user"), 400

    subscription = Subscription.query.filter_by(code=code).first()

    if subscription.user_id != user.id:
        return jsonify(msg="User validation failed"), 404

    if not subscription.is_active:
        return jsonify(msg="User validation failed"), 404

    return jsonify(msg="Active"), 200


@subscription_blueprint.route('/subscription/update', methods=['POST'])
@jwt_required()
def update():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    code = request.form.get('code')

    subscription = Subscription.query.filter_by(code=code).first()

    if not user:
        return jsonify(msg="No user"), 400

    current_date = datetime.datetime.now()

    if subscription.type == "MONTH":
        current_date = add_months(current_date, 1)
    elif subscription.type == "3MONTH":
        current_date = add_months(current_date, 3)
    elif subscription.type == "YEAR":
        current_date = add_months(current_date, 12)

    subscription.expiration_date = current_date
    subscription.is_active = True

    db.session.commit()

    return jsonify(msg="Updated"), 200


@subscription_blueprint.route('/subscription/cancel', methods=['POST'])
@jwt_required()
def cancel():

    code = request.form.get('code')
    subscription = Subscription.query.filter_by(code=code).first()

    if not subscription:
        return jsonify(msg="Have no subscription"), 404

    db.session.delete(subscription)

    return jsonify(msg="Subscription Deleted"), 200


def compare_dates(date1: datetime, date2: datetime) -> bool:
    date1_plus_3_months = add_months(date1, 3)
    return date2 >= date1_plus_3_months
def subscriptionUpdate(app):

    subscriptions = Subscription.query.all()
    current_date = datetime.datetime.now()

    for subscription in subscriptions:
        if subscription.is_active:
            if current_date > subscription.expiration_date:
                if subscription.paymentdata == "":
                    subscription.is_active = False
                    db.session.delete(subscription)
                else:
                    user = User.query.filter_by(id=subscription.user_id).first()
                    payment = json.loads(decrypt(ENKRKEY, user.id))
                    with app.test_client() as client:
                        response = client.post('/payment/payment',  data=payment, content_type='application/x-www-form-urlencoded')

                        if response.status_code == 200:
                            subscription.is_active = True
                            if subscription.type == "MONTH" or subscription.type == "SUB":
                                subscription.expiration_date = add_months(current_date, 1)
                            elif subscription.type == "3MONTH":
                                subscription.expiration_date = add_months(current_date, 3)
                            elif subscription.type == "YEAR":
                                subscription.expiration_date = add_months(current_date, 12)
                            subscription.status = "ACTIVE"
                        else:
                            subscription.is_active = False
                            subscription.status = "ONHOLD"
        else:
            if compare_dates(subscription.expiration_date, current_date):
                db.session.delete(subscription)

    db.session.commit()

@subscription_blueprint.route('/promo/validate', methods=['POST'])
@jwt_required()
def validate_promo():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    code = request.form.get('code')

    if not user:
        return jsonify(msg="No user"), 400

    promo = Promo.query.filter_by(code=code).first()

    if not promo:
        return jsonify(msg="Pro Code Not Found"), 404

    if  promo.type == "SINGLE":
        if promo.is_active:
            return jsonify(msg="Pro Code Still Activated"), 404
        if user not in promo.users:
            return jsonify(msg="Pro Code not for this user"), 404
        promo.is_active = True
        db.session.commit()
        subscription, is_created = addSubscription(user, "MONTH", "")
        if is_created:
            return jsonify(subscription), 200


    if promo.type == "MULTY":
        if promo.max_count == promo.current_count:
            return jsonify(msg="Pro Code Expired"), 404
        else:
            promo.current_count = promo.current_count + 1
            promo.users.append(user)
            db.session.commit()
            subscription, is_created = addSubscription(user, "MONTH", "")
            if is_created:
                return jsonify(subscription), 200

    if promo.type == "MULTYNONE":
        if promo.max_count == promo.current_count:
            return jsonify(msg="Pro Code Expired"), 404
        else:
            promo.current_count = promo.current_count + 1
            promo.users.append(user)
            db.session.commit()
            return jsonify(msg="Pro Code Activated"), 200
