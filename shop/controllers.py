from flask import (
	request,
	redirect,
	url_for,
    render_template,
    flash,
)

from shop import app
from shop.database import DBSession
from shop.models import (
    Product,
    Order,
    OrderProduct,
)


@app.route('/product/new', method=['GET', 'POST'])
def product_new():
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


@app.route('/')
def product_list():
    products = DBSession.query(Product).order_by(Product.title.asc())

    return render_template('product_list.html', products=products)
