from flask import (
	request,
	redirect,
	url_for,
	render_template,
	flash,
	jsonify,
)

from sqlalchemy.exc import SQLAlchemyError

from shop import app
from shop.database import DBSession
from shop.models.product import Product
from shop.forms.product import (
	ProductNewForm,
	ProductEditForm,
)


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

		flash('warning;Product was created successfully')

		return redirect(url_for('admin_product_edit', id=product.id))
	elif request.method == 'POST':
		flash('danger;Validation error. Please enter the correct data')

	return render_template('admin/product/new.html', form=form)


@app.route('/admin/product/<int:id>/edit', methods=['GET', 'POST'])
def admin_product_edit(id):
	product = DBSession.query(Product).get(id)

	if not product:
		flash('danger;Product not found')

		return redirect(url_for('admin_product_list'))

	form = ProductEditForm(request.form, product)

	if request.method == 'POST' and form.validate(current_product=product):
		form.populate_obj(product)

		DBSession.add(product)
		DBSession.commit()

		flash('warning;Product was updated successfully')

		return redirect(url_for('admin_product_list'))
	elif request.method == 'POST':
		flash('danger;Validation error. Please enter the correct data')

	return render_template('admin/product/edit.html', form=form, product=product)


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

	flash('warning;Product was deleted successfully')

	return jsonify(
		status='success',
		redirect_url=url_for('admin_product_list'),
	)
