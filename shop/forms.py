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


class ProductForm(Form):
	submit = SubmitField('Save', [validators.InputRequired()])
	title = StringField('Title', [validators.InputRequired()])
	price = DecimalField('Price', [validators.InputRequired()])
	image_url = StringField('Title')
	qty = IntegerField('QTY', [
		validators.InputRequired(),
		validators.NumberRange(min=0),
	])


class OrderPayForm(Form):
	submit = SubmitField('Pay', [validators.InputRequired()])
	payment_method = SelectField(
		'Payment Method',
		choices=PaymentMethod.get_options(),
		[
			validators.InputRequired(),
			validators.AnyOf(PaymentMethod._member_names_),
		],
	)
