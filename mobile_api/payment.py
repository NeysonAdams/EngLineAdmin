from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import Cource, User, Payments, Billing
from server_init import db
import hashlib
import requests
import xml.etree.ElementTree as ET

PAYMENT_HOST = "https://api.upay.uz/STAPI/STWS?wsdl=null"
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

    url = PAYMENT_HOST

    access_token = generate_md5(LOGIN+CardNumber+ExDate+PASSWORD)
    headers = {
        'Content-Type': 'text/xml;'
    }
    data = f'''
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="http://st.apus.com/">
    <soapenv:Header/>
    <soapenv:Body>
    <st:partnerRegisterCard>
    
    <partnerRegisterCardRequest>
        <StPimsApiPartnerKey>{SECRET_KEY}</StPimsApiPartnerKey>
        <AccessToken>{access_token}</AccessToken>
        <CardNumber>{CardNumber}</CardNumber>
        <ExDate>{ExDate}</ExDate>
        <Version>{Version}</Version>
        <Lang>{Lang}</Lang>
    </partnerRegisterCardRequest>
    
    </st:partnerRegisterCard>
    </soapenv:Body>
    </soapenv:Envelope>
    '''
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        code = root.find("code")
        resp = {
            "Result" : {
                "code":code,
                "Description": root.find("Description")
            }
        }
        if code == "OK":
            resp["ConfirmId"] = root.find("ConfirmId")
            resp["CardPhone"] = root.find("CardPhone")

        return jsonify(resp), 200
    else:
        print(response.status_code)
        print(response.reason)
        return jsonify(msg="Card Registration Error"), 404


