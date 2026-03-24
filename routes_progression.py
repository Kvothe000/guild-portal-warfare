"""
routes_progression.py — Breakthrough, Guardian Spirits e Equipment
Veil of Dominion — Fase 4 Backend
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid, datetime, random

from database import get_db
import models

router = APIRouter()

# =============================================================================
# HELPERS
# =============================================================================

def _uuid():
    return str(uuid.uuid4())

# BT custo em fragmentos por nível (0→1, 1→2, ..., 5→6)
BT_FRAGMENT_COST = [30, 60, 100, 150, 200, 300]

# Stats bonus por BT level (multiplicadores aditivos)
BT_STAT_BONUS = [
    {},                                   # BT0 — base
    {"hp": 0.05, "atk": 0.03},           # BT1
    {"hp": 0.10, "atk": 0.07},           # BT2
    {"hp": 0.18, "atk": 0.12, "def": 0.05},  # BT3
    {"hp": 0.25, "atk": 0.25, "def": 0.25, "spd": 0.10},  # BT4
    {"hp": 0.35, "atk": 0.35, "def": 0.35, "spd": 0.20},  # BT5
    {"hp": 0.50, "atk": 0.50, "def": 0.50, "spd": 0.35},  # BT6 (Ascensão)
]

# =============================================================================
# BREAKTHROUGH ROUTES
# =============================================================================

@router.post("/heroes/{hero_id}/breakthrough", tags=["Breakthrough"])
def breakthrough_hero(
    hero_id: str,
    player_id: str,
    db: Session = Depends(get_db),
):
    """
    Executa o Breakthrough de um herói se o jogador tem fragmentos suficientes.
    Fragmentos são consumidos da carteira. Stats são atualizados automaticamente.
    """
    hero = db.query(models.Hero).filter(models.Hero.id == hero_id, models.Hero.player_id == player_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Herói não encontrado.")

    current_bt = hero.breakthrough_level
    if current_bt >= 6:
        raise HTTPException(status_code=400, detail="Herói já alcançou a Ascensão Máxima (BT6).")

    cost = BT_FRAGMENT_COST[current_bt]

    # Check fragments (stored in PlayerProgress as json field — using hero.breakthrough_fragments)
    if hero.breakthrough_fragments < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Fragmentos insuficientes. Necessário: {cost}, disponível: {hero.breakthrough_fragments}."
        )

    # Consume fragments and apply BT
    hero.breakthrough_fragments -= cost
    hero.breakthrough_level += 1

    # Apply stat bonuses (additive over base stats)
    bonuses = BT_STAT_BONUS[hero.breakthrough_level]
    if "hp" in bonuses:
        hero.max_hp = int(hero.max_hp * (1 + bonuses["hp"]))
        hero.current_hp = hero.max_hp
    if "atk" in bonuses:
        hero.attack = int(hero.attack * (1 + bonuses["atk"]))
    if "def" in bonuses:
        hero.defense = int(hero.defense * (1 + bonuses["def"]))
    if "spd" in bonuses:
        hero.speed = int(hero.speed * (1 + bonuses["spd"]))

    db.commit()
    db.refresh(hero)

    return {
        "hero_id": hero.id,
        "name": hero.name,
        "new_bt_level": hero.breakthrough_level,
        "breakthrough_fragments": hero.breakthrough_fragments,
        "stats": {
            "max_hp": hero.max_hp,
            "attack": hero.attack,
            "defense": hero.defense,
            "speed": hero.speed,
        },
        "message": f"✨ {hero.name} avançou para BT{hero.breakthrough_level}!"
    }


@router.get("/heroes/{hero_id}/fragments", tags=["Breakthrough"])
def get_hero_fragments(hero_id: str, player_id: str, db: Session = Depends(get_db)):
    """Retorna os fragmentos atuais de um herói e o custo do próximo BT."""
    hero = db.query(models.Hero).filter(models.Hero.id == hero_id, models.Hero.player_id == player_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Herói não encontrado.")

    current_bt = hero.breakthrough_level
    next_cost = BT_FRAGMENT_COST[current_bt] if current_bt < 6 else None

    return {
        "hero_id": hero.id,
        "name": hero.name,
        "current_bt": current_bt,
        "fragments": hero.breakthrough_fragments,
        "next_bt_cost": next_cost,
        "can_breakthrough": next_cost is not None and hero.breakthrough_fragments >= next_cost,
    }


@router.post("/heroes/{hero_id}/fragments/add", tags=["Breakthrough"])
def add_fragments(hero_id: str, player_id: str, amount: int, db: Session = Depends(get_db)):
    """Adiciona fragmentos a um herói (drop de campanha, gacha, etc.)."""
    hero = db.query(models.Hero).filter(models.Hero.id == hero_id, models.Hero.player_id == player_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Herói não encontrado.")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser positiva.")

    hero.breakthrough_fragments = (hero.breakthrough_fragments or 0) + amount
    db.commit()
    return {"hero_id": hero.id, "name": hero.name, "total_fragments": hero.breakthrough_fragments}


# =============================================================================
# GUARDIAN SPIRIT ROUTES
# =============================================================================

# Tabela de possíveis Guardiões (mock pool — servidor-side para garantir fairness)
GUARDIAN_POOL = [
    {"name": "Ignis Eternus",      "element": "Fogo",     "rarity": "SSS", "weight": 1,
     "passive_name": "Chama Implacável",  "passive_description": "Ao início de cada turno, causa Burn no inimigo com menor HP.",
     "stat_bonus": {"hp": 800, "atk": 120, "def": 60, "spd": 25}},
    {"name": "Glacies Voidborn",   "element": "Gelo",     "rarity": "SSS", "weight": 1,
     "passive_name": "Névoa Glacial",     "passive_description": "Ataques críticos têm 40% de chance de aplicar Root por 1 turno.",
     "stat_bonus": {"hp": 700, "atk": 100, "def": 90, "spd": 30}},
    {"name": "Umbra Serenithas",   "element": "Sombra",   "rarity": "SS",  "weight": 4,
     "passive_name": "Véu das Sombras",   "passive_description": "Aliados com HP abaixo de 30% recebem +20% de esquiva.",
     "stat_bonus": {"hp": 500, "atk": 80, "def": 70, "spd": 40}},
    {"name": "Auris Luminary",     "element": "Luz",      "rarity": "SS",  "weight": 4,
     "passive_name": "Graça da Luz",      "passive_description": "Cura o aliado com menor HP em 5% do MaxHP no início de cada rodada.",
     "stat_bonus": {"hp": 600, "atk": 60, "def": 80, "spd": 30}},
    {"name": "Viridan Thornclad",  "element": "Natureza", "rarity": "SS",  "weight": 4,
     "passive_name": "Raízes Protetoras", "passive_description": "Ao sofrer dano fatal, uma vez por batalha, sobrevive com 1 HP.",
     "stat_bonus": {"hp": 700, "atk": 50, "def": 100, "spd": 20}},
    {"name": "Cinder Wraithling",  "element": "Fogo",     "rarity": "S",   "weight": 12,
     "passive_name": "Faísca Persistente","passive_description": "+15% de Ataque para todos os aliados da facção Vanguarda.",
     "stat_bonus": {"hp": 350, "atk": 70, "def": 40, "spd": 20}},
    {"name": "Frost Acolyte",      "element": "Gelo",     "rarity": "S",   "weight": 12,
     "passive_name": "Aura Glacial",      "passive_description": "Inimigos que atacam aliados têm SPD reduzida em 10% por 1 turno.",
     "stat_bonus": {"hp": 300, "atk": 50, "def": 60, "spd": 30}},
    {"name": "Shadow Cub",         "element": "Sombra",   "rarity": "A",   "weight": 30,
     "passive_name": "Imitação Sombria",  "passive_description": "+8% de Dano Crítico para o time.",
     "stat_bonus": {"hp": 200, "atk": 40, "def": 30, "spd": 35}},
    {"name": "Glow Sprite",        "element": "Luz",      "rarity": "A",   "weight": 30,
     "passive_name": "Brilho Tênue",      "passive_description": "Recupera 2% de mana por turno para todos os aliados.",
     "stat_bonus": {"hp": 250, "atk": 30, "def": 40, "spd": 25}},
]


def _weighted_roll():
    """Sorteia um Guardião com base nos pesos de raridade."""
    total = sum(g["weight"] for g in GUARDIAN_POOL)
    r = random.uniform(0, total)
    acc = 0
    for guardian in GUARDIAN_POOL:
        acc += guardian["weight"]
        if r <= acc:
            return guardian
    return GUARDIAN_POOL[-1]


@router.post("/guardians/summon", tags=["Guardian Spirits"])
def summon_guardian(player_id: str, db: Session = Depends(get_db)):
    """Invoca um Guardião Espiritual consumindo 1 Spirit Ticket."""
    wallet = db.query(models.PlayerWallet).filter(models.PlayerWallet.player_id == player_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Carteira não encontrada.")
    if wallet.spirit_tickets < 1:
        raise HTTPException(status_code=400, detail="Sem tickets de espírito. Participe de eventos ou compre no loja.")

    wallet.spirit_tickets -= 1

    rolled = _weighted_roll()

    guardian = models.GuardianSpirit(
        id=_uuid(),
        player_id=player_id,
        name=rolled["name"],
        element=rolled["element"],
        rarity=rolled["rarity"],
        level=1,
        passive_name=rolled["passive_name"],
        passive_description=rolled["passive_description"],
        stat_hp=rolled["stat_bonus"]["hp"],
        stat_atk=rolled["stat_bonus"]["atk"],
        stat_def=rolled["stat_bonus"]["def"],
        stat_spd=rolled["stat_bonus"]["spd"],
        is_equipped=False,
    )
    db.add(guardian)
    db.commit()
    db.refresh(guardian)

    return {
        "spirit": {
            "id": guardian.id,
            "name": guardian.name,
            "element": guardian.element,
            "rarity": guardian.rarity,
            "level": guardian.level,
            "passive_name": guardian.passive_name,
            "passive_description": guardian.passive_description,
            "stat_bonus": {"hp": guardian.stat_hp, "atk": guardian.stat_atk, "def": guardian.stat_def, "spd": guardian.stat_spd},
            "is_equipped": guardian.is_equipped,
        },
        "wallet_state": {
            "spirit_tickets": wallet.spirit_tickets,
            "crystals_premium": wallet.crystals_premium,
            "summon_tickets": wallet.summon_tickets,
            "gold": wallet.gold,
            "clan_coins": wallet.clan_coins,
            "pity_counter": wallet.pity_counter,
        },
    }


@router.get("/guardians/", tags=["Guardian Spirits"])
def get_player_guardians(player_id: str, db: Session = Depends(get_db)):
    """Lista todos os Guardiões do jogador."""
    guardians = db.query(models.GuardianSpirit).filter(models.GuardianSpirit.player_id == player_id).all()
    return [
        {
            "id": g.id, "name": g.name, "element": g.element, "rarity": g.rarity, "level": g.level,
            "passive_name": g.passive_name, "passive_description": g.passive_description,
            "stat_bonus": {"hp": g.stat_hp, "atk": g.stat_atk, "def": g.stat_def, "spd": g.stat_spd},
            "is_equipped": g.is_equipped,
        }
        for g in guardians
    ]


@router.post("/guardians/{spirit_id}/equip", tags=["Guardian Spirits"])
def equip_guardian(spirit_id: str, player_id: str, db: Session = Depends(get_db)):
    """Equipa um Guardião (desequipa o anterior automaticamente)."""
    spirit = db.query(models.GuardianSpirit).filter(
        models.GuardianSpirit.id == spirit_id,
        models.GuardianSpirit.player_id == player_id
    ).first()
    if not spirit:
        raise HTTPException(status_code=404, detail="Guardião não encontrado.")

    # Desequipar o atual
    db.query(models.GuardianSpirit).filter(
        models.GuardianSpirit.player_id == player_id,
        models.GuardianSpirit.is_equipped == True
    ).update({"is_equipped": False})

    spirit.is_equipped = True
    db.commit()
    return {"message": f"✨ {spirit.name} equipado com sucesso!", "spirit_id": spirit.id}


# =============================================================================
# EQUIPMENT ROUTES
# =============================================================================

# Pool de equipamentos como drops de campanha
EQUIP_POOL = [
    {"name": "Lâmina do Éter Fragmentado", "slot": "Weapon",    "rarity": "Lendário", "set_name": "Set do Veil",
     "stats": {"atk": 220, "crit_rate": 0.08}, "level": 1, "max_level": 15},
    {"name": "Armadura do Bastião Caído",   "slot": "Armor",     "rarity": "Lendário", "set_name": "Set do Veil",
     "stats": {"hp": 1800, "def": 150},         "level": 1, "max_level": 15},
    {"name": "Anel do Cronista",            "slot": "Accessory", "rarity": "Épico",    "set_name": "Set Arcano",
     "stats": {"spd": 45, "atk": 80},           "level": 1, "max_level": 12},
    {"name": "Relíquia do Lich",            "slot": "Relic",     "rarity": "Épico",    "set_name": "Set do Lich",
     "stats": {"hp": 900, "crit_dmg": 0.30},    "level": 1, "max_level": 12},
    {"name": "Garra das Sombras",           "slot": "Weapon",    "rarity": "Raro",     "set_name": None,
     "stats": {"atk": 140, "spd": 20},          "level": 1, "max_level": 10},
    {"name": "Manto da Lua Crescente",      "slot": "Armor",     "rarity": "Raro",     "set_name": None,
     "stats": {"hp": 700, "def": 80},           "level": 1, "max_level": 10},
]

UPGRADE_GOLD_COST = {"Lendário": 5000, "Épico": 2500, "Raro": 1000, "Comum": 200}


@router.get("/equipment/", tags=["Equipment"])
def get_player_equipment(player_id: str, db: Session = Depends(get_db)):
    """Lista todos os equipamentos do jogador."""
    equips = db.query(models.Equipment).filter(models.Equipment.player_id == player_id).all()
    return [
        {
            "id": e.id, "name": e.name, "slot": e.slot, "rarity": e.rarity,
            "level": e.level, "max_level": e.max_level,
            "stats": {k: v for k, v in {
                "atk": e.stat_atk, "def": e.stat_def, "hp": e.stat_hp,
                "spd": e.stat_spd, "crit_rate": e.stat_crit_rate, "crit_dmg": e.stat_crit_dmg
            }.items() if v},
            "set_name": e.set_name, "set_bonus": e.set_bonus, "hero_id": e.hero_id,
        }
        for e in equips
    ]


@router.post("/equipment/drop", tags=["Equipment"])
def drop_equipment(player_id: str, source: str = "campaign", db: Session = Depends(get_db)):
    """Dropa um equipamento (do drop de campanha, boss, etc.)."""
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    # Peso simples: legendário é mais raro
    weights = {"Lendário": 5, "Épico": 15, "Raro": 30, "Comum": 50}
    pool_with_weights = [(e, weights.get(e["rarity"], 10)) for e in EQUIP_POOL]
    total = sum(w for _, w in pool_with_weights)
    r = random.uniform(0, total)
    acc = 0
    chosen = EQUIP_POOL[-1]
    for equip, w in pool_with_weights:
        acc += w
        if r <= acc:
            chosen = equip
            break

    new_equip = models.Equipment(
        id=_uuid(), player_id=player_id,
        name=chosen["name"], slot=chosen["slot"], rarity=chosen["rarity"],
        level=1, max_level=chosen["max_level"],
        stat_atk=chosen["stats"].get("atk"), stat_def=chosen["stats"].get("def"),
        stat_hp=chosen["stats"].get("hp"), stat_spd=chosen["stats"].get("spd"),
        stat_crit_rate=chosen["stats"].get("crit_rate"), stat_crit_dmg=chosen["stats"].get("crit_dmg"),
        set_name=chosen.get("set_name"), set_bonus=None, hero_id=None,
    )
    db.add(new_equip)
    db.commit()
    db.refresh(new_equip)
    return {"message": f"🗡️ Drop: {new_equip.name} ({new_equip.rarity})!", "equipment_id": new_equip.id}


@router.post("/equipment/{equip_id}/upgrade", tags=["Equipment"])
def upgrade_equipment(equip_id: str, player_id: str, db: Session = Depends(get_db)):
    """Aprimora um equipamento em +1 nível, consumindo ouro."""
    equip = db.query(models.Equipment).filter(
        models.Equipment.id == equip_id, models.Equipment.player_id == player_id
    ).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado.")
    if equip.level >= equip.max_level:
        raise HTTPException(status_code=400, detail="Equipamento já está no nível máximo.")

    gold_cost = UPGRADE_GOLD_COST.get(equip.rarity, 1000) * equip.level
    wallet = db.query(models.PlayerWallet).filter(models.PlayerWallet.player_id == player_id).first()
    if not wallet or wallet.gold < gold_cost:
        raise HTTPException(status_code=400, detail=f"Ouro insuficiente. Custo: {gold_cost} 🟡.")

    wallet.gold -= gold_cost
    equip.level += 1

    # Scale stats +8% por nível
    scale = 1.08
    if equip.stat_atk: equip.stat_atk = int(equip.stat_atk * scale)
    if equip.stat_def: equip.stat_def = int(equip.stat_def * scale)
    if equip.stat_hp:  equip.stat_hp  = int(equip.stat_hp  * scale)
    if equip.stat_spd: equip.stat_spd = int(equip.stat_spd * scale)

    db.commit()
    db.refresh(equip)
    return {
        "id": equip.id, "name": equip.name, "level": equip.level,
        "gold_spent": gold_cost,
        "stats": {
            "atk": equip.stat_atk, "def": equip.stat_def,
            "hp": equip.stat_hp, "spd": equip.stat_spd,
            "crit_rate": equip.stat_crit_rate, "crit_dmg": equip.stat_crit_dmg,
        },
        "message": f"⬆️ {equip.name} aprimorado para +{equip.level}!"
    }


@router.post("/equipment/{equip_id}/equip", tags=["Equipment"])
def equip_to_hero(equip_id: str, hero_id: str, player_id: str, db: Session = Depends(get_db)):
    """Equipa um equipamento a um herói. Herói só pode ter 1 por slot."""
    equip = db.query(models.Equipment).filter(
        models.Equipment.id == equip_id, models.Equipment.player_id == player_id
    ).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado.")

    hero = db.query(models.Hero).filter(
        models.Hero.id == hero_id, models.Hero.player_id == player_id
    ).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Herói não encontrado.")

    # Desequipar do slot do mesmo tipo no herói
    db.query(models.Equipment).filter(
        models.Equipment.hero_id == hero_id,
        models.Equipment.slot == equip.slot,
    ).update({"hero_id": None})

    equip.hero_id = hero_id
    db.commit()
    return {"message": f"⚔️ {equip.name} equipado em {hero.name}!", "equip_id": equip.id, "hero_id": hero.id}


@router.delete("/equipment/{equip_id}/unequip", tags=["Equipment"])
def unequip_from_hero(equip_id: str, player_id: str, db: Session = Depends(get_db)):
    """Remove um equipamento do herói."""
    equip = db.query(models.Equipment).filter(
        models.Equipment.id == equip_id, models.Equipment.player_id == player_id
    ).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado.")
    equip.hero_id = None
    db.commit()
    return {"message": "Equipamento removido."}
