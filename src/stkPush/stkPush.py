from decouple import config
from flask import Flask, Response, jsonify, request, json, Blueprint
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import pytz

stkBp = Blueprint("stkPush","stkBp", url_prefix="/stk")

@stkBp.route("/", methods=["POST"])
def make_request():
    response_data = request.get_json()
    print("contact made")
    fmt = '%Y%m%d%H%M%S'
    tz_Nairobi = pytz.timezone('Africa/Nairobi')
    time = datetime.now(tz_Nairobi).strftime(fmt)
    print(f'This is the time: {time} and it is of type {type(time)}')
    mpesa_pass = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919";
    short_code = "174379";
    int_short_code = int(short_code)
    print(f'{int_short_code} is of type: {type(int_short_code)}')
    str_bytes = short_code + mpesa_pass + time;
    str_bytes = str_bytes.encode("ascii")
    password = base64.b64encode(str_bytes)
    password = password.decode("ascii")
    phoneNumber = response_data.get('phone')
    if phoneNumber.startswith('254') == False:
        phoneNumber = '254' + str(int(phoneNumber))
    phoneNumber = int(phoneNumber)
    print(phoneNumber)
    # make stk push
    try:

        # get access_token
        access_token = get_mpesa_token()
        print(f"access_token -> {access_token}")

        # stk_push request url
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        # put access_token in request headers
        headers = { "Authorization": f"Bearer {access_token}" ,"Content-Type": "application/json" }


        # define request body
        data = {
            "BusinessShortCode": int_short_code,
            "Password": str(password),
            "Timestamp": time, # timestamp format: 20190317202903 yyyyMMhhmmss 
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(response_data.get('amount')),
            "PartyA": phoneNumber,
            "PartyB": int_short_code,
            "PhoneNumber": phoneNumber,
            "CallBackURL": "https://eab2-102-166-210-117.ngrok.io/stk/callback",
            "AccountReference": "Boots Kenya Store",
            "TransactionDesc": "Payment of Ksh 1"
        }

        # make request and catch response and display the error message for debugging
        response = requests.post(api_url,json=data,headers=headers)
        jsonResponse = json.loads(response.text)
        errorMessage = jsonResponse.get('errorMessage')
        print(errorMessage)

        # check response code for errors and return response
        if response.status_code > 299:
            return jsonify({
                "success": False,
                "message":"Sorry, something went wrong please try again later."
            }),400

        # CheckoutRequestID = response.text['CheckoutRequestID']

        # Do something in your database e.g store the transaction or as an order
        # make sure to store the CheckoutRequestID to identify the tranaction in 
        # your CallBackURL endpoint.

        # return a respone to your user
        return jsonify({
            "data": json.loads(response.text)
        }),200

    except:
        # catch error and return respones

        return jsonify({
            "success":False,
            "message":"Sorry something went awry please try again."
        }),400

# get Oauth token from M-pesa [function]
def get_mpesa_token():

    consumer_key = "944ffP8lbnwq9uKoqzgL3SAKeAt3OhJR"
    consumer_secret = "e6yZUQbeXoKzQOud"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # make a get request using python requests liblary
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    return r.json()['access_token']

@stkBp.route("/callback", methods=["POST"])
def callbackResponse():
    callback_response = request.get_json()
    print(callback_response)
    return jsonify("Response registered!!"), 200