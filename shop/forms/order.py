import itertools

from wtforms import (
	Form,
	SelectField,
	validators,
)

from shop.models.enums import PaymentMethod

from . import submit


class OrderPayForm(Form, metaclass=submit('Pay')):
	payment_method = SelectField(
		'Payment Method',
		[
			validators.InputRequired(),
			validators.AnyOf(PaymentMethod._member_names_),
		],
		choices=list(itertools.chain([(None, '-- Please Select --')], PaymentMethod.get_options())),
	)
