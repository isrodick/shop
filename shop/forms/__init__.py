from wtforms import (
	SubmitField,
	validators,
)


def submit(title):
	def metaclass(name, parents, attributes):
		attributes['submit'] = SubmitField(title, [validators.InputRequired()])
		return type(name, parents, attributes)
	return metaclass
