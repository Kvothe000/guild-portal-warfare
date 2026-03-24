"""Fase 4 — Upgrade existing guardian_spirits + create equipment table

Revision ID: fa4_progression_v1
Revises: v2_veil_of_dominion
Create Date: 2025-03-23

guardian_spirits ALREADY EXISTS (from 9c96d635287b / v2_veil_of_dominion).
We only need to ADD the new columns (element, passive_name, passive_description,
stat_hp, stat_atk, stat_def, stat_spd, obtained_at) and CREATE equipment table.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'fa4_progression_v1'
# Merge dos dois branches paralelos:
# - 9c96d635287b = cadeia principal do banco (atual)
# - v2_veil_of_dominion = branch com alterações de modelos v2 (não aplicado ao banco)
down_revision = ('9c96d635287b', 'v2_veil_of_dominion')
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================================
    # guardian_spirits — add missing columns (table already exists)
    # Use try/except so re-running is safe
    # =========================================================================
    with op.batch_alter_table('guardian_spirits') as batch_op:
        try:
            batch_op.add_column(sa.Column('element',             sa.String(), nullable=True, server_default='Fogo'))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('level',               sa.Integer(), nullable=True, server_default='1'))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('passive_name',        sa.String(), nullable=True, server_default=''))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('passive_description', sa.Text(), nullable=True, server_default=''))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('stat_hp',  sa.Integer(), nullable=True, server_default='0'))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('stat_atk', sa.Integer(), nullable=True, server_default='0'))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('stat_def', sa.Integer(), nullable=True, server_default='0'))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('stat_spd', sa.Integer(), nullable=True, server_default='0'))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column('obtained_at', sa.DateTime(), nullable=True))
        except Exception:
            pass

    # =========================================================================
    # equipment — create fresh (does NOT exist yet)
    # =========================================================================
    op.create_table(
        'equipment',
        sa.Column('id',        sa.String(), nullable=False),
        sa.Column('player_id', sa.String(), nullable=False),
        sa.Column('hero_id',   sa.String(), nullable=True),
        sa.Column('name',      sa.String(), nullable=False),
        sa.Column('slot',      sa.String(), nullable=False),
        sa.Column('rarity',    sa.String(), nullable=False),
        sa.Column('level',     sa.Integer(), nullable=True, server_default='1'),
        sa.Column('max_level', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('stat_atk',       sa.Integer(), nullable=True),
        sa.Column('stat_def',       sa.Integer(), nullable=True),
        sa.Column('stat_hp',        sa.Integer(), nullable=True),
        sa.Column('stat_spd',       sa.Integer(), nullable=True),
        sa.Column('stat_crit_rate', sa.Float(),   nullable=True),
        sa.Column('stat_crit_dmg',  sa.Float(),   nullable=True),
        sa.Column('set_name',  sa.String(), nullable=True),
        sa.Column('set_bonus', sa.Text(),   nullable=True),
        sa.Column('obtained_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['hero_id'],   ['heroes.id'],  ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_equipment_player_id', 'equipment', ['player_id'])
    op.create_index('ix_equipment_hero_id',   'equipment', ['hero_id'])


def downgrade():
    op.drop_table('equipment')
    # Não fazemos downgrade dos ALTER TABLE de guardian_spirits para não
    # corromper dados de jogadores existentes.
