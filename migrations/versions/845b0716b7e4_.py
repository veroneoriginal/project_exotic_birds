"""empty message

Revision ID: 845b0716b7e4
Revises: 58aa1e86dd89
Create Date: 2024-06-14 23:00:16.856635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '845b0716b7e4'
down_revision = '58aa1e86dd89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint('comments_parent_comment_id_fkey', type_='foreignkey')
        batch_op.drop_column('notification')
        batch_op.drop_column('parent_comment_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_comment_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('notification', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('comments_parent_comment_id_fkey', 'comments', ['parent_comment_id'], ['id'])

    # ### end Alembic commands ###
