from flask import url_for

from sqlalchemy import (
	Column,
	Integer,
	Numeric,
	Unicode,
)

from shop.database import Base

from . import check_qty_positive


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
