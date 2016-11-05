"""empty message

Revision ID: 41bb354ba4d8
Revises: None
Create Date: 2016-11-04 00:36:00.927260

"""

# revision identifiers, used by Alembic.
revision = '41bb354ba4d8'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('new', 'paid', name='orderstatus'), nullable=False),
    sa.Column('payment_method', sa.Enum('liqpay', 'privat24', 'paypal', name='paymentmethod'), nullable=True),
    sa.CheckConstraint("(status = 'paid' AND payment_method IS NOT NULL) OR (status = 'new' AND payment_method IS NULL)", name='order_payment_method_contstraint'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Unicode(length=255), nullable=False),
    sa.Column('price', sa.Numeric(precision=12, scale=4), nullable=False),
    sa.Column('image_url', sa.Unicode(length=255), nullable=True),
    sa.Column('qty', sa.Integer(), nullable=False),
    sa.CheckConstraint('qty >= 0', name='product_check_qty_positive'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('order_product',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('qty', sa.Integer(), nullable=False),
    sa.CheckConstraint('qty >= 0', name='order_product_check_qty_positive'),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('order_id', 'product_id')
    )
    op.create_index(op.f('ix_order_product_order_id'), 'order_product', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_product_product_id'), 'order_product', ['product_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_order_product_product_id'), table_name='order_product')
    op.drop_index(op.f('ix_order_product_order_id'), table_name='order_product')
    op.drop_table('order_product')
    op.drop_table('product')
    op.drop_table('order')
    ### end Alembic commands ###
