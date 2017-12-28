from flask import abort, request
from functools import wraps
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os


def validate_twilio_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

        request_valid = validator.validate(
            request.url,
            request.form,
            request.headers.get('X-TWILIO-SIGNATURE', '')
        )
        if request_valid:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function


def is_valid_number(num):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    try:
        client.lookups.phone_numbers(num).fetch(type='carrier')
        return True
    except TwilioRestException as e:
        if e.code == 20404:
            return False
        else:
            raise e
