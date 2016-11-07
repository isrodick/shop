from flask import Flask


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    SQLALCHEMY_DATABASE_URI='postgresql://isrodick_db:shop_db@localhost/shop',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

from shop.controllers.admin.order import *
from shop.controllers.admin.product import *
from shop.controllers.basket import *
from shop.controllers.order import *
from shop.controllers.product import *
