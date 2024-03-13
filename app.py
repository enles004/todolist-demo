from flask import Flask
from flask_bcrypt import Bcrypt

from flask_caching import Cache
from config import Config
from services.make_celery import make_celery

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object(Config)
cache = Cache(app)
celery = make_celery(app)
