from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import User
from server_init import db

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



    user = User.query.filter_by(google_id=google_id).first()

    if user:
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(user.auth_setialization(access_token, refresh_token)), 200

    user = User.query.filter_by(facebook_id=facebook_id).first()

    if user:
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(user.auth_setialization(access_token, refresh_token)), 200

    new_user = User()
    new_user.google_id = google_id
    new_user.facebook_id = facebook_id
    new_user.phone_number = phone
    new_user.email = email
    new_user.level = level
    new_user.img_url = img_url

    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    return jsonify(new_user.auth_setialization(access_token, refresh_token)), 200


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

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.auth_setialization(access_token, refresh_token)), 200


@auth.route('/users/google_auth', methods=['POST'])
def google_auth():
    google_id = request.form.get('google_id')
    name = request.form.get('name')
    email = request.form.get('email')
    img_url = request.form.get('img_url')

    user = User.query.filter_by(email=email).first()

    if user:
        user.google_id = google_id
        user.login = ""
        user.name = name
        user.email = email
        user.img_url = img_url
        db.session.commit()
    else:
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            new_user = User()
            new_user.google_id = google_id
            new_user.login = ""
            new_user.name = name
            new_user.email = email
            new_user.img_url = img_url
            db.session.add(new_user)
            db.session.commit()
            user = new_user

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.auth_setialization(access_token, refresh_token)), 200

@auth.route('/users/facebook_auth', methods=['POST'])
def facebook_auth():
    facebook_id = request.form.get('facebook_id')
    name = request.form.get('name')
    email = request.form.get('email')
    img_url = request.form.get('img_url')

    user = User.query.filter_by(email=email).first()

    if user:
        user.facebook_id = facebook_id
        user.login = ""
        user.name = name
        user.email = email
        user.img_url = img_url
        db.session.commit()
    else:
        user = User.query.filter_by(facebook_id=facebook_id).first()

        if not user:
            new_user = User()
            new_user.facebook_id = facebook_id
            new_user.name = name
            new_user.email = email
            new_user.img_url = img_url
            db.session.add(new_user)
            db.session.commit()
            user = new_user

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user.auth_setialization(access_token, refresh_token)), 200






