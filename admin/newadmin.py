from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from database.models import User, Levels
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
@role_required('superuser')
def level():
    if request.method == 'GET':
        levels = Levels.query.all()
        return  jsonify(level.serialize for level in levels), 200
    #if request.method == 'POST':