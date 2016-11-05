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

from shop.database import Base


def check_qty_positive(tablename):
	return CheckConstraint('qty >= 0', name='{}_check_qty_positive'.format(tablename))


class OrderStatus(enum.Enum):
	new = 'New'
	paid = 'Paid'


class PaymentMethod(enum.Enum):
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


class OrderProduct(Base):
	__tablename__ = 'order_product'
	__table_args__ = (
		check_qty_positive(__tablename__),
	)

	order_id = Column(Integer, ForeignKey('order.id', onupdate='CASCADE', ondelete='CASCADE'), index=True, primary_key=True)
	product_id = Column(Integer, ForeignKey('product.id', onupdate='CASCADE', ondelete='CASCADE'), index=True, primary_key=True)
	qty = Column(Integer, nullable=False)

	product = relation(Product)
