from flask import Flask
from Site.extentions import db

app = Flask(__name__)

app.secret_key = 'dfndsbfsfe45439'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LeKCP8nAAAAAOyY-F0STg6BT2N87zKAhX-vz2VS"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LeKCP8nAAAAAHAzsogZglQDxc4FMORusUQEY2sS"

db.init_app(app)

from Site import routes
