from flask import Flask
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

app.run(port=5000, host='localhost')

