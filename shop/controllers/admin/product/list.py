from flask import render_template

from shop import app
from shop.database import DBSession
from shop.models.product import Product


@app.route('/admin/product/list')
def admin_product_list():
	products = DBSession.query(Product).order_by(Product.title.asc())

	return render_template('admin/product/list.html', products=products)
