from flask import render_template

from shop import app
from shop.database import DBSession
from shop.models import Product


@app.route('/')
def product_list():
    products = DBSession.query(Product).order_by(Product.title.asc())

    return render_template('product_list.html', products=products)
