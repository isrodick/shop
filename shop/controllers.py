from flask import (
	request,
	redirect,
	url_for,
    render_template,
    flash,
)

from sqlalchemy.exc import SQLAlchemyError

from shop import app
from shop.database import DBSession
from shop.models import (
    Product,
    Order,
    OrderProduct,
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

		return redirect(url_for('product_edit', id=product.id))

	flash('Product was deleted successfully')

	return redirect(url_for('product_list'))


@app.route('/')
def product_list():
    products = DBSession.query(Product).order_by(Product.title.asc())

    return render_template('product_list.html', products=products)
