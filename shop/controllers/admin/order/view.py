from flask import (
	redirect,
	url_for,
	render_template,
	flash,
)

from shop import app
from shop.database import DBSession
from shop.models.order import Order


@app.route('/admin/order/<int:id>/view')
def admin_order_view():
	order = DBSession.query(Order).get(id)

	if not order:
		flash('Order not found')

		return redirect(url_for('admin_order_list'))

	return render_template('admin/order/view.html', order=order)
