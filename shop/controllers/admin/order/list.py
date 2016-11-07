from flask import render_template

from shop import app
from shop.database import DBSession
from shop.models.order import OrderStatus
from shop.models.enums import OrderStatus


@app.route('/admin/order/list')
def admin_order_list():
	orders = DBSession.query(Order)\
		.order_by(
			(Order.status == OrderStatus.paid.name).desc(),
		)

	return render_template('admin/order/list.html', orders=orders)
