from wtforms import (
	Form,
	SubmitField,
	StringField,
	DecimalField,
	IntegerField,
	SelectField,
	validators,
)

from shop.models import PaymentMethod


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
		choices=PaymentMethod.get_options(),
	)
