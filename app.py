from flask import Flask, render_template, request, redirect, url_for
from form import PhoneForm
from twilio.twiml.voice_response import VoiceResponse, Gather
from fizz import fizz
from validator import validate_twilio_request, is_valid_number
from twilio.rest import Client
from make_call import make_call
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from pymongo import MongoClient
import os


account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
my_phone = os.environ.get('TWILIO_PHONE_NUMBER')
client = Client(account_sid, auth_token)

scheduler = BackgroundScheduler()
scheduler.start()

db_name = os.environ.get('DB_NAME')
db_uri  = os.environ.get('DB_URI')


db_connection = MongoClient(db_uri)
db = db_connection[db_name]

calls = db['calls']

app = Flask(__name__)
app.config.from_object(Config)



@app.route('/')
def hello_world():
    return redirect(url_for('caller'))


@app.route('/call', methods=['GET', 'POST'])
def caller():
    form = PhoneForm()
    if request.method == 'GET':
        return render_template('call.html', form=form)
    elif request.method == 'POST' and form.validate():
        num = request.form['phone']
        time_ = request.form['delay']
        unit = request.form['unit']

        if is_valid_number(num):
            if time_ == '':
                make_call(num)
                return render_template('call.html', form=form, number=num)
            else:
                if unit == 's':
                    call_time = datetime.now() + timedelta(seconds=int(time_))
                    scheduler.add_job(make_call, 'date', run_date=call_time, args=[num])
                if unit == 'm':
                    call_time = datetime.now() + timedelta(minutes=int(time_))
                    scheduler.add_job(make_call, 'date', run_date=call_time, args=[num])
                if unit == 'h':
                    call_time = datetime.now() + timedelta(hours=int(time_))
                    scheduler.add_job(make_call, 'date', run_date=call_time, args=[num])
                if unit == 'd':
                    call_time = datetime.now() + timedelta(days=int(time_))
                    scheduler.add_job(make_call, 'date', run_date=call_time, args=[num])
            return render_template('call.html', form=form, number=num)
        else:
            return render_template('call.html', form=form, error=num)
    else:
        return redirect(url_for('caller'))


@app.route('/incoming', methods=['POST'])
@app.route('/incoming/<phone>', methods=['POST'])
@validate_twilio_request
def incoming(phone='none'):
    if phone != 'none':
        print(phone)
    resp = VoiceResponse()

    gather = Gather(action='/gather')
    gather.say("Please insert your fizz buzz number followed by the pound symbol")
    resp.append(gather)

    resp.redirect('/incoming')

    return str(resp)


@app.route('/gather', methods=['POST'])
@app.route('/gather/<phone>', methods=['POST'])
@validate_twilio_request
def gath(phone='none'):
    if phone != 'none':
        print("gather: " + phone)
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
        resp.say('Your fizzbuzz is' + fizz(int(choice)))
        return str(resp)
    else:
        resp.say("invalid choice. Start over")

    resp.redirect('/incoming')
    return str(resp)


if __name__ == '__main__':
    app.run()


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


