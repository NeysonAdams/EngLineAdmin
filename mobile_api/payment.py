from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import Cource, User, Payments, Billing
from server_init import db
import hashlib
import requests
import xml.etree.ElementTree as ET

PAYMENT_HOST = ""
SECRET_KEY = ""
SEVICE_ID = ""
LOGIN=""
PASSWORD = ""

payment_blueprint = Blueprint('payment_bluepprint', __name__)

namespaces = {
    'S': 'http://schemas.xmlsoap.org/soap/envelope/',
    'ns2': 'http://st.apus.com/'
}

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
    print(data)
    response = requests.post(url, headers=headers, data=data)
    print(response.text)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        code = root.find('.//ns2:partnerRegisterCardResponse//Result/code', namespaces).text
        description = root.find('.//ns2:partnerRegisterCardResponse//Result/Description', namespaces).text

        resp = {
            "Result" : {
                "code":code,
                "Description": description
            }
        }
        if code == "OK":
            resp["ConfirmId"] = root.find(".//ns2:partnerRegisterCardResponse//ConfirmId", namespaces).text
            resp["CardPhone"] = root.find(".//ns2:partnerRegisterCardResponse//CardPhone", namespaces).text

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

    print (data)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)

        print(response.text)
        code = root.find('.//ns2:partnerCardResendSmsResponse//Result/code', namespaces).text
        description = root.find('.//ns2:partnerCardResendSmsResponse//Result/Description', namespaces).text
        resp = {
            "Result": {
                "code": code,
                "Description": description
            }
        }
        if code == "OK":
            resp["ConfirmId"] = root.find(".//ns2:partnerCardResendSmsResponse//ConfirmId", namespaces).text
            resp["CardPhone"] = root.find(".//ns2:partnerCardResendSmsResponse//CardPhone", namespaces).text

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

    print(ConfirmId)

    headers = {
        'Content-Type': 'text/xml;'
    }
    print(f"{LOGIN}{ConfirmId}{VerifyCode}{PASSWORD}")
    data = f'''
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="http://st.apus.com/">
            <soapenv:Header/>
            <soapenv:Body>
            <st:partnerConfirmCard>

            <partnerConfirmCardRequest>
                <StPimsApiPartnerKey>{SECRET_KEY}</StPimsApiPartnerKey>
                <AccessToken>{generate_md5(f"{LOGIN}{ConfirmId}{VerifyCode}{PASSWORD}")}</AccessToken>
                <ConfirmId>{ConfirmId}</ConfirmId>
                <VerifyCode>{VerifyCode}</VerifyCode>
                <Version>{Version}</Version>
                <Lang>{Lang}</Lang>
            </partnerConfirmCardRequest>

            </st:partnerConfirmCard>
            </soapenv:Body>
            </soapenv:Envelope>
            '''

    print (data)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        print(response.text)
        code = root.find('.//ns2:partnerConfirmCardResponse//Result/code', namespaces).text
        description = root.find('.//ns2:partnerConfirmCardResponse//Result/Description', namespaces).text
        resp = {
            "Result": {
                "code": code,
                "Description": description
            }
        }
        if code == "OK":
            resp["UzcardId"] = root.find('.//ns2:partnerConfirmCardResponse//UzcardId', namespaces).text
            resp["CardPhone"] = root.find('.//ns2:partnerConfirmCardResponse//CardPhone', namespaces).text
            resp["Balance"] = root.find('.//ns2:partnerConfirmCardResponse//Balance', namespaces).text
            resp["CardHolder"] = root.find('.//ns2:partnerConfirmCardResponse//CardHolder', namespaces).text

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
                    <CardList>{UzcardIds}</CardList>
                    <Version>{Version}</Version>
                    <Lang>{Lang}</Lang>
                </partnerCardListRequest>

                </st:partnerCardList>
                </soapenv:Body>
                </soapenv:Envelope>
                '''
    print(data)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        print(response.text)
        code = root.find('.//ns2:partnerCardListResponse//Result/code', namespaces).text
        description = root.find('.//ns2:partnerCardListResponse//Result/Description', namespaces).text
        resp = {
            "Result": {
                "code": code,
                "Description": description
            }
        }
        if code == "OK":
            resp["CardList"] = []
            cardList = root.find('.//ns2:partnerCardListResponse//CardList', namespaces)
            for sublist in cardList.findall('CardList'):
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
    AmountInTiyin = int(request.form.get('AmountInTiyin'))*100
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
    print(f"{LOGIN}{CardPhone}{UzcardIds}{SEVICE_ID}{PersonalAccount}{AmountInTiyin}{PASSWORD}")
    data = f'''
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:st="http://st.apus.com/">
                <soapenv:Header/>
                <soapenv:Body>
                <st:partnerPayment>

                <partnerPaymentRequest>
                    <StPimsApiPartnerKey>{SECRET_KEY}</StPimsApiPartnerKey>
                    <AccessToken>{generate_md5(f"{LOGIN}{CardPhone}{UzcardIds}{SEVICE_ID}{PersonalAccount}{AmountInTiyin}{PASSWORD}")}</AccessToken>
                    <CardPhone>{CardPhone}</CardPhone>
                    <UzcardId>{UzcardIds}</UzcardId>
                    <ServiceId>{SEVICE_ID}</ServiceId>
                    <PaymentType></PaymentType>
                    <PersonalAccount>{PersonalAccount}</PersonalAccount>
                    <RegionId></RegionId>
                    <SubRegionId></SubRegionId>
                    <AmountInTiyin>{int(AmountInTiyin)}</AmountInTiyin>
                    <Version>{Version}</Version>
                    <Lang>{Lang}</Lang>
                </partnerPaymentRequest>

                </st:partnerPayment>
                </soapenv:Body>
                </soapenv:Envelope>
                '''

    response = requests.post(url, headers=headers, data=data)

    print(data)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        code = root.find('.//ns2:partnerPaymentResponse//Result/code', namespaces).text
        description = root.find('.//ns2:partnerPaymentResponse//Result/Description', namespaces).text
        resp = {
            "Result": {
                "code": code,
                "Description": description
            }
        }
        if code == "OK":
            try:
                resp["ConfirmId"] = root.find('.//ns2:partnerConfirmPaymentResponse//ConfirmId', namespaces).text
            except:
                pass
            resp["Confirmed"] = root.find('.//ns2:partnerPaymentResponse//Confirmed', namespaces).text
            resp["TransactionId"] = root.find('.//ns2:partnerPaymentResponse//TransactionId', namespaces).text
            resp["UzcardTransactionId"] = root.find('.//ns2:partnerPaymentResponse//UzcardTransactionId', namespaces).text
            resp["PaymentDate"] = root.find('.//ns2:partnerPaymentResponse//PaymentDate', namespaces).text
            resp["PaymentAmount"] = root.find('.//ns2:partnerPaymentResponse//PaymentAmount', namespaces).text
            resp["ServiceId"] = root.find('.//ns2:partnerPaymentResponse//ServiceId', namespaces).text
            resp["CardPan"] = root.find('.//ns2:partnerPaymentResponse//CardPan', namespaces).text

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
        code = root.find('.//ns2:partnerConfirmPaymentResponse//Result/code', namespaces).text
        description = root.find('.//ns2:partnerConfirmPaymentResponse//Result/Description', namespaces).text
        resp = {
            "Result": {
                "code": code,
                "Description": description
            }
        }
        if code == "OK":
            resp["Confirmed"] = root.find('.//ns2:partnerConfirmPaymentResponse//Confirmed', namespaces).text
            resp["TransactionId"] = root.find('.//ns2:partnerConfirmPaymentResponse//TransactionId', namespaces).text
            resp["UzcardTransactionId"] = root.find('.//ns2:partnerConfirmPaymentResponse//UzcardTransactionId', namespaces).text
            resp["PaymentDate"] = root.find('.//ns2:partnerConfirmPaymentResponse//PaymentDate', namespaces).text
            resp["PaymentAmount"] = root.find('.//ns2:partnerConfirmPaymentResponse//PaymentAmount', namespaces).text
            resp["ServiceId"] = root.find('.//ns2:partnerConfirmPaymentResponse//ServiceId', namespaces).text
            resp["CardPan"] = root.find('.//ns2:partnerConfirmPaymentResponse//CardPan', namespaces).text

        return jsonify(resp), 200
    else:
        return jsonify(msg=response.text), response.status_code


@payment_blueprint.route('/payment/get_exesize_billing', methods=['GET'])
@jwt_required()
def get_exesize_billing():

    billings = Billing.query.filter_by(type='speaking_lesson').all()

    return jsonify(billings=[i.serialize for i in billings]), 200