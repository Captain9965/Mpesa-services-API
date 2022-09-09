"""empty message

Revision ID: 57aaa43515ca
Revises: fef8b949e139
Create Date: 2022-09-01 09:05:19.696025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57aaa43515ca'
down_revision = 'fef8b949e139'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'response_dump', ['uuid_'])
    op.create_unique_constraint(None, 'stk_request_dump', ['uuid_'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'stk_request_dump', type_='unique')
    op.drop_constraint(None, 'response_dump', type_='unique')
    # ### end Alembic commands ###