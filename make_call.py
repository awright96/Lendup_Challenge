import os, subprocess
from twilio.rest import Client
from flask import url_for


def make_call(num):
    print('Calling: ' + num)
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    my_phone = os.environ.get('TWILIO_PHONE_NUMBER')
    client = Client(account_sid, auth_token)
    client.calls.create(to=num, from_=my_phone, url=url_for('incoming'))


