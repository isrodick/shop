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


@app.route('/order/product/<int:product_id>/add', methods=['POST'])
def order_product_add(product_id):
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


@app.route('/order/product/<int:product_id>/qty', methods=['POST'])
def order_product_qty(product_id):
	try:
		qty = int(request.form['qty'])
	except (ValueError, TypeError) as e:
		print(e)

		return jsonify(
			status='valid-error',
			message='Please enter integer value',
		)

	if qty <= 0:
		return jsonify(
			status='valid-error',
			message='Please enter positive value',
		)

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

	if order_product.product.qty < qty:
		return jsonify(
			status='valid-error',
			message='Only {} product(s) in stock'.format(order_product.product.qty),
		)

	order_product.qty = qty

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


@app.route('/order/product/<int:product_id>/delete', methods=['POST'])
def order_product_delete(product_id):
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

	try:
		DBSession.delete(order_product)
		DBSession.flush()
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		abort(400)	## temporarily

	return jsonify(
		status='success',
		product_id=order_product.product_id,
		total_price=order_product.get_total_price(),
		total_products_qty=order_product.order.get_total_product_qty(),
	)
