from flask import (
	request,
	session,
	redirect,
	url_for,
	abort,
    render_template,
    flash,
    jsonify,
)

from sqlalchemy.exc import SQLAlchemyError

from shop import app
from shop.database import DBSession
from shop.models import (
    Product,
    Order,
    OrderProduct,
    OrderStatus,
    PaymentMethod,
)


@app.route('/admin/product/list')
def admin_product_list():
    products = DBSession.query(Product).order_by(Product.title.asc())

    return render_template('admin_product_list.html', products=products)


@app.route('/admin/product/new', methods=['GET', 'POST'])
def admin_product_new():
	if request.method == 'POST':
		product = Product()

		product.title = request.form['title']
		product.prie = request.form['prie']
		product.image_url = request.form['image_url']
		product.qty = request.form['qty']

		DBSession.add(product)
		DBSession.flush()
		DBSession.commit()

		flash('Product was created successfully')

		return redirect(url_for('product_edit', id=product.id))

	return render_template('product_new.html')


@app.route('/admin/product/<int:id>/edit', methods=['GET', 'POST'])
def admin_product_edit(id):
	product = DBSession.query(Product).get(id)

	if not product:
		flash('Product not found')

		return redirect(url_for('product_list'))

	if request.method == 'POST':
		product.title = request.form['title']
		product.prie = request.form['prie']
		product.image_url = request.form['image_url']
		product.qty = request.form['qty']

		DBSession.add(product)
		DBSession.commit()

		flash('Product was updated successfully')

		return redirect(url_for('product_list'))

	return render_template('product_edit.html', product=product)


@app.route('/admin/product/<int:id>/delete', methods=['POST'])
def admin_product_delete(id):
	product = DBSession.query(Product).get(id)

	if not product:
		flash('Product not found')

		return redirect(url_for('product_list'))

	if request.method != 'POST':
		return redirect(url_for('product_list'))

	try:
		DBSession.delete(product)
		DBSession.flush()
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)
		flash('Product could not be deleted')

		DBSession.rollback()

		return redirect(url_for('product_edit', id=product.id))

	flash('Product was deleted successfully')

	return redirect(url_for('product_list'))


@app.route('/')
def product_list():
    products = DBSession.query(Product).order_by(Product.title.asc())

    return render_template('product_list.html', products=products)


@app.route('/basket')
def basket():
	order = None

	if 'order_id' in session:
		order = DBSession.query(Order).get(session['order_id'])

	return render_template('basket.html', order=order, payment_methods=PaymentMethod)


@app.route('/order/product/<int:product_id>/add')
def order_product_add(product_id):
	order = None

	if 'order_id' in session:
		order = DBSession.query(Order).get(session['order_id'])
	else:
		order = Order()
		order.status = OrderStatus.new

		try:
			DBSession.add(order)
			DBSession.flush()
		except SQLAlchemyError as e:
			print(e)

			DBSession.rollback()

			abort(400)	## temporarily

		session['order_id'] = order.id

	product = DBSession.query(Product).get(product_id)

	if not product:
		abort(404)	## temporarily

	if product.qty < 1:
		abort(400)	## temporarily

	order_product = OrderProduct()
	order_product.order_id = order.id
	order_product.product_id = product.id
	order_product.qty = 1

	try:
		DBSession.add(order_product)
		DBSession.flush()
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		abort(400) ## temporarily

	return jsonify(
		total_products_qty=sum(link.qty for link in order.links),
	)


@app.route('/order/product/<int:product_id>/qty', methods=['POST'])
def order_product_qty(product_id):
	order = None

	if 'order_id' in session:
		order = DBSession.query(Order).get(session['order_id'])

	if not order:
		abort(404)

	product = DBSession.query(Product).get(product_id)

	if not product:
		abort(404)	## temporarily

	if product.qty < request.form['qty']:
		abort(400)	## temporarily

	order_product = order.product_items.get(product_id)

	if not order_product:
		abort(404)	## temporarily

	order_product.qty = request.form['qty']

	try:
		DBSession.add(order_product)
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		abort(400)	## temporarily

	return jsonify(
		product={
			'id': order_product.product_id,
			'qty': order_product.qty,
		},
		total_price=sum(link.qty * link.product.price for link in order.links),
	)


@app.route('/order/product/<int:product_id>/delete', methods=['POST'])
def order_product_delete(product_id):
	order = None

	if 'order_id' in session:
		order = DBSession.query(Order).get(session['order_id'])

	if not order:
		abort(404)

	product = DBSession.query(Product).get(product_id)

	if not product:
		abort(404)	## temporarily

	order_product = order.product_items.get(product_id)

	if not order_product:
		abort(404)	## temporarily

	try:
		DBSession.delete(order_product)
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		abort(400)	## temporarily

	return jsonify(
		product_id=product.id,
		total_price=sum(link.qty * link.product.price for link in order.links),
	)


@app.route('/admin/order/list')
def admin_order_list():
	orders = DBSession.query(Order)\
		.order_by(
			(Order.status == OrderStatus.paid.name).desc(),
		)

    return render_template('admin_order_list.html', products=orders)


@app.route('/admin/order/<int:id>/view')
def admin_order_view():
	order = DBSession.query(Order).get(id)

	if not order:
		flash('Order not found')

		return redirect(url_for('admin_order_list'))

	return render_template('admin_order_view.html', order=order)


@app.route('/admin/order/<int:id>/delete', methods=['POST'])
def admin_order_delete(id):
	order = DBSession.query(Order).get(id)

	if not order:
		flash('Order not found')

		return redirect(url_for('admin_order_list'))

	try:
		DBSession.delete(order)
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)
		flash('Order could not be deleted')

		DBSession.rollback()

		return redirect(url_for('admin_order_view', id=order.id))

	flash('Order was deleted successfully')

	return redirect(url_for('admin_order_list'))


@app.route('/order/list')
def order_list():
	orders = DBSession.query(Order)\
		.order_by(
			(Order.status == OrderStatus.paid.name).desc(),
		)

    return render_template('order_list.html', products=orders)


@app.route('/order/<int:id>/view')
def order_view():
	order = DBSession.query(Order).get(id)

	if not order:
		flash('Order not found')

		return redirect(url_for('order_list'))

	return render_template('order_view.html', order=order)


@app.route('/order/pay', methods=['POST'])
def order_pay():
	order = None

	if 'order_id' in session:
		order = DBSession.query(Order).get(session['order_id'])

	if not order:
		abort(404)

	if request.form['payment_method'] not in PaymentMethod._member_names_:
		flash('Invalid payment method')

		return redirect(url_for('basket'))

	order.status = OrderStatus.paid
	order.payment_method = request.form['payment_method']

	try:
		DBSession.add(order)
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		flash('Error during order payment')

		return redirect(url_for('basket'))

	session.pop('order_id', None)

	return redirect(url_for('order_view', id=order.id))
