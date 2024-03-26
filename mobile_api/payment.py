from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import Cource, User, Payments, Billing
from server_init import db
import hashlib
import requests

PAYMENT_HOST = "https://api.upay.uz/STAPI/STWS?wsdl"
SECRET_KEY = "A01A0380CA3C61428C26A231F0E49A09"
SEVICE_ID = "1442"
LOGIN="engl1n3"
PASSWORD = "m7W2OK"

payment_blueprint = Blueprint('payment_bluepprint', __name__)

def generate_md5(input_string):
    md5_hash = hashlib.md5(input_string.encode()).hexdigest()
    return md5_hash

@payment_blueprint.route('/payment/card_register', methods=['POST'])
@jwt_required()
def card_registrate():
    CardNumber = request.form.get('CardNumber')
    ExDate = request.form.get('ExDate')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST+"/partnerRegisterCard"

    form_data = {
        "StPimsApiPartnerKey" : SECRET_KEY,
        "AccessToken" : generate_md5(LOGIN+CardNumber+ExDate+PASSWORD),
        "CardNumber" : CardNumber,
        "Version" : Version,
        "Lang" : Lang
    }

    response = requests.post(url, data=form_data)

    if response.status_code == 200:
        return response.text
    else:
        return jsonify(msg="Card Registration Error"), 404


@payment_blueprint.route('/payment/resend_sms', methods=['POST'])
@jwt_required()
def resend_sms():
    ConfirmId = request.form.get('ConfirmId')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST + "/partnerCardResendSms"

    form_data = {
        "StPimsApiPartnerKey": SECRET_KEY,
        "AccessToken": generate_md5(LOGIN + ConfirmId + PASSWORD),
        "ConfirmId": ConfirmId,
        "Version": Version,
        "Lang": Lang
    }

    response = requests.post(url, data=form_data)

    if response.status_code == 200:
        return response.text
    else:
        return jsonify(msg=response.text), response.status_code


@payment_blueprint.route('/payment/confirm_card', methods=['POST'])
@jwt_required()
def confirm_card():
    ConfirmId = request.form.get('ConfirmId')
    VerifyCode = request.form.get('VerifyCode')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST + "/partnerConfirmCard"

    form_data = {
        "StPimsApiPartnerKey": SECRET_KEY,
        "AccessToken": generate_md5(LOGIN + ConfirmId + VerifyCode + PASSWORD),
        "ConfirmId": ConfirmId,
        "VerifyCode": VerifyCode,
        "Version": Version,
        "Lang": Lang
    }

    response = requests.post(url, data=form_data)

    if response.status_code == 200:
        return response.text, 200
    else:
        return jsonify(msg=response.text), response.status_code

@payment_blueprint.route('/payment/card_list', methods=['POST'])
@jwt_required()
def card_list():
    UzcardIds = request.form.get('UzcardIds')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST + "/partnerCardList"

    form_data = {
        "StPimsApiPartnerKey": SECRET_KEY,
        "AccessToken": generate_md5(LOGIN + UzcardIds + PASSWORD),
        "UzcardIds": UzcardIds,
        "Version": Version,
        "Lang": Lang
    }

    response = requests.post(url, data=form_data)

    if response.status_code == 200:
        return response.text, 200
    else:
        return jsonify(msg=response.text), response.status_code

@payment_blueprint.route('/payment/payment', methods=['POST'])
@jwt_required()
def payment():
    UzcardIds = request.form.get('UzcardIds')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')
    BillingId = request.form.get('BillingId')
    AmountInTiyin = request.form.get('AmountInTiyin')
    CardPhone = request.form.get('CardPhone')

    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()
    if not user:
        return jsonify(msg="Mo user"), 400

    billing = Billing.query.filter_by(id=BillingId).first()

    payment = Payments()
    payment.user = user
    payment.billing = billing

    db.session.add(payment)
    db.session.commit()

    PersonalAccount = payment.id

    url = PAYMENT_HOST + "/partnerPayment"

    form_data = {
        "StPimsApiPartnerKey": SECRET_KEY,
        "AccessToken": generate_md5(LOGIN +CardPhone + UzcardIds + SEVICE_ID + PersonalAccount + AmountInTiyin + PASSWORD),
        "UzcardIds": UzcardIds,
        "ServiceId": SEVICE_ID,
        "PaymentType":"",
        "PersonalAccount":PersonalAccount,
        "RegionId":"",
        "SubRegionId":"",
        "AmountInTiyin": int(AmountInTiyin)*100,
        "Version": Version,
        "Lang": Lang
    }

    response = requests.post(url, data=form_data)

    if response.status_code == 200:
        return response.text, 200
    else:
        return jsonify(msg=response.text), response.status_code


@payment_blueprint.route('/payment/confirm_payment', methods=['POST'])
@jwt_required()
def confirm_payment():
    ConfirmId = request.form.get('ConfirmId')
    VerifyCode = request.form.get('VerifyCode')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST + "/partnerConfirmPayment"

    form_data = {
        "StPimsApiPartnerKey": SECRET_KEY,
        "AccessToken": generate_md5(LOGIN + ConfirmId + VerifyCode + PASSWORD),
        "ConfirmId": ConfirmId,
        "VerifyCode": VerifyCode,
        "Version": Version,
        "Lang": Lang
    }

    response = requests.post(url, data=form_data)

    if response.status_code == 200:
        return response.text, 200
    else:
        return jsonify(msg=response.text), response.status_code