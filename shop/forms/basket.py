import itertools

from wtforms import (
	Form,
	SelectField,
	IntegerField,
	validators,
)

from shop.models.enums import PaymentMethod

from . import submit


class BasketPayForm(Form, metaclass=submit('Pay')):
	payment_method = SelectField(
		'Payment Method',
		[
			validators.InputRequired(),
			validators.AnyOf(PaymentMethod._member_names_),
		],
		choices=list(itertools.chain([(None, '-- Please Select --')], PaymentMethod.get_options())),
	)


class BasketProductQtyForm(Form):
	qty = IntegerField('QTY', [
		validators.InputRequired(),
		validators.NumberRange(min=1),
	])

	def validate(self, product):
		valid = False

		if super().validate():
			valid = True

			if product.qty < self.qty.data:
				valid = False
				self.qty.errors.append('Only {} product(s) in stock'.format(product.qty))

		return valid