@payment_blueprint.route('/payment/resend_sms', methods=['POST'])
@jwt_required()
def resend_sms():
    ConfirmId = request.form.get('ConfirmId')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST

    headers = {
        'Content-Type': 'text/xml;'
    }

    data = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="http://st.apus.com/">
        <soapenv:Header/>
        <soapenv:Body>
        <st:partnerCardResendSms>

        <partnerCardResendSmsRequest>
            <StPimsApiPartnerKey>{SECRET_KEY}</StPimsApiPartnerKey>
            <AccessToken>{generate_md5(LOGIN + ConfirmId + PASSWORD)}</AccessToken>
            <ConfirmId>{ConfirmId}</ConfirmId>
            <Version>{Version}</Version>
            <Lang>{Lang}</Lang>
        </partnerCardResendSmsRequest>

        </st:partnerCardResendSms>
        </soapenv:Body>
        </soapenv:Envelope>
        '''


    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        code = root.find("code")
        resp = {
            "Result": {
                "code": code,
                "Description": root.find("Description")
            }
        }
        if code == "OK":
            resp["ConfirmId"] = root.find("ConfirmId")
            resp["CardPhone"] = root.find("CardPhone")

        return jsonify(resp), 200
    else:
        return jsonify(msg=response.text), response.status_code


@payment_blueprint.route('/payment/confirm_card', methods=['POST'])
@jwt_required()
def confirm_card():
    ConfirmId = request.form.get('ConfirmId')
    VerifyCode = request.form.get('VerifyCode')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST

    headers = {
        'Content-Type': 'text/xml;'
    }

    data = f'''
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="http://st.apus.com/">
            <soapenv:Header/>
            <soapenv:Body>
            <st:partnerConfirmCard>

            <partnerConfirmCardRequest>
                <StPimsApiPartnerKey>{SECRET_KEY}</StPimsApiPartnerKey>
                <AccessToken>{generate_md5(LOGIN + ConfirmId + VerifyCode + PASSWORD)}</AccessToken>
                <VerifyCode>{VerifyCode}</VerifyCode>
                <Version>{Version}</Version>
                <Lang>{Lang}</Lang>
            </partnerConfirmCardRequest>

            </st:partnerConfirmCard>
            </soapenv:Body>
            </soapenv:Envelope>
            '''

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        code = root.find("code")
        resp = {
            "Result": {
                "code": code,
                "Description": root.find("Description")
            }
        }
        if code == "OK":
            resp["UzcardId"] = root.find("UzcardId")
            resp["CardPhone"] = root.find("CardPhone")
            resp["Balance"] = root.find("Balance")
            resp["CardHolder"] = root.find("CardHolder")

        return jsonify(resp), 200
    else:
        return jsonify(msg=response.text), response.status_code

@payment_blueprint.route('/payment/card_list', methods=['POST'])
@jwt_required()
def card_list():
    UzcardIds = request.form.get('UzcardIds')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST

    headers = {
        'Content-Type': 'text/xml;'
    }

    data = f'''
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="http://st.apus.com/">
                <soapenv:Header/>
                <soapenv:Body>
                <st:partnerCardList>

                <partnerCardListRequest>
                    <StPimsApiPartnerKey>{SECRET_KEY}</StPimsApiPartnerKey>
                    <AccessToken>{generate_md5(LOGIN + UzcardIds + PASSWORD)}</AccessToken>
                    <UzcardIds>{UzcardIds}</UzcardIds>
                    <Version>{Version}</Version>
                    <Lang>{Lang}</Lang>
                </partnerCardListRequest>

                </st:partnerCardList>
                </soapenv:Body>
                </soapenv:Envelope>
                '''

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        code = root.find("code")
        resp = {
            "Result": {
                "code": code,
                "Description": root.find("Description")
            }
        }
        if code == "OK":
            resp["CardList"] = []
            for sublist in root.find('CardList').findall('CardList'):
                card = {
                    "UzcardId":sublist.find('UzcardId').text,
                    "FullName":sublist.find('FullName').text,
                    "Pan":sublist.find('Pan').text,
                    "ExpireDate":sublist.find('ExpireDate').text,
                    "Phone":sublist.find('Phone').text,
                    "Balance": sublist.find('Balance').text,
                    "Sms": sublist.find('Sms').text,
                    "Status": sublist.find('Status').text,
                }
                resp["CardList"].append(card)

        return jsonify(resp), 200
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

    url = PAYMENT_HOST

    headers = {
        'Content-Type': 'text/xml;'
    }

    data = f'''
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="http://st.apus.com/">
                <soapenv:Header/>
                <soapenv:Body>
                <st:partnerPayment>

                <partnerPaymentRequest>
                    <StPimsApiPartnerKey>{SECRET_KEY}</StPimsApiPartnerKey>
                    <AccessToken>{generate_md5(LOGIN +CardPhone + UzcardIds + SEVICE_ID + PersonalAccount + AmountInTiyin + PASSWORD)}</AccessToken>
                    <UzcardIds>{UzcardIds}</UzcardIds>
                    <ServiceId>{SEVICE_ID}</ServiceId>
                    <PaymentType></PaymentType>
                    <PersonalAccount>{PersonalAccount}</PersonalAccount>
                    <RegionId></RegionId>
                    <SubRegionId></SubRegionId>
                    <AmountInTiyin>{int(AmountInTiyin)*100}</AmountInTiyin>
                    <Version>{Version}</Version>
                    <Lang>{Lang}</Lang>
                </partnerPaymentRequest>

                </st:partnerPayment>
                </soapenv:Body>
                </soapenv:Envelope>
                '''

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        code = root.find("code")
        resp = {
            "Result": {
                "code": code,
                "Description": root.find("Description")
            }
        }
        if code == "OK":
            resp["Confirmed"] = root.find("Confirmed")
            resp["TransactionId"] = root.find("TransactionId")
            resp["UzcardTransactionId"] = root.find("UzcardTransactionId")
            resp["PaymentDate"] = root.find("PaymentDate")
            resp["PaymentAmount"] = root.find("PaymentAmount")
            resp["ServiceId"] = root.find("ServiceId")
            resp["CardPan"] = root.find("CardPan")

        return jsonify(resp), 200
    else:
        return jsonify(msg=response.text), response.status_code


@payment_blueprint.route('/payment/confirm_payment', methods=['POST'])
@jwt_required()
def confirm_payment():
    ConfirmId = request.form.get('ConfirmId')
    VerifyCode = request.form.get('VerifyCode')
    Version = request.form.get('Version')
    Lang = request.form.get('Lang')

    url = PAYMENT_HOST

    headers = {
        'Content-Type': 'text/xml;'
    }

    data = f'''
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="http://st.apus.com/">
                <soapenv:Header/>
                <soapenv:Body>
                <st:partnerConfirmPayment>

                <partnerConfirmPaymentRequest>
                    <StPimsApiPartnerKey>{SECRET_KEY}</StPimsApiPartnerKey>
                    <AccessToken>{generate_md5(LOGIN + ConfirmId + VerifyCode + PASSWORD)}</AccessToken>
                    <ConfirmId>{ConfirmId}</ConfirmId>
                    <VerifyCode>{VerifyCode}</VerifyCode>
                    <Version>{Version}</Version>
                    <Lang>{Lang}</Lang>
                </partnerConfirmPaymentRequest>

                </st:partnerConfirmPayment>
                </soapenv:Body>
                </soapenv:Envelope>
                '''

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        code = root.find("code")
        resp = {
            "Result": {
                "code": code,
                "Description": root.find("Description")
            }
        }
        if code == "OK":
            resp["Confirmed"] = root.find("Confirmed")
            resp["TransactionId"] = root.find("TransactionId")
            resp["UzcardTransactionId"] = root.find("UzcardTransactionId")
            resp["PaymentDate"] = root.find("PaymentDate")
            resp["PaymentAmount"] = root.find("PaymentAmount")
            resp["ServiceId"] = root.find("ServiceId")
            resp["CardPan"] = root.find("CardPan")

        return jsonify(resp), 200
    else:
        return jsonify(msg=response.text), response.status_code


@payment_blueprint.route('/payment/get_exesize_billing', methods=['GET'])
@jwt_required()
def get_exesize_billing():

    billings = Billing.query.filter_by(type='speaking_lesson').all()

    return jsonify(billings=[i.serialize for i in billings]), 200