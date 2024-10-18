from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import User, Subscription, Devices
from server_init import db
from flask_security.utils import hash_password, verify_password
from twilio.rest import Client
from mobile_api.subscription import addSubscription

from config import TWILLIO_KEY, TWILlIO_SID, TWILLIO_SMS

client = Client(TWILlIO_SID, TWILLIO_KEY)

auth = Blueprint('auth', __name__)

@auth.route('/users/get_user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify(msg="No user"), 404
    return jsonify(user.serialize), 200

@auth.route('/users/create_user', methods=['POST'])
def create_user():
    google_id = request.form.get('google_id')
    facebook_id = request.form.get('facebook_id')
    phone = request.form.get('phone')
    email = request.form.get('email')
    level = request.form.get('level')
    img_url = request.form.get('img_url')
    udid = request.form.get('udid')


    user = User.query.filter_by(google_id=google_id).first()

    devices = Devices.query.filter_by(udid=udid).first()

    if user:
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(user.auth_serialization(access_token, refresh_token)), 200

    user = User.query.filter_by(facebook_id=facebook_id).first()

    if user:
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        subscription = Subscription.query.filter_by(user_id=user.id).first()

        return jsonify(user.auth_serialization(access_token, refresh_token, subscription)), 200


    if devices and devices.email != email:
        return jsonify(msg="This device already added"), 404

    if not devices:
        device = Devices(
            udid = udid,
            email=email
        )
        db.session.add(device)

    new_user = User()
    new_user.login = ""
    new_user.google_id = google_id
    new_user.facebook_id = facebook_id
    new_user.phone_number = phone
    new_user.email = email
    new_user.level = level
    new_user.img_url = img_url
    new_user.experiance = 0
    new_user.current_level = 1

    db.session.add(new_user)
    db.session.commit()

    subscription, created = addSubscription(user, "SUB", "")

    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    return jsonify(new_user.auth_serialization(access_token, refresh_token, subscription)), 200


@auth.route('/users/set_name', methods=['POST'])
@jwt_required()
def set_name():
    user_id = get_jwt_identity()
    name = request.form.get('name')
    #login = request.form.get('login')

    user = User.query.filter_by(id=user_id).first()

    user.name = name
    #user.login = login

    db.session.commit()

    return jsonify(user.serialize), 200

@auth.route('/users/set_level', methods=["POST"])
@jwt_required()
def set_level():
    user_id = get_jwt_identity()
    level = request.form.get('level')
    user = User.query.filter_by(id=user_id).first()

    levels = {
        "Beginner": 1,
        "Elementary": 2,
        "Pre-Intermediate": 3,
        "Intermediate": 4,
        "Pre-Advanced": 5,
        "Advanced": 6
    }

    user.level = levels[level]
    db.session.commit()

    return jsonify(user.serialize), 200


@auth.route('/users/refresh_token', methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=user_id),
        'refresh_token': create_refresh_token(identity=user_id)
    }
    return jsonify(ret), 200

@auth.route('/users/auth_login', methods=['GET'])
@jwt_required()
def login():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()

    if not user:
        return jsonify(msg="User is not exist"), 401

    subscription = Subscription.query.filter_by(user_id=user.id).first()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.auth_serialization(access_token, refresh_token, subscription, True)), 200

@auth.route('/users/apple_auth', methods=['POST'])
def apple_auth():
    google_id = request.form.get('id')
    name = request.form.get('name')
    email = request.form.get('email')

    subscription = None
    user = User.query.filter_by(email=email).first()
    isRegistrated = False
    if user:
        isRegistrated = True
        user.google_id = google_id
        user.login = ""
        user.name = name
        user.email = email
        user.img_url = ""
        db.session.commit()
        subscription = Subscription.query.filter_by(user_id=user.id).first()
    else:
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            new_user = User()
            new_user.google_id = google_id
            new_user.login = ""
            new_user.name = name
            new_user.email = email
            new_user.img_url = ""
            new_user.experiance = 0
            new_user.current_level = 1
            db.session.add(new_user)
            db.session.commit()
            user = new_user
            subscription, created = addSubscription(user, "SUB", "")

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.auth_serialization(access_token, refresh_token, subscription, isRegistrated)), 200

@auth.route('/users/google_auth', methods=['POST'])
def google_auth():
    google_id = request.form.get('google_id')
    name = request.form.get('name')
    email = request.form.get('email')
    img_url = request.form.get('img_url')
    subscription = None
    user = User.query.filter_by(email=email).first()
    isRegistrated = False
    if user:
        isRegistrated = True
        user.google_id = google_id
        user.login = ""
        user.name = name
        user.email = email
        user.img_url = img_url
        db.session.commit()
        subscription = Subscription.query.filter_by(user_id=user.id).first()
    else:
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            new_user = User()
            new_user.google_id = google_id
            new_user.login = ""
            new_user.name = name
            new_user.email = email
            new_user.img_url = img_url
            new_user.experiance = 0
            new_user.current_level = 1
            db.session.add(new_user)
            db.session.commit()
            user = new_user
            subscription, created = addSubscription(user, "SUB", "")

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.auth_serialization(access_token, refresh_token, subscription, isRegistrated)), 200

