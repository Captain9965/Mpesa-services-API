from decouple import config
from flask import Flask, Response, jsonify, request, json, Blueprint
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import pytz
from src import ResponseDump, RequestDump, db
import uuid

stkBp = Blueprint("stkPush","stkBp", url_prefix="/stk")

@stkBp.route("/", methods=["POST"])
def make_request():

    #get the request data payload:
    request_data = request.get_json()

    #get time:
    fmt = '%Y%m%d%H%M%S'
    tz_Nairobi = pytz.timezone('Africa/Nairobi')
    time_raw = datetime.now(tz_Nairobi)
    time = time_raw.strftime(fmt)

    #store the request in the requestDump database:
    """
    Todo: Should validate the json data to guard against SQL injection attacks 
    """
    r = RequestDump(
        uuid_ = uuid.uuid4(),
        payload = request_data,
        created_at = time_raw,
        service = "STK PUSH"
    )

    db.session.add(r)
    db.session.commit()

    #get password from .env:
    mpesa_pass = str(config("MPESA_PASS_KEY"));
    str_short_code = request_data.get('shortcode')
    short_code = int(str_short_code)

    #get the password by b64 encoding the short code + mpesa pass + time:
    str_bytes =  str_short_code + mpesa_pass + time;
    str_bytes = str_bytes.encode("ascii")
    password = base64.b64encode(str_bytes)
    password = password.decode("ascii")
    password = str(password)

    # get phone number to push the stk to from the request and validate it:
    """ Further validation needed
        For example: what if the phone number provided is > 12 characters long?
    """
    phoneNumber = request_data.get('phone')
    if phoneNumber.startswith('254') == False:
        phoneNumber = '254' + str(int(phoneNumber))
    phoneNumber = int(phoneNumber)

    # make stk push
    try:

        # get access_token
        access_token = get_mpesa_token()

        # stk_push request url
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        # put access_token in request headers
        headers = { "Authorization": f"Bearer {access_token}" ,"Content-Type": "application/json" }


        # define request body
        data = {
            "BusinessShortCode": short_code,
            "Password": password,
            "Timestamp": time,              # timestamp format: 20190317202903 yyyyMMhhmmss 
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(request_data.get('amount')),
            "PartyA": phoneNumber,
            "PartyB": short_code,
            "PhoneNumber": phoneNumber,
            "CallBackURL": f"https://{str(config('MPESA_CALLBACK_URL'))}/stk/callback",
            "AccountReference": str(request_data.get('AccountReference')),
            "TransactionDesc": "STK Payment"
        }

        # make request and catch response and display the error message, if any,  for debugging
        response = requests.post(api_url,json=data,headers=headers)
        jsonResponse = json.loads(response.text)
        errorMessage = jsonResponse.get('errorMessage')
        print(errorMessage)

        # check response code for errors and return response
        if response.status_code > 299:
            return jsonify({
                "success": False,
                "message": errorMessage
            }),400

        #return the successful response to the user:
        return jsonify({
            "Response": json.loads(response.text)
        }),200

    except:

        # catch error and return responses:
        return jsonify({
            "success":False,
            "message":"Sorry, an unexpected exception occurred. Please contact Admin."
        }),400

# get Authentication token from M-pesa [function]:
def get_mpesa_token():
    consumer_key = str(config('CONSUMER_KEY'))
    consumer_secret = str(config('CONSUMER_SECRET'))
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # make a get request using python requests library
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    return r.json().get('access_token')
    
"""This is the callback url:"""
@stkBp.route("/callback", methods=["POST"])
def callbackResponse():
    callback_response = request.get_json()
    print(callback_response)
    tz_Nairobi = pytz.timezone('Africa/Nairobi')
    time_raw = datetime.now(tz_Nairobi)
    #store the response:
    resp = ResponseDump(
        uuid_ = uuid.uuid4(),
        payload = callback_response,
        created_at = time_raw,
        service = "STK PUSH"
    )

    db.session.add(resp)
    db.session.commit()
    
    #send the response to the callback url:


    return jsonify("Response registered!!"), 200