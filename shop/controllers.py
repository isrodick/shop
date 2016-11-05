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
	ProductForm,
	OrderPayForm,
)

import uuid


@app.route('/admin/product/list')
def admin_product_list():
    products = DBSession.query(Product).order_by(Product.title.asc())

    return render_template('admin_product_list.html', products=products)


@app.route('/admin/product/new', methods=['GET', 'POST'])
def admin_product_new():
	form = ProductForm(request.POST)

	if request.method == 'POST' and form.validate():
		product = Product()

		product.title = form.title.data
		product.prie = form.prie.data
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

	form = ProductForm(request.POST, product)

	if request.method == 'POST' and form.validate():
		form.populate_obj(products)

		DBSession.add(product)
		DBSession.commit()

		flash('Product was updated successfully')

		return redirect(url_for('admin_product_list'))
	elif request.method == 'POST':
		flash('Validation error. Please enter the correct data')

	return render_template('admin_product_edit.html', form=form)


@app.route('/admin/product/<int:id>/delete', methods=['POST'])
def admin_product_delete(id):
	product = DBSession.query(Product).get(id)

	if not product:
		flash('Product not found')

		return redirect(url_for('admin_product_list'))

	try:
		DBSession.delete(product)
		DBSession.commit()
	except SQLAlchemyError as e:
		print(e)
		flash('Product could not be deleted')

		DBSession.rollback()

		return redirect(url_for('admin_product_edit', id=product.id))

	flash('Product was deleted successfully')

	return redirect(url_for('admin_product_list'))


@app.route('/')
def product_list():
	products = DBSession.query(Product).order_by(Product.title.asc())

	return render_template(
		'product_list.html',
		products=products,
		add_basket_id=str(uuid.uuid1()),
	)


@app.route('/basket', methods=['GET', 'POST'])
def basket():
	order = Order.get_from_session()

	if not order:
		flash('Order not found')

		return redirect(url_for('product_list'))

	form = OrderPayForm(request.POST, order)

	if request.method == 'POST' and form.validate():
		form.populate_obj(order)
		order.status = OrderStatus.paid

		DBSession.add(order)
		DBSession.commit()

		session.pop('order_id', None)

		flash('Order paid successfully')

		return redirect(url_for('task_list'))
	elif request.method == 'POST':
		flash('Validation error. Please enter the correct data')

	return render_template('basket.html', form=form, payment_methods=PaymentMethod)


@app.route('/order/product/<int:product_id>/add')
def order_product_add(product_id):
	product = DBSession.query(Product).get(product_id)

	if not product:
		abort(404)	## temporarily

	if product.qty < 1:
		abort(400)	## temporarily

	try:
		order = Order.get_from_session(create=True)
	except FlushError as e:
		abort(400)

	order_product = OrderProduct()
	order_product.order_id = order.id
	order_product.product_id = product.id
	order_product.qty = 1

	DBSession.add(order_product)
	DBSession.commit()

	return jsonify(
		total_products_qty=sum(link.qty for link in order.links),
	)


@app.route('/order/product/<int:product_id>/qty', methods=['POST'])
def order_product_qty(product_id):
	if 'order_id' not in session:
		abort(404)

	order_product = DBSession.query(OrderProduct).get(session['order_id'], product_id)

	if not order_product:
		abort(404)

	if order_product.product.qty < request.form['qty']:
		abort(400)	## temporarily

	order_product.qty = request.form['qty']

	try:
		DBSession.add(order_product)
		DBSession.flush()
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
		total_price=sum(link.qty * link.product.price for link in order_product.order.links),
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
		total_price=sum(link.qty * link.product.price for link in order_product.order.links),
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
