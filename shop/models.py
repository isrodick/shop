from sqlalchemy import (
	CheckConstraint,
	ForeignKey,
	Column,
	Integer,
	Numeric,
	Unicode,
)
from sqlalchemy.orm import relation

from shop.database import Base


def check_qty_positive(tablename):
	return CheckConstraint('qty >= 0', name='{}_check_qty_positive'.format(tablename))


class Product(Base):
	__tablename__ = 'product'
	__table_args__ = (
		check_qty_positive(__tablename__),
	)

	id = Column(Integer, primary_key=True)
	title = Column(Unicode(255), nullable=False)
	price = Column(Numeric(precision=12, scale=4), nullable=False)
	image_url = Column(Unicode(255))
	qty = Column(Integer, nullable=False)


class Order(Base):
	__tablename__ = 'order'

	id = Column(Integer, primary_key=True)
	status = Column(Integer, nullable=False)

	products = relation('OrderProduct', backref='order', lazy='subquery', cascade='all, delete-orphan')


class OrderProduct(Base):
	__tablename__ = 'order_product'
	__table_args__ = (
		check_qty_positive(__tablename__),
	)

	order_id = Column(Integer, ForeignKey('order.id', onupdate='CASCADE', ondelete='CASCADE'), index=True, primary_key=True)
	product_id = Column(Integer, ForeignKey('product.id', onupdate='CASCADE', ondelete='CASCADE'), index=True, primary_key=True)
	qty = Column(Integer, nullable=False)

	product = relation(Product)
