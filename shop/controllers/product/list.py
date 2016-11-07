from flask import render_template

from shop import app
from shop.database import DBSession
from shop.models.product import Product
from shop.models.order import Order


@app.route('/')
def product_list():
	products = DBSession.query(Product).order_by(Product.title.asc())

	return render_template(
		'product/list.html',
		products=products,
		order_product_ids=Order.get_product_ids_from_session(),
		total_products_qty=Order.get_tatal_product_qty_from_session(),
	)
