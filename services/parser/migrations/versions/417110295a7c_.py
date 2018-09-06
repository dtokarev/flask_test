"""empty message

Revision ID: 417110295a7c
Revises: 
Create Date: 2018-09-04 17:11:11.017431

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '417110295a7c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=True),
    sa.Column('value', sa.String(length=2000), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )

    op.create_table('search',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('title_ru', sa.String(length=250), nullable=True),
    sa.Column('title_en', sa.String(length=250), nullable=True),
    sa.Column('kinopoisk_id', sa.String(length=250), nullable=True),
    sa.Column('error', sa.Text(length=16000000), nullable=True),
    sa.Column('year', sa.SmallInteger(), nullable=True),
    sa.Column('type', sa.Enum('MOVIE', 'SERIES', name='resourcetype'), nullable=False),
    sa.Column('status', sa.Enum('NEW', 'PROCESSING', 'ERROR', 'NOT_FOUND', 'COMPLETED', name='statuses'), nullable=False),
    sa.Column('import_source', sa.String(length=250), nullable=True),
    sa.Column('import_source_id', sa.String(length=250), nullable=True),
    sa.Column('raw', sa.Text(length=16000000), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('kinopoisk_id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_search_status'), 'search', ['status'], unique=False)
    op.create_index(op.f('ix_search_type'), 'search', ['type'], unique=False)

    op.create_table('parsed_data',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('kinopoisk_id', sa.String(length=250), nullable=True),
    sa.Column('import_source_id', sa.String(length=250), nullable=True),
    sa.Column('page_link', sa.String(length=250), nullable=True),
    sa.Column('raw_page_data', sa.Text(length=16000000), nullable=True),
    sa.Column('quality', sa.String(length=250), nullable=True),
    sa.Column('format', sa.String(length=250), nullable=True),
    sa.Column('country', sa.String(length=250), nullable=True),
    sa.Column('size', sa.String(length=250), nullable=True),
    sa.Column('title', sa.Text(length=65535), nullable=True),
    sa.Column('title_ru', sa.String(length=250), nullable=True),
    sa.Column('title_en', sa.String(length=250), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('translation', sa.String(length=250), nullable=True),
    sa.Column('translation_code', sa.String(length=250), nullable=True),
    sa.Column('subtitle', sa.String(length=250), nullable=True),
    sa.Column('subtitle_format', sa.String(length=250), nullable=True),
    sa.Column('genre', sa.Text(length=65535), nullable=True),
    sa.Column('description', sa.Text(length=65535), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('casting', sa.Text(length=65535), nullable=True),
    sa.Column('video_info', sa.Text(length=65535), nullable=True),
    sa.Column('audio_info', sa.Text(length=65535), nullable=True),
    sa.Column('magnet_link', sa.Text(length=65535), nullable=True),
    sa.Column('search_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['search_id'], ['search.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )


def downgrade():
    op.drop_table('parsed_data')
    op.drop_index(op.f('ix_search_type'), table_name='search')
    op.drop_index(op.f('ix_search_status'), table_name='search')
    op.drop_table('search')
    op.drop_table('config')
