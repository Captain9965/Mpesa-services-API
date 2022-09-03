# Mpesa services Api
This is a flask API that abstracts the M-Pesa services such as B2C, C2B, reversals and stk push to make it easier for reliable and quick intergration. This is made possible through simplified interfaces 

To run the application on **linux**:
1. First set up a **virtual environment**: 
>``python3 -m venv venv``
2. Install flask and other dependencies for this application:
>``Pip install -r requirements.txt``
3. Create a .env file with all the required application configurations
4. Set up a postgres database and edit the .env accordingly. Use [this](https://chartio.com/learn/postgresql/create-a-user-with-psql/)  as a reference.

## Environmment variables
The environment variables should be:

`APP_CONFIG=config.DevConfig
DATABASE_URL=postgresql:///db_name
PROD_DATABASE_URL=postgresql:///db_name
MPESA_PASS_KEY=passkey
CONSUMER_KEY=consumerkey
CONSUMER_SECRET=consumersecret
MPESA_CALLBACK_URL=callbackurl.io`