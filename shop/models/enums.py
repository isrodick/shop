import enum


class _Enum(enum.Enum):
	@classmethod
	def get_options(cls):
		return [(key, cls._member_map_[key].value) for key in cls._member_map_]


class OrderStatus(_Enum):
	new = 'New'
	paid = 'Paid'


class PaymentMethod(_Enum):
	liqpay = 'LiqPay'
	privat24 = 'Privat24'
	paypal = 'PayPal'
