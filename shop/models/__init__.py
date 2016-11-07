from sqlalchemy import CheckConstraint


__all__ = ['enums', 'order', 'product']


def check_qty_positive(tablename):
	return CheckConstraint('qty >= 0', name='{}_check_qty_positive'.format(tablename))
