from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid
import datetime
import enum
from database import Base

# Enums
class HeroRole(enum.Enum):
    Tank = "Tank"
    Carry = "Carry"
    Support = "Support"
    Control = "Control"

class PortalRarity(enum.Enum):
    C = "C"
    B = "B"
    A = "A"
    S = "S"

class BattleStatus(enum.Enum):
    Pending = "Pending"
    Resolved = "Resolved"

class SkillType(enum.Enum):
    Basic = "Basic"
    Active = "Active"
    Ultimate = "Ultimate"
    Passive = "Passive"

class EffectType(enum.Enum):
    Damage = "Damage"
    Heal = "Heal"
    Taunt = "Taunt"
    Buff = "Buff"

# Funções utilitárias
def generate_uuid():
    return str(uuid.uuid4())

class Guild(Base):
    __tablename__ = "guilds"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    players = relationship("Player", back_populates="guild")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    guild = relationship("Guild", back_populates="players")
    heroes = relationship("Hero", back_populates="player")
    
    # FASE 4: Relacionamento 1:1 com o painel de progressão PvE e AFK do jogador
    progress = relationship("PlayerProgress", back_populates="player", uselist=False)
    
    # FASE 7: Economia e Carteira do Jogador
    wallet = relationship("PlayerWallet", back_populates="player", uselist=False)

class Hero(Base):
    __tablename__ = "heroes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"))
    name = Column(String)
    role = Column(Enum(HeroRole))
    level = Column(Integer, default=1)
    max_hp = Column(Integer, default=100)
    current_hp = Column(Integer, default=100)
    
    # FASE 6: Mana/Energy System
    max_mana = Column(Integer, default=100)
    current_mana = Column(Integer, default=0)
    
    attack = Column(Integer, default=10)
    defense = Column(Integer, default=10)
    speed = Column(Integer, default=10)
    is_in_team = Column(Boolean, default=False)
    
    # FASE 5: Death Cooldown System (Anti-Whale Mechanic)
    # Se morto em uma Guerra de Portal, o herói recebe um timestamp futuro.
    # Até esse timestamp expirar, ele não pode atacar Portais.
    # Opcional no futuro: cobrar Cristais para reverter esse timestamp para NULL.
    death_cooldown_until = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    player = relationship("Player", back_populates="heroes")
    skills = relationship("Skill", back_populates="hero", cascade="all, delete-orphan")

# ==========================================
# FASE 6: Sistema de Habilidades (Combat Engine)
# ==========================================

class Skill(Base):
    """
    Representa uma Habilidade específica pertencente a um Herói.
    Em um Gacha em produção, isso clonaria um 'SkillTemplate' da definição do Herói base.
    """
    __tablename__ = "skills"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    hero_id = Column(String, ForeignKey("heroes.id"))
    
    name = Column(String)
    skill_type = Column(Enum(SkillType)) # Basic, Active, Ultimate, Passive
    
    # Restrições de uso
    cooldown = Column(Integer, default=0) # Turnos de CD
    energy_cost = Column(Integer, default=0) # Custo para conjurar
    
    # Lógica de Impacto
    effect_type = Column(Enum(EffectType)) # Damage, Heal, Taunt, Buff
    multiplier = Column(Float, default=1.0) # Multiplicador Ex: 1.5 = 150% do attack stat
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    hero = relationship("Hero", back_populates="skills")

class Portal(Base):
    __tablename__ = "portals"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    rarity = Column(Enum(PortalRarity))
    resource_type = Column(String)
    resource_generation_rate = Column(Integer)
    
    controlling_guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    controlling_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    defender_1_id = Column(String, ForeignKey("players.id"), nullable=True)
    defender_2_id = Column(String, ForeignKey("players.id"), nullable=True)
    defender_3_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    last_collected_at = Column(DateTime, nullable=True)

class Battle(Base):
    __tablename__ = "battles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    portal_id = Column(String, ForeignKey("portals.id"))
    
    attacker_guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    attacker_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    defender_guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    defender_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    attacker_1_id = Column(String, ForeignKey("players.id"))
    attacker_2_id = Column(String, ForeignKey("players.id"), nullable=True)
    attacker_3_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    status = Column(Enum(BattleStatus), default=BattleStatus.Pending)
    
    winner_guild_id = Column(String, ForeignKey("guilds.id"), nullable=True)
    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    # Para SQLite usaremos String ao invés de JSONB, será serializado no Python
    combat_log = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

# ==========================================
# FASE 4: Sitema PvE (Campanha) e Retenção Idle
# ==========================================

