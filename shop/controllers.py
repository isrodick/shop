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
from sqlalchemy.orm.exc import FlushError

from shop import app
from shop.database import DBSession
from shop.models import (
    Product,
    Order,
    OrderProduct,
    OrderStatus,
    PaymentMethod,
)
from shop.forms import (
	ProductNewForm,
	ProductEditForm,
	OrderPayForm,
)


@app.route('/admin/product/list')
def admin_product_list():
    products = DBSession.query(Product).order_by(Product.title.asc())

    return render_template('admin_product_list.html', products=products)


@app.route('/admin/product/new', methods=['GET', 'POST'])
def admin_product_new():
	form = ProductNewForm(request.form)

	if request.method == 'POST' and form.validate():
		product = Product()

		product.title = form.title.data
		product.price = form.price.data
		product.image_url = form.image_url.data
		product.qty = form.qty.data

		DBSession.add(product)
		DBSession.commit()

		flash('Product was created successfully')

		return redirect(url_for('admin_product_edit', id=product.id))
	elif request.method == 'POST':
		flash('Validation error. Please enter the correct data')

	return render_template('admin_product_new.html', form=form)


@app.route('/admin/product/<int:id>/edit', methods=['GET', 'POST'])
def admin_product_edit(id):
	product = DBSession.query(Product).get(id)

	if not product:
		flash('Product not found')

		return redirect(url_for('admin_product_list'))

	form = ProductEditForm(request.form, product)

	if request.method == 'POST' and form.validate(current_product=product):
		form.populate_obj(product)

		DBSession.add(product)
		DBSession.commit()

		flash('Product was updated successfully')

		return redirect(url_for('admin_product_list'))
	elif request.method == 'POST':
		flash('Validation error. Please enter the correct data')

	return render_template('admin_product_edit.html', form=form, product=product)


@app.route('/admin/product/<int:id>/delete', methods=['POST'])
def admin_product_delete(id):
	product = DBSession.query(Product).get(id)

	if not product:
		return jsonify(
			status='error',
			message='Product not found',
		)

	try:
		DBSession.delete(product)
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		return jsonify(
			status='error',
			message='Product could not be deleted',
		)

	flash('Product was deleted successfully')

	return jsonify(
		status='success',
		redirect_url=url_for('admin_product_list'),
	)


@app.route('/')
def product_list():
	products = DBSession.query(Product).order_by(Product.title.asc())

	return render_template(
		'product_list.html',
		products=products,
		order_product_ids=Order.get_product_ids_from_session(),
		total_products_qty=Order.get_tatal_product_qty_from_session(),
	)


@app.route('/basket', methods=['GET', 'POST'])
def basket():
	order = Order.get_from_session()
	form = OrderPayForm(request.form)

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

			return redirect(url_for('task_list'))
		else:
			flash('Validation error. Please enter the correct data')

	return render_template(
		'basket.html',
		form=form,
		order=order,
		sorted_links=sorted(order.links, key=lambda link: link.product.title),
		basket_has_products=order.has_products() if order else False,
		payment_methods=PaymentMethod,
		total_products_qty=Order.get_tatal_product_qty_from_session(),
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
		product={
			'id': order_product.product_id,
			'qty': order_product.qty,
		},
		total_price=str(order_product.order.get_total_price()),
		total_products_qty=order_product.order.get_total_product_qty(),
	)


@app.route('/order/product/<int:product_id>/delete', methods=['POST'])
def order_product_delete(product_id):
	if 'order_id' not in session:
		abort(404)

	order_product = DBSession.query(OrderProduct).get(session['order_id'], product_id)

	if not order_product:
		abort(404)

	try:
		DBSession.delete(order_product)
		DBSession.flush()
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)

		DBSession.rollback()

		abort(400)	## temporarily

	return jsonify(
		product_id=order_product.product_id,
		total_price=order_product.get_total_price(),
		total_products_qty=order_product.order.get_total_product_qty(),
	)


@app.route('/admin/order/list')
def admin_order_list():
	orders = DBSession.query(Order)\
		.order_by(
			(Order.status == OrderStatus.paid.name).desc(),
		)

	return render_template('admin_order_list.html', orders=orders)


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

	if session.get('order_id') == id:
		session.pop('order_id', None)

	flash('Order was deleted successfully')

	return redirect(url_for('admin_order_list'))


@app.route('/order/list')
def order_list():
	orders = DBSession.query(Order)\
		.order_by(
			(Order.status == OrderStatus.paid.name).desc(),
		)

	return render_template('order_list.html', orders=orders)


@app.route('/order/<int:id>/view')
def order_view():
	order = DBSession.query(Order).get(id)

	if not order:
		flash('Order not found')

		return redirect(url_for('order_list'))

	return render_template('order_view.html', order=order)
