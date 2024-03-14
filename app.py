from flask import Flask
from flask_bcrypt import Bcrypt

from flask_caching import Cache
from config import Config

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object(Config)
cache = Cache(app)
