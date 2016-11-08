from flask import (
	request,
	session,
	redirect,
	url_for,
	flash,
	render_template,
)

from sqlalchemy.exc import SQLAlchemyError

from shop import app
from shop.database import DBSession
from shop.models.order import Order
from shop.models.enums import OrderStatus
from shop.forms.basket import BasketPayForm


def get_error_product_qty(order):
	if not order:
		return set()

	error_product_qty = set()

	for link in order.links:
		if link.product.qty < link.qty:
			error_product_qty.add(link.product_id)

	return error_product_qty



@app.route('/basket', methods=['GET', 'POST'])
def basket():
	order = Order.get_from_session()

	form = BasketPayForm(request.form)

	error_product_qty = get_error_product_qty(order)

	if request.method == 'POST':
		if not order:
			flash('danger;Order not found')

			return redirect(url_for('product_list'))

		if not error_product_qty and form.validate():
			form.populate_obj(order)
			order.status = OrderStatus.paid

			for link in order.links:
				link.product.qty -= link.qty

			try:
				DBSession.add(order)
				DBSession.flush()
				DBSession.commit()
			except SQLAlchemyError as e:
				print(e)

				DBSession.rollback()

				flash('danger;Error during pay order')

				return redirect(url_for('basket'))

			session.pop('order_id', None)

			flash('warning;Order paid successfully')

			return redirect(url_for('basket_paid_view', id=order.id))
		else:
			flash('danger;Validation error. Please enter the correct data')

	return render_template(
		'basket/basket.html',
		form=form,
		order=order,
		error_product_qty=error_product_qty,
		sorted_links=sorted(order.links, key=lambda link: link.product.title) if order else [],
		basket_has_products=order.has_products() if order else False,
		total_products_qty=Order.get_tatal_product_qty_from_session(),
	)


@app.route('/basket/<int:id>/paid')
def basket_paid_view(id):
	order = DBSession.query(Order).get(id)

	if not order:
		flash('danger;Order not found')

		return redirect(url_for('product_list'))

	if order.status != OrderStatus.paid:
		flash('danger;Order not paid yet')

		return redirect(url_for('product_list'))

	return render_template(
		'basket/basket_paid.html',
		order=order,
		sorted_links=sorted(order.links, key=lambda link: link.product.title),
		basket_has_products=order.has_products(),
	)
