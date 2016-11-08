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

			return redirect(url_for('product_list'))
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
