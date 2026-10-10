"""Restore missing formats table.

The database was stamped at 77fd92f0ef18, but the 'formats' table that
revision creates is absent (the albums.format_id foreign key still points
at it). This repair revision brings the database back in line with
77fd92f0ef18 so that later revisions can run as written.

Revision ID: 9c0ab3d41f55
Revises: 77fd92f0ef18
Create Date: 2026-10-10 19:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c0ab3d41f55'
down_revision = '77fd92f0ef18'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if not sa.inspect(bind).has_table('formats'):
        op.create_table('formats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
        )


def downgrade():
    op.drop_table('formats')
