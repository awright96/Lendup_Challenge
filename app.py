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
import os, pprint

#Setup for Twilio
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
my_phone = os.environ.get('TWILIO_PHONE_NUMBER')
client = Client(account_sid, auth_token)

#Setup for the scheduler to make delayed calls
scheduler = BackgroundScheduler()
scheduler.start()

#Setup for database
db_name = os.environ.get('DB_NAME')
db_uri  = os.environ.get('DB_URI')
db_connection = MongoClient(db_uri)
db = db_connection[db_name]
calls = db['calls']

#Create flask object
app = Flask(__name__)
app.config.from_object(Config)


#Default route, redirects to /call
@app.route('/')
def hello_world():
    return redirect(url_for('caller'))


@app.route('/call', methods=['GET', 'POST'])
def caller():
    form = PhoneForm()
    call_table = []
    for call in calls.find():
        call_table.append(call)

    #Serve the form
    if request.method == 'GET':
        return render_template('call.html', form=form, calls=call_table)

    #Read from the form
    elif request.method == 'POST' and form.validate():
        num = request.form['phone']
        time_ = request.form['delay']
        unit = request.form['unit']


        if is_valid_number(num):
            if time_ == '':
                make_call(num)
                return render_template('call.html', form=form, number=num, calls=call_table)
            else:
                delay = str(time_) + unit
                if unit == 's':
                    call_time = datetime.now() + timedelta(seconds=int(time_))
                    scheduler.add_job(make_call, 'date', run_date=call_time, args=[num, delay])
                if unit == 'm':
                    call_time = datetime.now() + timedelta(minutes=int(time_))
                    scheduler.add_job(make_call, 'date', run_date=call_time, args=[num, delay])
                if unit == 'h':
                    call_time = datetime.now() + timedelta(hours=int(time_))
                    scheduler.add_job(make_call, 'date', run_date=call_time, args=[num, delay])
                if unit == 'd':
                    call_time = datetime.now() + timedelta(days=int(time_))
                    scheduler.add_job(make_call, 'date', run_date=call_time, args=[num, delay])
            return render_template('call.html', form=form, number=num, calls=call_table)
        else:
            return render_template('call.html', form=form, error=num, calls=call_table)
    else:
        return redirect(url_for('caller'))

#Route for all call processing, including outgoing calls. The 'incoming'
#   refers to incoming from Twilio, not just incoming calls
@app.route('/incoming', methods=['POST'])
@app.route('/incoming/<phone>:<delay>', methods=['POST'])
@validate_twilio_request
def incoming(phone='none', delay='0s'):
    resp = VoiceResponse()
    if phone != 'none':
        gather = Gather(action='/gather/' + phone + ':' + delay)
        gather.say("Please insert your fizz buzz number followed by the pound symbol")
        resp.append(gather)
        resp.redirect('/incoming')
        return str(resp)

    gather = Gather(action='/gather')
    gather.say("Please insert your fizz buzz number followed by the pound symbol")
    resp.append(gather)

    resp.redirect('/incoming')

    return str(resp)


@app.route('/gather', methods=['POST'])
@app.route('/gather/<phone>:<delay>', methods=['POST'])
@validate_twilio_request
def gath(phone='none', delay='0s'):

    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']

        if phone != 'none':
            post = {'phone': phone,
                    'delay': delay,
                    'choice': choice}
            calls.insert_one(post)

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


