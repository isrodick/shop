from flask import (
	request,
	session,
	jsonify,
)

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import FlushError

from shop import app
from shop.database import DBSession
from shop.models.product import Product
from shop.models.order import (
	Order,
	OrderProduct,
)
from shop.forms.basket import BasketProductQtyForm


@app.route('/basket/product/<int:product_id>/add', methods=['POST'])
def basket_product_add(product_id):
	product = DBSession.query(Product).get(product_id)

	if not product:
		return jsonify(
			status='error',
			message='Product not found',
		)

	if product.qty < 1:
		return jsonify(
			status='error',
			message='Product is not available',
		)

	try:
		order = Order.get_from_session(create=True)
	except FlushError as e:
		return jsonify(
			status='error',
			message='Error during add the product to the backet',
		)

	_order_product = DBSession.query(OrderProduct).get((order.id, product.id))
	if _order_product:
		return jsonify(
			status='error',
			message='This product already at the basket',
		)

	order_product = OrderProduct()
	order_product.order_id = order.id
	order_product.product_id = product.id
	order_product.qty = 1

	DBSession.add(order_product)
	DBSession.commit()

	return jsonify(
		status='success',
		total_products_qty=order_product.order.get_total_product_qty(),
	)


@app.route('/basket/product/<int:product_id>/qty', methods=['POST'])
def basket_product_qty(product_id):
	if 'order_id' not in session:
		return jsonify(
			status='error',
			message='Order not found',
		)

	order_product = DBSession.query(OrderProduct).get((session['order_id'], product_id))

	if not order_product:
		return jsonify(
			status='error',
			message='This product is not added to the basket',
		)

	form = BasketProductQtyForm(request.form)

	if not form.validate(order_product.product):
		return jsonify(
			status='valid-error',
			message=' '.join(form.qty.errors)
		)

	order_product.qty = form.qty.data

	try:
		DBSession.add(order_product)
		DBSession.flush()
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		return jsonify(
			status='error',
			message='Error during update product qty to the basket',
		)

	return jsonify(
		total_price=str(order_product.order.get_total_price()),
		total_products_qty=order_product.order.get_total_product_qty(),
	)


@app.route('/basket/product/<int:product_id>/delete', methods=['POST'])
def basket_product_delete(product_id):
	if 'order_id' not in session:
		return jsonify(
			status='error',
			message='Order not found',
		)

	order_product = DBSession.query(OrderProduct).get((session['order_id'], product_id))
	order = order_product.order

	if not order_product:
		return jsonify(
			status='error',
			message='This product is not added to the basket',
		)

	try:
		DBSession.delete(order_product)
		DBSession.flush()
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		return jsonify(
			status='error',
			message='Error during remove product from the basket',
		)

	return jsonify(
		status='success',
		total_price=str(order.get_total_price()),
		total_products_qty=order_product.order.get_total_product_qty(),
	)