@auth.route('/users/facebook_auth', methods=['POST'])
def facebook_auth():
    facebook_id = request.form.get('facebook_id')
    name = request.form.get('name')
    email = request.form.get('email')
    img_url = request.form.get('img_url')
    subscription = None
    user = User.query.filter_by(email=email).first()
    isRegistrated = False
    if user:
        isRegistrated = True
        user.facebook_id = facebook_id
        user.login = ""
        user.name = name
        user.email = email
        user.img_url = img_url
        db.session.commit()
        subscription = Subscription.query.filter_by(user_id=user.id).first()
    else:
        user = User.query.filter_by(facebook_id=facebook_id).first()

        if not user:
            new_user = User()
            new_user.facebook_id = facebook_id
            new_user.name = name
            new_user.login = name
            new_user.email = email
            new_user.img_url = img_url
            new_user.experiance = 0
            new_user.current_level = 1
            db.session.add(new_user)
            db.session.commit()
            user = new_user
            subscription, created = addSubscription(user, "SUB", "")

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.auth_serialization(access_token, refresh_token, subscription, isRegistrated)), 200

@auth.route('/users/authintification', methods=["POST"])
def authintification():

    login = request.form.get('login')
    password = request.form.get('password')

    user = User.query.filter_by(email=login).first()

    if not user:
        user = User.query.filter_by(phone_number=login).first()

    if not user:
        return jsonify(msg="User is not exist"), 404

    if not verify_password(password, user.password):
        return jsonify(msg="Wrong password"), 404

    subscription = Subscription.query.filter_by(user_id=user.id).first()
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.auth_serialization(access_token, refresh_token, subscription)), 200


@auth.route('/users/registrate', methods=["POST"])
def registrate():
    email = request.form.get('email')
    phone_number=request.form.get('phone_number')
    name=request.form.get('user_name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify(msg="User email already exist"), 404

    user = User.query.filter_by(phone_number=phone_number).first()

    if user:
        return jsonify(msg="User phone already exist"), 404

    new_user = User()
    new_user.email = email
    new_user.name = name
    new_user.phone_number = phone_number
    new_user.password=hash_password(password)
    new_user.level = 0
    new_user.login = name
    new_user.experiance = 0
    new_user.current_level = 1

    db.session.add(new_user)
    db.session.commit()

    subscription, created = addSubscription(new_user, "SUB", "")

    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    return jsonify(new_user.auth_serialization(access_token, refresh_token, subscription)), 200


@auth.route('/users/verify_number', methods=["POST"])
def verify_number():
    phone_number=request.form.get('phone_number')
    code=request.form.get('code')

    verify_status = client.verify.v2.services(TWILLIO_SMS).verification_checks.create(to=phone_number, code=code)

    return jsonify(verif=verify_status.valid), 200

@auth.route('/users/start_change_password', methods=["POST"])
def start_change_password():
    if 'email' in request.form:
        to = request.form.get('email')

        user = User.query.filter_by(email=to).first()
        if not user:
            return jsonify(msg="User not exist"), 404
        chanel="email"
    else:
        to = request.form.get('phone_number')
        user = User.query.filter_by(phone_number=to).first()
        if not user:
            return jsonify(msg="User not exist"), 404
        chanel="sms"

    client.verify.v2.services(TWILLIO_SMS).verifications.create(to=to, channel=chanel)

    return jsonify(msg="succes"), 200


@auth.route('/users/change_password_verify', methods=["POST"])
def change_password_verify():
    if 'email' in request.form:
        to = request.form.get('email')
        user = User.query.filter_by(email=to).first()
    else:
        to = request.form.get('phone_number')
        user = User.query.filter_by(phone_number=to).first()
        to="+"+to

    code = request.form.get('code')

    verify_status = client.verify.v2.services(TWILLIO_SMS).verification_checks.create(to=to, code=code)

    if verify_status.valid:
        return jsonify(msg="succes"), 200
    else:
        return jsonify(msg="Verification Failed"), 404

@auth.route('/users/change_password', methods=["POST"])
def change_password():
    if 'email' in request.form:
        to = request.form.get('email')
        user = User.query.filter_by(email=to).first()
    else:
        to = request.form.get('phone_number')
        user = User.query.filter_by(phone_number=to).first()
    new_password = request.form.get('new_password')

    if not user:
        return jsonify(msg="User not exist"),404

    user.password = hash_password(new_password)
    db.session.commit()

    return jsonify(msg="succes"), 200

#@auth.route('/users/auth_login', methods=['GET'])
#@jwt_required()
#def login():
#    uid = get_jwt_identity()