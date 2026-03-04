from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Boolean
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

class Hero(Base):
    __tablename__ = "heroes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    player_id = Column(String, ForeignKey("players.id"))
    name = Column(String)
    role = Column(Enum(HeroRole))
    level = Column(Integer, default=1)
    max_hp = Column(Integer, default=100)
    current_hp = Column(Integer, default=100)
    attack = Column(Integer, default=10)
    defense = Column(Integer, default=10)
    speed = Column(Integer, default=10)
    is_in_team = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    player = relationship("Player", back_populates="heroes")

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
