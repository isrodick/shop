from flask import (
	session,
	redirect,
	url_for,
	flash,
)

from sqlalchemy.exc import SQLAlchemyError

from shop import app
from shop.database import DBSession
from shop.models.order import Order


@app.route('/admin/order/<int:id>/delete', methods=['POST'])
def admin_order_delete(id):
	order = DBSession.query(Order).get(id)

	if not order:
		flash('danger;Order not found')

		return redirect(url_for('admin_order_list'))

	try:
		DBSession.delete(order)
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)
		flash('danger;Order could not be deleted')

		DBSession.rollback()

		return redirect(url_for('admin_order_view', id=order.id))

	if session.get('order_id') == id:
		session.pop('order_id', None)

	flash('warning;Order was deleted successfully')

	return redirect(url_for('admin_order_list'))
