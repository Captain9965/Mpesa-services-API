from decouple import config
from flask import Flask, Response, jsonify, request, json, Blueprint
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import pytz
from src import ResponseDump, RequestDump, db
import uuid

stkBp = Blueprint("stkPush", "stkBp", url_prefix="/stk")


@stkBp.route("/", methods=["POST"])
def make_request():
    # get the request data payload:
    request_data = request.get_json()

    # if malformed payload, return error message, else proceed:
    if ("phone" not in request_data
            or "amount" not in request_data
            or "shortcode" not in request_data
            or "AccountReference" not in request_data
            or "ApplicationId" not in request_data):
        return jsonify({
            "Success": False,
            "Message": "Malformed json payload"
        }), 400
        # check the app id against the registered valid ids before proceeding!!
    # get time:
    fmt = '%Y%m%d%H%M%S'
    tz_Nairobi = pytz.timezone('Africa/Nairobi')
    time_raw = datetime.now(tz_Nairobi)
    time = time_raw.strftime(fmt)

    # extract the data from the request:
    str_short_code = request_data.get('shortcode')
    Amount = int(request_data.get('amount'))
    phoneNumber = request_data.get('phone')
    AccountReference = str(request_data.get('AccountReference'))
    AppId = int(request_data.get('ApplicationId'))

    # get password from .env:
    mpesa_pass = str(config("MPESA_PASS_KEY"))
    short_code = int(str_short_code)

    # get the password by b64 encoding the short code + mpesa pass + time:
    str_bytes = str_short_code + mpesa_pass + time
    str_bytes = str_bytes.encode("ascii")
    password = base64.b64encode(str_bytes)
    password = password.decode("ascii")
    password = str(password)

    # get phone number to push the stk to from the request and validate it:
    """ Further validation needed
        For example: what if the phone number provided is > 12 characters long?
    """

    if not phoneNumber.startswith('254'):
        phoneNumber = '254' + str(int(phoneNumber))
    int_phoneNumber = int(phoneNumber)

    # make stk push
    try:

        # get access_token
        access_token = get_mpesa_token()

        # stk_push request url
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        # put access_token in request headers
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # define request body
        data = {
            "BusinessShortCode": short_code,
            "Password": password,
            "Timestamp": time,  # timestamp format: 20190317202903 yyyyMMhhmmss
            "TransactionType": "CustomerPayBillOnline",
            "Amount": Amount,
            "PartyA": phoneNumber,
            "PartyB": short_code,
            "PhoneNumber": int_phoneNumber,
            "CallBackURL": f"https://{str(config('MPESA_CALLBACK_URL'))}/stk/callback",
            "AccountReference": AccountReference,
            "TransactionDesc": "STK Payment"
        }

        # make request and catch response and display the error message, if any,  for debugging
        response = requests.post(api_url, json=data, headers=headers)
        jsonResponse = json.loads(response.text)
        errorMessage = jsonResponse.get('errorMessage')
        print("errorMessage-->")
        print(errorMessage)

        # check response code for errors and return response
        if response.status_code > 299:
            # store the request and the success state False:
            # in addition, store the error message for audit:
            if errorMessage is not None:
                f = RequestDump(
                    uuid_=uuid.uuid4(),
                    created_at=time_raw,
                    amount=Amount,
                    phone=phoneNumber,
                    shortcode=str_short_code,
                    accountReference=AccountReference,
                    service="STK PUSH",
                    requestStatus=False,
                    errorMessage=errorMessage,
                    appId=AppId,

                )
                db.session.add(f)
                db.session.commit()

            return jsonify({
                "success": False,
                "message": errorMessage
            }), 400

        # return the successful response to the user and store the success response:
        response_dict = json.loads(response.text)
        s = RequestDump(
            uuid_=uuid.uuid4(),
            created_at=time_raw,
            amount=Amount,
            phone=phoneNumber,
            shortcode=str_short_code,
            accountReference=AccountReference,
            service="STK PUSH",
            requestStatus=True,
            checkoutRequestId=response_dict.get('CheckoutRequestID'),
            merchantRequestId=response_dict.get('MerchantRequestID'),
            appId=AppId,

        )
        db.session.add(s)
        db.session.commit()

        return jsonify({
            "Response": json.loads(response.text)
        }), 200

    except Exception as e:
        print(e)
        # catch error and return responses:
        return jsonify({
            "success": False,
            "message": "Sorry, an unexpected exception occurred. Please contact Admin."
        }), 400


"""This is the callback url:"""

@stkBp.route("/callback", methods=["POST"])
def callbackResponse():
    callback_response = request.get_json()
    print(callback_response)
    print("Now save the response!")
    tz_Nairobi = pytz.timezone('Africa/Nairobi')
    time_raw = datetime.now(tz_Nairobi)
    # store the response:
    resp = ResponseDump(
        uuid_=uuid.uuid4(),
        payload=callback_response,
        created_at=time_raw,
        service="STK PUSH"
    )

    db.session.add(resp)
    db.session.commit()

    # send the response to the callback url:

    return jsonify("Response registered!!"), 200

@stkBp.route("/fetchAllTransactions", methods = ["GET"])
def fetchAllTransactions():
    t = RequestDump.query.all()
    if not t:
        return jsonify(
            "No transactions found"
        ), 404
    transactions = [data.serialize for data in t]
    return jsonify(transactions), 200

        


"""
delete all transactions in DB

@todo: Add an endpoint to delete specific transactions based on checkoutRequestID
use method delete?
""" 
@stkBp.route("/deleteAllTransactions", methods = ["GET"])
def deleteAllTransactions():
    t= RequestDump.query.all()
    if not t:
         return jsonify(
            "No transactions found"
        ), 404
    for field in t:   
        db.session.delete(field)
    db.session.commit()
    return jsonify(
        "All transactions deleted successfully"
    ), 200

""" Check the status of the request from Safaricom and reconcile transaction"""
@stkBp.route("/checkStatus", methods = ["POST"])
def checkTransactionStatus():
    request_data = request.get_json()

    #first validate the payload before sending the request:

    CheckoutRequestID = request_data.get('CheckoutRequestID')
    str_short_code = request_data.get('shortcode')

    #calculate the timestamp:
    fmt = '%Y%m%d%H%M%S'
    tz_Nairobi = pytz.timezone('Africa/Nairobi')
    time_raw = datetime.now(tz_Nairobi)
    time = time_raw.strftime(fmt)

    # get password from .env:
    mpesa_pass = str(config("MPESA_PASS_KEY"))
    short_code = int(str_short_code)

    # get the password by b64 encoding the short code + mpesa pass + time:
    str_bytes = str_short_code + mpesa_pass + time
    str_bytes = str_bytes.encode("ascii")
    password = base64.b64encode(str_bytes)
    password = password.decode("ascii")
    password = str(password)

     # get access_token
    access_token = get_mpesa_token()

    # stk_push request url
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"

    # put access_token in request headers
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    #data:
    data = {
        "BusinessShortCode" : short_code,
        "Password": password,
        "Timestamp": time,
        "CheckoutRequestID" : CheckoutRequestID
        
    }

    #response:
    response = requests.post(api_url, json=data, headers=headers)
    jsonResponse = json.loads(response.text)
    
    return jsonify({
        "Response":jsonResponse
    }), 200



# get Authentication token from M-pesa [function]:
def get_mpesa_token():
    consumer_key = str(config('CONSUMER_KEY'))
    consumer_secret = str(config('CONSUMER_SECRET'))
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # make a get request using python requests library
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    return r.json().get('access_token')