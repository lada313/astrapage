from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('clients',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('phone', sa.String(32), index=True),
        sa.Column('email', sa.String(255), index=True),
        sa.Column('client_external_id', sa.String(128), index=True),
        sa.Column('first_name', sa.String(128)),
        sa.Column('last_name', sa.String(128)),
        sa.Column('middle_name', sa.String(128)),
        sa.Column('city', sa.String(128)),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(16)),
        sa.Column('consent_email', sa.Boolean(), default=None),
        sa.Column('consent_sms', sa.Boolean(), default=None),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_table('loyalty_cards',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('card_id', sa.String(64), index=True),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('clients.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tier', sa.String(64)),
        sa.Column('points', sa.Numeric(18,4)),
        sa.Column('balance', sa.Numeric(18,4)),
        sa.Column('issued_at', sa.Date()),
        sa.Column('expires_at', sa.Date()),
        sa.Column('status', sa.String(64))
    )
    op.create_table('products',
        sa.Column('sku', sa.String(64), primary_key=True),
        sa.Column('title', sa.String(255)),
        sa.Column('category', sa.String(128)),
        sa.Column('price', sa.Numeric(18,2))
    )
    op.create_table('purchases',
        sa.Column('order_id', sa.String(64), primary_key=True),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('clients.id', ondelete='SET NULL'), nullable=True),
        sa.Column('phone', sa.String(32), index=True),
        sa.Column('email', sa.String(255), index=True),
        sa.Column('order_date', sa.DateTime()),
        sa.Column('total_amount', sa.Numeric(18,2)),
        sa.Column('currency', sa.String(8))
    )
    op.create_table('purchase_items',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('order_id', sa.String(64), sa.ForeignKey('purchases.order_id', ondelete='CASCADE')),
        sa.Column('sku', sa.String(64)),
        sa.Column('title', sa.String(255)),
        sa.Column('qty', sa.Numeric(18,3)),
        sa.Column('price', sa.Numeric(18,2))
    )
    op.create_table('segments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(128)),
        sa.Column('description', sa.Text()),
        sa.Column('filters_json', sa.Text()),
        sa.Column('size', sa.Integer),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_table('segment_members',
        sa.Column('segment_id', sa.Integer, sa.ForeignKey('segments.id', ondelete='CASCADE')),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('clients.id', ondelete='CASCADE'))
    )

def downgrade():
    op.drop_table('segment_members')
    op.drop_table('segments')
    op.drop_table('purchase_items')
    op.drop_table('purchases')
    op.drop_table('products')
    op.drop_table('loyalty_cards')
    op.drop_table('clients')
