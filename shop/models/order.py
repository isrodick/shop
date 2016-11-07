from flask import session

from sqlalchemy import (
	CheckConstraint,
	ForeignKey,
	Column,
	Integer,
	Enum,
)
from sqlalchemy.orm import relation
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.exc import SQLAlchemyError


from shop.database import (
	Base,
	DBSession,
)

from .enums import (
	OrderStatus,
	PaymentMethod,
)

from . import check_qty_positive

from .product import Product


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
			order = DBSession.query(cls).get(session['order_id'])

		if not order and create:
			order = cls()
			order.status = OrderStatus.new

			try:
				DBSession.add(order)
				DBSession.flush()
			except SQLAlchemyError as e:
				print(e)

				DBSession.rollback()

				# abort(400)	## temporarily

			session['order_id'] = order.id

		return order

	@classmethod
	def get_product_ids_from_session(cls):
		order = cls.get_from_session()

		if not order:
			return None

		return tuple(link.product_id for link in order.links)

	def has_products(self):
		return self.get_total_product_qty() > 0

	def get_total_price(self):
		return sum(link.qty * link.product.price for link in self.links)

	def get_total_product_qty(self):
		return sum(link.qty for link in self.links)

	@classmethod
	def get_tatal_product_qty_from_session(cls):
		order = cls.get_from_session()

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
