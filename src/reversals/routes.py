from decouple import config
from flask import Flask, Response, jsonify, request, json, Blueprint
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import pytz
from src import ResponseDump, StkRequestDump, db
import uuid

reversalsBp = Blueprint("reversals", "reversalsBp", url_prefix="/reversals")

@reversalsBp.route("/", methods = ["POST"])
def make_request():
    request_data = request.get_json()

    #debug:
    print(request_data)

    # if malformed payload, return error message, else proceed:
    if ("TransactionID" not in request_data
            or "amount" not in request_data
            or "shortcode" not in request_data
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
    AppId = int(request_data.get('ApplicationId'))
    TransactionID = request_data.get('TransactionID')

    # get password from .env:
    mpesa_pass = str(config("MPESA_PASS_KEY"))
    short_code = int(str_short_code)

    # get the password by b64 encoding the short code + mpesa pass + time:
    str_bytes = str_short_code + mpesa_pass + time
    str_bytes = str_bytes.encode("ascii")
    password = base64.b64encode(str_bytes)
    password = password.decode("ascii")
    password = str(password)
    # make stk push
    try:

        # get access_token
        access_token = get_mpesa_token()

        # stk_push request url
        api_url = "https://sandbox.safaricom.co.ke/mpesa/reversal/v1/request"

        # put access_token in request headers
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # define request body
        data = {
            "Initiator": "Boots Store Kenya",
            "SecurityCredential": password,
            "CommandID": "TransactionReversal",
            "TransactionID": TransactionID ,
            "Amount": Amount,
            "ReceiverParty": short_code,
            "RecieverIdentifierType": 4,
            "ResultURL": f"https://{str(config('MPESA_CALLBACK_URL'))}/reversals/resultUrl/",
            "QueueTimeOutURL": f"https://{str(config('MPESA_CALLBACK_URL'))}/reversals/queueTimeoutUrl/",
            "Remarks": "please",
            "Occasion": "work"
        }

        # make request and catch response and display the error message, if any,  for debugging
        response = requests.post(api_url, json=data, headers=headers)
        jsonResponse = json.loads(response.text)
        print(jsonResponse)

        return jsonify({
            "Response": jsonResponse
        }), 200
    except Exception as e:
        print(e)
        # catch error and return responses:
        return jsonify({
            "success": False,
            "message": "Sorry, an unexpected exception occurred. Please contact Admin."
        }), 400
#query timeout url:
@reversalsBp.route("/queueTimeoutUrl", methods= ['POST','GET'])
def queueTimeoutUrl():
    request_data = request.get_json()
    print(request_data)
    return jsonify({
        "Result" : "success"
    }),200

#resulturl:
@reversalsBp.route("/resultUrl", methods= ['GET', 'POST'])
def resutlUrl():
    request_data = request.get_json()
    print(request_data)
    return jsonify({
        "Result" : "success"
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
