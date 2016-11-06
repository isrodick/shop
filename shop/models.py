from flask import (
	session,
	url_for,
)

from sqlalchemy import (
	CheckConstraint,
	ForeignKey,
	Column,
	Integer,
	Numeric,
	Unicode,
	Enum,
)
from sqlalchemy.orm import relation
from sqlalchemy.orm.collections import attribute_mapped_collection

import enum

from shop.database import (
	Base,
	DBSession,
)


def check_qty_positive(tablename):
	return CheckConstraint('qty >= 0', name='{}_check_qty_positive'.format(tablename))


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


class Product(Base):
	__tablename__ = 'product'
	__table_args__ = (
		check_qty_positive(__tablename__),
	)

	id = Column(Integer, primary_key=True)
	title = Column(Unicode(255), nullable=False, unique=True)
	price = Column(Numeric(precision=12, scale=4), nullable=False)
	image_url = Column(Unicode(255))
	qty = Column(Integer, nullable=False)

	def get_img_url(self):
		return self.image_url if self.image_url else url_for('static', filename='imgs/no_image.png')

	def in_stock(self):
		return True if self.qty > 0 else False


class Order(Base):
	__tablename__ = 'order'
	__table_args__ = (
		CheckConstraint(
			'(status = \'{paid}\' AND payment_method IS NOT NULL) OR (status = \'{new}\' AND payment_method IS NULL)'.format(
				paid=OrderStatus.paid.name,
				new=OrderStatus.new.name
			),
			name='{}_payment_method_contstraint'.format(__tablename__),
		),
	)

	id = Column(Integer, primary_key=True)
	status = Column(Enum(OrderStatus), nullable=False)
	payment_method = Column(Enum(PaymentMethod))

	product_items = relation('OrderProduct', order_by='OrderProduct.product_id.asc()', cascade='all, delete-orphan', collection_class=attribute_mapped_collection('product_id'))
	links = relation('OrderProduct', backref='order', lazy='subquery', cascade='all, delete-orphan')

	@classmethod
	def get_from_session(cls, create=False):
		order = None

		if 'order_id' in session:
			order = DBSession.query(Order).get(session['order_id'])
		elif create:
			order = Order()
			order.status = OrderStatus.new

			try:
				DBSession.add(order)
				DBSession.flush()
			except SQLAlchemyError as e:
				print(e)

				DBSession.rollback()

				abort(400)	## temporarily

			session['order_id'] = order.id

		return order

	def get_total_price(self):
		return sum(link.qty * link.product.price for link in self.links)

	def get_total_product_qty(self):
		return sum(link.qty for link in self.links)

	@classmethod
	def get_tatal_product_qty_from_session(cls):
		order = None

		if 'order_id' in session:
			order = order = DBSession.query(cls).get(session['order_id'])

		if not order:
			return None

		return order.get_total_product_qty()


class OrderProduct(Base):
	__tablename__ = 'order_product'
	__table_args__ = (
		check_qty_positive(__tablename__),
	)

	order_id = Column(Integer, ForeignKey('order.id', onupdate='CASCADE', ondelete='CASCADE'), index=True, primary_key=True)
	product_id = Column(Integer, ForeignKey('product.id', onupdate='CASCADE', ondelete='CASCADE'), index=True, primary_key=True)
	qty = Column(Integer, nullable=False)

	product = relation(Product)
