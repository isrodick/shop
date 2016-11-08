from flask import (
	request,
	session,
	redirect,
	url_for,
	flash,
	render_template,
)

from shop import app
from shop.database import DBSession
from shop.models.order import Order
from shop.models.enums import OrderStatus
from shop.forms.basket import BasketPayForm


@app.route('/basket', methods=['GET', 'POST'])
def basket():
	order = Order.get_from_session()

	form = BasketPayForm(request.form)

	if request.method == 'POST':
		if not order:
			flash('Order not found')

			return redirect(url_for('product_list'))

		if form.validate():
			form.populate_obj(order)
			order.status = OrderStatus.paid

			DBSession.add(order)
			DBSession.commit()

			session.pop('order_id', None)

			flash('Order paid successfully')

			return redirect(url_for('basket_paid_view', id=order.id))
		else:
			flash('Validation error. Please enter the correct data')

	return render_template(
		'basket/basket.html',
		form=form,
		order=order,
		sorted_links=sorted(order.links, key=lambda link: link.product.title) if order else [],
		basket_has_products=order.has_products() if order else False,
		total_products_qty=Order.get_tatal_product_qty_from_session(),
	)


@app.route('/basket/<int:id>/paid')
def basket_paid_view(id):
	order = DBSession.query(Order).get(id)

	if not order:
		flash('Order not found')

		return redirect(url_for('product_list'))

	if order.status != OrderStatus.paid:
		flash('Order not paid yet')

		return redirect(url_for('product_list'))

	return render_template('basket/basket_paid.html', order=order)
