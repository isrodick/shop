from flask import request

from wtforms import (
	Form,
	SubmitField,
	StringField,
	DecimalField,
	IntegerField,
	SelectField,
	validators,
)

from shop.database import DBSession
from shop.models import (
	Product,
	PaymentMethod,
)

import itertools

def submit(title):
	def metaclass(name, parents, attributes):
		attributes['submit'] = SubmitField(title, [validators.InputRequired()])
		return type(name, parents, attributes)
	return metaclass


class ProductForm(Form):
	title = StringField('Title', [validators.InputRequired()])
	price = DecimalField('Price', [validators.InputRequired()])
	image_url = StringField('Image URL')
	qty = IntegerField('QTY', [
		validators.InputRequired(),
		validators.NumberRange(min=0),
	])

	def validate(self, current_product=None):
		valid = False

		if request.method == 'POST' and super().validate():
			valid = True

			query = DBSession.query(Product)\
				.filter(Product.title == self.title.data)
			if current_product:
				query = query.filter(Product.id != current_product.id)
			_product = query.first()

			if _product:
				valid = False
				self.title.errors.append('Product with this title already exists.')

		return valid


class ProductNewForm(ProductForm, metaclass=submit('Create')):
	pass


class ProductEditForm(ProductForm, metaclass=submit('Save')):
	pass


class OrderPayForm(Form):
	submit = SubmitField('Pay', [validators.InputRequired()])
	payment_method = SelectField(
		'Payment Method',
		[
			validators.InputRequired(),
			validators.AnyOf(PaymentMethod._member_names_),
		],
		choices=list(itertools.chain([(None, '-- Please Select --')], PaymentMethod.get_options())),
	)
