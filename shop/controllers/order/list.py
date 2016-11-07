from flask import render_template

from shop import app
from shop.database import DBSession
from shop.models.order import Order
from shop.models.enums import OrderStatus


@app.route('/order/list')
def order_list():
	orders = DBSession.query(Order)\
		.order_by(
			(Order.status == OrderStatus.paid.name).desc(),
		)

	return render_template('order/list.html', orders=orders)