class CampaignStage(Base):
    """
    Representa uma fase fixa do modo Campanha (PvE).
    Define quão difícil é o combate e qual a 'renda passiva' (AFK) que o jogador
    ganha ao ter concluído esta fase. O muro de dificuldade substitui a Stamina.
    """
    __tablename__ = "campaign_stages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    # Exemplo: 101 (Mundo 1, Fase 1), 102 (Mundo 1, Fase 2)
    stage_number = Column(Integer, unique=True, index=True) 
    name = Column(String)
    
    # Multiplicador abstrato de status para os inimigos a serem gerados contra a engine
    difficulty_modifier = Column(Integer, default=1) 
    
    # Renda Passiva gerada por HORA no Caixa AFK. Quanto maior a fase, melhor o farm.
    afk_xp_per_hour = Column(Integer, default=60)
    afk_gold_per_hour = Column(Integer, default=120)


class PlayerProgress(Base):
    """
    Uma extensão 1:1 da tabela Player. Guarda tudo relacionado ao avanço
    matemático do jogador no tempo (Idle) e nos modos PvE. 
    Modularizado para evitar inflar colunas ativas na tabela 'players'.
    """
    __tablename__ = "player_progress"
    
    # A mesma ID do Player é a Primary Key aqui (Relação 1:1 absoluta)
    player_id = Column(String, ForeignKey("players.id"), primary_key=True)
    
    # Fase mais alta concluída (Define o teto de farm AFK atual)
    highest_stage_number = Column(Integer, default=0) 
    
    # Timestamp base do Idle System (Caixa AFK). Toda a lógica matemática F2P reside aqui.
    # Loot Retrotativo = (Now - last_afk_collection).horas * afk_rate_da_sua_highest_stage
    last_afk_collection = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Sistema de Tickets e Mecânicas Diárias Anti-Burnout (Limita mas não prende)
    daily_sweeps_remaining = Column(Integer, default=5) # Dungeons Sweeps
    daily_fast_rewards_remaining = Column(Integer, default=1) # Botão de resgatar 2h do AFK imediatamente grátis
    
    # FASE 5: Rankeada (Ladder 1v1)
    # Pontuação ELO padrão que sobe ao vencer e cai ao perder
    arena_points = Column(Integer, default=1000)
    
    # Para controlarmos os resets pontuais de servidores baseados no ciclo de 24h
    last_daily_reset = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Conexão de volta com a tabela Principal
    player = relationship("Player", back_populates="progress")

# ==========================================
# FASE 5: Arena de Honra (PvP 1v1 Rankeado)
# ==========================================

class ArenaMatch(Base):
    """
    Registro independente para partidas 1v1. 
    A Arena é focada no ganho de pontos de vaidade (Ladder), 
    não acionando as pesadas mecânicas de Guilda como 'Death Cooldown' ou 'Hero Lock'.
    """
    __tablename__ = "arena_matches"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    
    # O desafiante e o defensor
    attacker_player_id = Column(String, ForeignKey("players.id"))
    defender_player_id = Column(String, ForeignKey("players.id"))
    
    # Status ELO no momento em que a batalha começou (Para histórico verídico)
    attacker_points_before = Column(Integer)
    defender_points_before = Column(Integer)
    
    winner_player_id = Column(String, ForeignKey("players.id"), nullable=True)
    
    # Quantos pontos ELO foram movimentados nesta partida
    points_exchanged = Column(Integer, default=0) 
    
    # Serializado em string/JSONB caso SQLite/Postgres. 
    # Guarda o mesmo formato 3v3 de engine.py
    combat_log = Column(String, nullable=True) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# ==========================================
# FASE 7: Economia, Moedas e Sistema de Gacha
# ==========================================

class PlayerWallet(Base):
    """
    Guarda 100% da parte financeira/econômica do jogador.
    Isolada da tabela principal 'players' e do progresso para segurança (Anti-Exploit).
    """
    __tablename__ = "player_wallets"
    
    player_id = Column(String, ForeignKey("players.id"), primary_key=True)
    
    # Moedas
    gold = Column(Integer, default=0) # Dinheiro base (Usado para Upgrades de Level)
    crystals_premium = Column(Integer, default=0) # Moeda premium/Real money (Gacha e Skips)
    guild_coins = Column(Integer, default=0) # Farma nas guerras e usa na Loja da Guilda
    
    # Invocação
    summon_tickets = Column(Integer, default=0) # Tickets grátis ou ganhos em eventos
    
    # Sistema Anti-Frustração (Pity)
    pity_counter = Column(Integer, default=0) # Entra em cena na matemática do Roll
    
    player = relationship("Player", back_populates="wallet")
