from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.models import User
from flask_security.utils import hash_password
from server_init import db

profile = Blueprint('profile', __name__)

@profile.route('/profile/change_password', methods=['POST'])
@jwt_required()
def change_password():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')

    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify(msg="No user"), 404

    if user.password != hash_password(old_password):
        return jsonify(msg="Old password is wrong"), 400

    user.password = hash_password(new_password)
    db.session.commit()
    return jsonify(msg="Success"), 200