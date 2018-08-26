from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.update(
    BOOTSTRAP_SERVE_LOCAL=True,
    SECRET_KEY='derplodicus'
)

from app import routes

bootstrap = Bootstrap(app)
