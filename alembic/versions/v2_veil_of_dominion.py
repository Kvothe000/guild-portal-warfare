"""
Veil of Dominion — Migration v2.0
Rename: guilds → clans
Add: clan_boss_sessions, clan_boss_damage, player_commanders, guardian_spirits
Modify: players (guild_id → clan_id), heroes (breakthrough cols, death_cooldown_until),
        portals (map_x, map_y, controlling_clan_id), player_wallets (spirit_tickets),
        gacha_banners (soft_pity_start, expires_at, is_active),
        player_progress (daily_boss_attacks_remaining)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "v2_veil_of_dominion"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================
    # 1. RENAME guilds → clans
    # =========================================================
    op.rename_table("guilds", "clans")

    # Adicionar coluna description ao clans
    op.add_column("clans", sa.Column("description", sa.Text(), nullable=True))

    # =========================================================
    # 2. PLAYERS — guild_id → clan_id
    # =========================================================
    # Dropar FK antiga se existir
    try:
        op.drop_constraint("players_guild_id_fkey", "players", type_="foreignkey")
    except Exception:
        pass  # FK pode ter nome diferente

    # Renomear coluna guild_id → clan_id
    op.alter_column("players", "guild_id", new_column_name="clan_id")

    # Criar nova FK
    op.create_foreign_key(
        "players_clan_id_fkey", "players", "clans", ["clan_id"], ["id"]
    )

    # =========================================================
    # 3. PLAYER_COMMANDERS — nova tabela
    # =========================================================
    op.create_table(
        "player_commanders",
        sa.Column("player_id", sa.String(), sa.ForeignKey("players.id"), primary_key=True),
        sa.Column("order_class", sa.String(), nullable=False),
        sa.Column("level", sa.Integer(), default=1, nullable=False, server_default="1"),
        sa.Column("experience", sa.Integer(), default=0, nullable=False, server_default="0"),
        sa.Column("active_basic_id", sa.String(), nullable=True),
        sa.Column("active_active_id", sa.String(), nullable=True),
        sa.Column("active_ultimate_id", sa.String(), nullable=True),
        sa.Column("active_passive_id", sa.String(), nullable=True),
        sa.Column("team_slot", sa.Integer(), default=5, nullable=False, server_default="5"),
        sa.Column("max_hp", sa.Integer(), default=2000, nullable=False, server_default="2000"),
        sa.Column("current_hp", sa.Integer(), default=2000, nullable=False, server_default="2000"),
        sa.Column("attack", sa.Integer(), default=150, nullable=False, server_default="150"),
        sa.Column("defense", sa.Integer(), default=120, nullable=False, server_default="120"),
        sa.Column("speed", sa.Integer(), default=110, nullable=False, server_default="110"),
    )

    # =========================================================
    # 4. CLAN_BOSS_SESSIONS — nova tabela
    # =========================================================
    op.create_table(
        "clan_boss_sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("clan_id", sa.String(), sa.ForeignKey("clans.id"), nullable=False),
        sa.Column("boss_name", sa.String(), default="Lich Soberano de Valdris", nullable=True),
        sa.Column("boss_max_hp", sa.Integer(), default=10000000, nullable=False, server_default="10000000"),
        sa.Column("boss_current_hp", sa.Integer(), default=10000000, nullable=False, server_default="10000000"),
        sa.Column("boss_level", sa.Integer(), default=1, nullable=False, server_default="1"),
        sa.Column("status", sa.String(), default="Active", nullable=False, server_default="Active"),
        sa.Column("week_start", sa.DateTime(), nullable=True),
        sa.Column("week_end", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    # =========================================================
    # 5. CLAN_BOSS_DAMAGE — nova tabela
    # =========================================================
    op.create_table(
        "clan_boss_damage",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("session_id", sa.String(), sa.ForeignKey("clan_boss_sessions.id"), nullable=True),
        sa.Column("player_id", sa.String(), sa.ForeignKey("players.id"), nullable=True),
        sa.Column("damage_dealt", sa.Integer(), default=0, nullable=False, server_default="0"),
        sa.Column("attacks_used", sa.Integer(), default=0, nullable=False, server_default="0"),
        sa.Column("last_attack_at", sa.DateTime(), nullable=True),
    )

    # =========================================================
    # 6. GUARDIAN_SPIRITS — nova tabela
    # =========================================================
    op.create_table(
        "guardian_spirits",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("player_id", sa.String(), sa.ForeignKey("players.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("rarity", sa.String(), default="A", nullable=True),
        sa.Column("is_equipped", sa.Boolean(), default=False, nullable=False, server_default="false"),
        sa.Column("chase_trigger", sa.String(), nullable=True),
        sa.Column("chase_effect", sa.String(), nullable=True),
        sa.Column("damage_multiplier", sa.Float(), default=1.5, nullable=False, server_default="1.5"),
    )

    # =========================================================
    # 7. HEROES — adicionar novas colunas
    # =========================================================
    op.add_column("heroes", sa.Column("breakthrough_level", sa.Integer(), server_default="0", nullable=False))
    op.add_column("heroes", sa.Column("breakthrough_fragments", sa.Integer(), server_default="0", nullable=False))
    op.add_column("heroes", sa.Column("death_cooldown_until", sa.DateTime(), nullable=True))

    # =========================================================
    # 8. PORTALS — adicionar coordenadas de mapa + clan
    # =========================================================
    op.add_column("portals", sa.Column("map_x", sa.Float(), server_default="0.0", nullable=False))
    op.add_column("portals", sa.Column("map_y", sa.Float(), server_default="0.0", nullable=False))

    # Renomear guild_id → clan_id se existir
    try:
        op.drop_constraint("portals_controlling_guild_id_fkey", "portals", type_="foreignkey")
        op.alter_column("portals", "controlling_guild_id", new_column_name="controlling_clan_id")
        op.create_foreign_key("portals_controlling_clan_id_fkey", "portals", "clans", ["controlling_clan_id"], ["id"])
    except Exception:
        op.add_column("portals", sa.Column("controlling_clan_id", sa.String(), sa.ForeignKey("clans.id"), nullable=True))

    # =========================================================
    # 9. PLAYER_WALLETS — adicionar spirit_tickets
    # =========================================================
    op.add_column("player_wallets", sa.Column("spirit_tickets", sa.Integer(), server_default="0", nullable=False))
    # Renomear crystals → crystals_premium se necessário
    try:
        op.alter_column("player_wallets", "crystals", new_column_name="crystals_premium")
    except Exception:
        pass

    # =========================================================
    # 10. GACHA_BANNERS — adicionar soft_pity, expires_at, is_active
    # =========================================================
    op.add_column("gacha_banners", sa.Column("soft_pity_start", sa.Integer(), server_default="75", nullable=False))
    op.add_column("gacha_banners", sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False))
    op.add_column("gacha_banners", sa.Column("expires_at", sa.DateTime(), nullable=True))

    # =========================================================
    # 11. PLAYER_PROGRESS — adicionar daily_boss_attacks_remaining
    # =========================================================
    op.add_column("player_progress", sa.Column(
        "daily_boss_attacks_remaining", sa.Integer(), server_default="3", nullable=False
    ))


def downgrade() -> None:
    # Reverter na ordem inversa
    op.drop_column("player_progress", "daily_boss_attacks_remaining")
    op.drop_column("gacha_banners", "expires_at")
    op.drop_column("gacha_banners", "is_active")
    op.drop_column("gacha_banners", "soft_pity_start")
    op.drop_column("player_wallets", "spirit_tickets")
    op.drop_column("portals", "map_x")
    op.drop_column("portals", "map_y")
    op.drop_column("heroes", "death_cooldown_until")
    op.drop_column("heroes", "breakthrough_fragments")
    op.drop_column("heroes", "breakthrough_level")
    op.drop_table("guardian_spirits")
    op.drop_table("clan_boss_damage")
    op.drop_table("clan_boss_sessions")
    op.drop_table("player_commanders")
    op.rename_table("clans", "guilds")
