from flask import Flask
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

from app import phone

app.run(port=5000, host='localhost')

