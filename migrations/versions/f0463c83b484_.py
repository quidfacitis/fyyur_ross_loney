"""empty message

Revision ID: f0463c83b484
Revises: ee718e58c434
Create Date: 2020-10-02 09:46:31.095755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0463c83b484'
down_revision = 'ee718e58c434'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artistgenres',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('genre', sa.String(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('Artist', sa.Column('citystate_id', sa.Integer(), nullable=False))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=200), nullable=True))
    op.create_foreign_key(None, 'Artist', 'citystate', ['citystate_id'], ['id'])
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'Artist', type_='foreignkey')
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'citystate_id')
    op.drop_table('artistgenres')
    # ### end Alembic commands ###
