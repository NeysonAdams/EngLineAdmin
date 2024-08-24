from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from database.models import User, Cource
from flask_security.utils import hash_password
from server_init import db
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

            if user.role != required_role:
                return jsonify({"msg": "Insufficient role"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

@newadmin.route('/admin/api/users', methods=['GET', 'POST', 'PUT'])
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
@role_required('superuser')
def deleteUser(id):
    user = User.query.filter_by(id=id).first()

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"User {id} has been deleted"}), 200

@newadmin.route('/admin/api/cources', methods=['GET', 'POST', 'PUT'])
@role_required('superuser')
def cources():
    if request.method == 'GET':
        cources = Cource.query.all()
        return jsonify([cource.serialize for cource in cources]), 200

