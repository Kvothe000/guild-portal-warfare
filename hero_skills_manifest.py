# hero_skills_manifest.py

from enum import Enum

# Dicionários em memória que servem como a "Bíblia Numérica" do Game Design.
# Quando um herói é puxado no Gacha, o service lê este manifesto para popular
# o banco de dados (Tabelas Hero e Skill) com as Habilidades e Status corretos.

class Faction(str, Enum):
    VANGUARD = "Vanguard"
    ARCANE = "Arcane"
    SHADOW = "Shadow"

class Rarity(str, Enum):
    SSS = "SSS"
    SS = "SS"
    S = "S"
    A = "A"
    B = "B"

class StatusEffect(str, Enum):
    NONE = "NoneEffect"
    KNOCKDOWN = "Knockdown"
    HIGH_FLOAT = "HighFloat"
    LOW_FLOAT = "LowFloat"
    REPULSE = "Repulse"
    # Status de CC e DoT
    STUN = "Stun"
    SILENCE = "Silence"
    BLIND = "Blind"
    ROOT = "Root"
    BURN = "Burn"
    POISON = "Poison"
    BLEED = "Bleed"
    SHIELD = "Shield"

# Dicionário Master de 40 Heróis (Estrutura do Lançamento)
HERO_TEMPLATES = {
    # ==========================================
    # 🎭 AVATARES DO JOGADOR (Main Characters)
    # ==========================================
    "Avatar_Ignis": {
        "name": "Avatar do Fogo",
        "faction": Faction.VANGUARD, "rarity": Rarity.SS, "role": "Carry",
        "base_stats": {"hp": 1500, "attack": 160, "defense": 100, "speed": 100},
        "skills": [
            {"name": "Golpe Flamejante", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.25, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Chuva de Fogo", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage_And_DoT", "multiplier": 1.5, "launcher_chance": 1.0, "launcher": StatusEffect.HIGH_FLOAT, "apply_status": StatusEffect.BURN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Combo Calcinante", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE, "max_chases_per_turn": 1}
        ]
    },
    "Avatar_Aqua": {
        "name": "Avatar da Água",
        "faction": Faction.ARCANE, "rarity": Rarity.SS, "role": "Support",
        "base_stats": {"hp": 1800, "attack": 100, "defense": 120, "speed": 95},
        "skills": [
            {"name": "Onda Curativa", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Heal", "multiplier": 0.8, "launcher_chance": 0, "launcher": StatusEffect.NONE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Prisão D'água", "type": "Ultimate", "cost": 20, "cooldown": 3, "effect": "Damage_And_CC", "multiplier": 1.0, "launcher_chance": 1.0, "launcher": StatusEffect.KNOCKDOWN, "apply_status": StatusEffect.SILENCE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Lâmina D'água", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.LOW_FLOAT, "max_chases_per_turn": 2}
        ]
    },
    "Avatar_Terra": {
        "name": "Avatar da Terra",
        "faction": Faction.VANGUARD, "rarity": Rarity.SS, "role": "Tank",
        "base_stats": {"hp": 2200, "attack": 90, "defense": 200, "speed": 85},
        "skills": [
            {"name": "Soco Sísmico", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "launcher_chance": 0.3, "launcher": StatusEffect.KNOCKDOWN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Muralha de Rocha", "type": "Ultimate", "cost": 20, "cooldown": 4, "effect": "Heal_And_Shield", "multiplier": 1.5, "launcher_chance": 0, "launcher": StatusEffect.NONE, "apply_status": StatusEffect.SHIELD, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Esmagamento", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_And_CC", "multiplier": 1.0, "chase_trigger": StatusEffect.REPULSE, "chase_effect": StatusEffect.KNOCKDOWN, "apply_status": StatusEffect.ROOT, "max_chases_per_turn": 1}
        ]
    },
    "Avatar_Umbra": {
        "name": "Avatar das Sombras",
        "faction": Faction.SHADOW, "rarity": Rarity.SS, "role": "Carry",
        "base_stats": {"hp": 1300, "attack": 180, "defense": 90, "speed": 130},
        "skills": [
            {"name": "Ataque Furtivo", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "launcher_chance": 0.25, "launcher": StatusEffect.LOW_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Assassinato Escuro", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage_CC_Delay", "multiplier": 2.5, "launcher_chance": 1.0, "launcher": StatusEffect.REPULSE, "delay_amount": 25, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Perseguição Letal", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_Ignore_Def", "multiplier": 1.2, "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.HIGH_FLOAT, "max_chases_per_turn": 2}
        ]
    },
    "Avatar_Zephyr": {
        "name": "Avatar do Vento",
        "faction": Faction.ARCANE, "rarity": Rarity.SS, "role": "Control",
        "base_stats": {"hp": 1400, "attack": 130, "defense": 100, "speed": 150},
        "skills": [
            {"name": "Lâmina de Vento", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "launcher_chance": 0.20, "launcher": StatusEffect.HIGH_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Dança do Vento", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Action_Advance", "multiplier": 0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "advance_amount": 50, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Tornado Crescente", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.7, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.HIGH_FLOAT, "max_chases_per_turn": 3}
        ]
    },

    # ==========================================
    # 🛡️ VANGUARDA DE AÇO (13 Heróis)
    # ==========================================
    "Valkios": {
        "name": "Válkios, O Estandarte Imóvel",
        "faction": Faction.VANGUARD,
        "rarity": Rarity.SSS,
        "role": "Tank",
        "base_stats": {"hp": 1800, "attack": 80, "defense": 200, "speed": 90},
        "skills": [
            {
                "name": "Ataque com Martelo", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.35, "launcher": StatusEffect.KNOCKDOWN,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Último Suspiro do Mártir", "type": "Ultimate", "cost": 40, "cooldown": 3,
                "effect": "Taunt_And_Shield", "multiplier": 1.5, "launcher_chance": 1.0, "launcher": StatusEffect.KNOCKDOWN, # Hit frontal
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Vanguarda Esmagadora", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage_And_CC", "multiplier": 1.2, 
                "chase_trigger": StatusEffect.REPULSE, "chase_effect": StatusEffect.KNOCKDOWN,
                "apply_status": StatusEffect.STUN
            }
        ]
    },
    "Aric": {
        "name": "Aric, Marechal de Ferro",
        "faction": Faction.VANGUARD,
        "rarity": Rarity.SS,
        "role": "Carry",
        "base_stats": {"hp": 1200, "attack": 140, "defense": 120, "speed": 105},
        "skills": [
            {
                "name": "Corte de Lança", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.20, "launcher": StatusEffect.REPULSE,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Mandado de Guerra", "type": "Ultimate", "cost": 40, "cooldown": 3,
                "effect": "Damage_And_Buff", "multiplier": 1.8, "launcher_chance": 1.0, "launcher": StatusEffect.REPULSE,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Levante do Marechal", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 0.8,
                "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.HIGH_FLOAT,
                "max_chases_per_turn": 2
            }
        ]
    },
    "Balthazar": {
        "name": "Balthazar, Inquisidor de Pedra",
        "faction": Faction.VANGUARD,
        "rarity": Rarity.SS,
        "role": "Carry",
        "base_stats": {"hp": 1100, "attack": 150, "defense": 100, "speed": 100},
        "skills": [
            {
                "name": "Martelo do Inquisidor", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.20, "launcher": StatusEffect.KNOCKDOWN,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Julgamento Monolítico", "type": "Ultimate", "cost": 40, "cooldown": 4,
                "effect": "Damage_And_CC", "multiplier": 2.2, "launcher_chance": 1.0, "launcher": StatusEffect.KNOCKDOWN,
                "apply_status": StatusEffect.SILENCE,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Correntes ao Solo", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage_Ignore_Def", "multiplier": 1.1,
                "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.KNOCKDOWN,
                "max_chases_per_turn": 2
            }
        ]
    },
    "ClerigoRuinas": {
        "name": "Clérigo das Ruínas",
        "faction": Faction.VANGUARD,
        "rarity": Rarity.A,
        "role": "Support",
        "base_stats": {"hp": 1000, "attack": 70, "defense": 110, "speed": 95},
        "skills": [
            {
                "name": "Oração Pesada", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Heal", "multiplier": 0.6, "launcher_chance": 0, "launcher": StatusEffect.NONE,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Bênção da Pedra Fria", "type": "Ultimate", "cost": 30, "cooldown": 3,
                "effect": "Heal_And_Shield", "multiplier": 1.2, "apply_status": StatusEffect.SHIELD,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Golpe de Punição", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 0.6,
                "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE,
                "max_chases_per_turn": 1
            }
        ]
    },
    
    "Tiberius": {
        "name": "Tiberius, O Escudo-de-Bronze",
        "faction": Faction.VANGUARD, "rarity": Rarity.S, "role": "Tank",
        "base_stats": {"hp": 1500, "attack": 85, "defense": 160, "speed": 85},
        "skills": [
            {"name": "Golpe de Escudo", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "launcher_chance": 0.3, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Barreira Falange", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Heal_And_Shield", "multiplier": 1.5, "launcher_chance": 0, "launcher": StatusEffect.NONE, "apply_status": StatusEffect.SHIELD, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Trincheira", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_And_CC", "multiplier": 0.7, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.KNOCKDOWN, "apply_status": StatusEffect.STUN, "max_chases_per_turn": 1}
        ]
    },
    "Rurik": {
        "name": "Rurik, Quebra-Fosso",
        "faction": Faction.VANGUARD, "rarity": Rarity.S, "role": "Carry",
        "base_stats": {"hp": 1100, "attack": 135, "defense": 110, "speed": 95},
        "skills": [
            {"name": "Machado de Cerco", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.2, "launcher_chance": 0.2, "launcher": StatusEffect.KNOCKDOWN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Fenda Tectônica", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "AoE_Damage_Multihit", "multiplier": 1.4, "launcher_chance": 0, "launcher": StatusEffect.NONE, "hit_count": 5, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Pisão Brutal", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.3, "chase_trigger": StatusEffect.REPULSE, "chase_effect": StatusEffect.HIGH_FLOAT, "max_chases_per_turn": 1}
        ]
    },
    "Galiena": {
        "name": "Galiena, Guardiã da Pólvora",
        "faction": Faction.VANGUARD, "rarity": Rarity.A, "role": "Carry",
        "base_stats": {"hp": 900, "attack": 140, "defense": 85, "speed": 105},
        "skills": [
            {"name": "Tiro Cego", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.25, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Chuva de Morteiros", "type": "Ultimate", "cost": 60, "cooldown": 5, "effect": "AoE_Damage_HitCombo", "multiplier": 2.0, "launcher_chance": 1.0, "launcher": StatusEffect.HIGH_FLOAT, "hit_count": 8, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Bala Estilhaçante", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_And_DoT", "multiplier": 0.9, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.LOW_FLOAT, "apply_status": StatusEffect.BURN, "max_chases_per_turn": 1}
        ]
    },
    "Vane": {
        "name": "Vane, Capitão da Fileira",
        "faction": Faction.VANGUARD, "rarity": Rarity.SS, "role": "Support",
        "base_stats": {"hp": 1300, "attack": 110, "defense": 130, "speed": 115},
        "skills": [
            {"name": "Comando de Avanço", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "launcher_chance": 0.2, "launcher": StatusEffect.LOW_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Marcha Implacável", "type": "Ultimate", "cost": 20, "cooldown": 3, "effect": "Action_Advance", "multiplier": 0.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "advance_amount": 75, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Tática de Cerco", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.REPULSE, "max_chases_per_turn": 2}
        ]
    },
    "Corvin": {
        "name": "Corvin, Alabardeiro Cego",
        "faction": Faction.VANGUARD, "rarity": Rarity.A, "role": "Carry",
        "base_stats": {"hp": 950, "attack": 145, "defense": 90, "speed": 110},
        "skills": [
            {"name": "Estocada Guia", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "launcher_chance": 0.25, "launcher": StatusEffect.LOW_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Dança das Lâminas", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage", "multiplier": 2.0, "launcher_chance": 1.0, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Corte Sentido", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_Ignore_Def", "multiplier": 1.2, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.KNOCKDOWN, "max_chases_per_turn": 1}
        ]
    },
    "Sigrid": {
        "name": "Sigrid, Dama das Correntes",
        "faction": Faction.VANGUARD, "rarity": Rarity.S, "role": "Control",
        "base_stats": {"hp": 1150, "attack": 115, "defense": 105, "speed": 125},
        "skills": [
            {"name": "Açoite", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.3, "launcher": StatusEffect.KNOCKDOWN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Prisão de Ferro", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Damage_And_CC", "multiplier": 1.2, "launcher_chance": 1.0, "launcher": StatusEffect.LOW_FLOAT, "apply_status": StatusEffect.ROOT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Puxão Violento", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_CC_Delay", "multiplier": 0.8, "chase_trigger": StatusEffect.REPULSE, "chase_effect": StatusEffect.KNOCKDOWN, "delay_amount": 20, "chase_trigger": StatusEffect.NONE, "max_chases_per_turn": 2} # delay the target
        ]
    },
    "Thorne": {
        "name": "Thorne, Aríete Humano",
        "faction": Faction.VANGUARD, "rarity": Rarity.B, "role": "Tank",
        "base_stats": {"hp": 1400, "attack": 75, "defense": 140, "speed": 80},
        "skills": [
            {"name": "Ombrada", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "launcher_chance": 0.15, "launcher": StatusEffect.KNOCKDOWN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Grito de Provocação", "type": "Ultimate", "cost": 20, "cooldown": 3, "effect": "Taunt", "multiplier": 0.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Esmagar Crânios", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE, "max_chases_per_turn": 1}
        ]
    },
    "Oren": {
        "name": "Oren, Forjador de Batalha",
        "faction": Faction.VANGUARD, "rarity": Rarity.A, "role": "Support",
        "base_stats": {"hp": 1200, "attack": 85, "defense": 120, "speed": 100},
        "skills": [
            {"name": "Malho Quente", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage_And_DoT", "multiplier": 0.9, "launcher_chance": 0.2, "launcher": StatusEffect.HIGH_FLOAT, "apply_status": StatusEffect.BURN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Temperar Armaduras", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Heal_And_Shield", "multiplier": 1.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "apply_status": StatusEffect.SHIELD, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Golpe Dúctil", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.LOW_FLOAT, "max_chases_per_turn": 1}
        ]
    },
    "Alara": {
        "name": "Alara, Lança do Amanhecer",
        "faction": Faction.VANGUARD, "rarity": Rarity.S, "role": "Carry",
        "base_stats": {"hp": 1050, "attack": 140, "defense": 100, "speed": 120},
        "skills": [
            {"name": "Perfuração Luminosa", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "launcher_chance": 0.25, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Investida do Sol nascente", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage_And_Debuff", "multiplier": 1.8, "launcher_chance": 1.0, "launcher": StatusEffect.HIGH_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Lança Célere", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_Multihit", "multiplier": 0.6, "hit_count": 3, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE, "max_chases_per_turn": 2}
        ]
    },

    # ==========================================
    # 🌀 CÍRCULO ETEREAL (14 Heróis)
    # ==========================================
    "Seraphine": {
        "name": "Seraphine, A Erradicadora do Vazio",
        "faction": Faction.ARCANE,
        "rarity": Rarity.SSS,
        "role": "Carry",
        "base_stats": {"hp": 950, "attack": 200, "defense": 80, "speed": 110},
        "skills": [
            {
                "name": "Esfera do Vazio", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 1.1, "launcher_chance": 0.25, "launcher": StatusEffect.HIGH_FLOAT,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Ruptura Dimensional", "type": "Ultimate", "cost": 60, "cooldown": 4,
                "effect": "AoE_Damage_HitCombo", "multiplier": 1.8, "launcher_chance": 0.8, "launcher": StatusEffect.HIGH_FLOAT,
                "hit_count": 10, # Gera 10 hits instantâneos para ativar passivas de outros
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Vendaval Roto", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage_And_Debuff", "multiplier": 1.5,
                "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.HIGH_FLOAT,
                "max_chases_per_turn": 1
            }
        ]
    },
    "Aelius": {
        "name": "Aelius, Cronista Louco",
        "faction": Faction.ARCANE,
        "rarity": Rarity.SS,
        "role": "Support",
        "base_stats": {"hp": 1050, "attack": 120, "defense": 95, "speed": 130}, # Muito rápido
        "skills": [
            {
                "name": "Poeira do Tempo", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 0.8, "launcher_chance": 0.20, "launcher": StatusEffect.LOW_FLOAT,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Eco do Tempo", "type": "Ultimate", "cost": 40, "cooldown": 4,
                "effect": "Action_Advance", "multiplier": 0.0, "advance_amount": 100, # Avança aliado alvo em 100% (Turno extra)
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Explosão Rúnica", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage_And_DoT", "multiplier": 0.7,
                "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.HIGH_FLOAT,
                "apply_status": StatusEffect.BURN,
                "max_chases_per_turn": 2
            }
        ]
    },
    "Lyra": {
        "name": "Lyra, Tecelã de Fendas",
        "faction": Faction.ARCANE,
        "rarity": Rarity.SS,
        "role": "Carry",
        "base_stats": {"hp": 1000, "attack": 135, "defense": 90, "speed": 115},
        "skills": [
            {
                "name": "Lascas Arcanas", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Damage_Multihit", "multiplier": 0.4, "hit_count": 3,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Cadeia Dimensional", "type": "Ultimate", "cost": 30, "cooldown": 2,
                "effect": "Damage_And_CC", "multiplier": 1.2, "apply_status": StatusEffect.ROOT,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Fuzilamento Bruto", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage_Multihit", "multiplier": 0.25, "hit_count": 8,
                "chase_trigger": StatusEffect.ROOT, "chase_effect": StatusEffect.LOW_FLOAT,
                "max_chases_per_turn": 2
            }
        ]
    },

    "Orion": {
        "name": "Orion, Teórico do Caos",
        "faction": Faction.ARCANE, "rarity": Rarity.SS, "role": "Carry",
        "base_stats": {"hp": 900, "attack": 160, "defense": 80, "speed": 120},
        "skills": [
            {"name": "Distorção Menor", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.2, "launcher_chance": 0.3, "launcher": StatusEffect.HIGH_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Anomalia Gravitacional", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "AoE_Damage_Multihit", "multiplier": 1.6, "launcher_chance": 0.8, "launcher": StatusEffect.HIGH_FLOAT, "hit_count": 6, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Somação de Variáveis", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_Ignore_Def", "multiplier": 1.4, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE, "max_chases_per_turn": 1}
        ]
    },
    "Kaelista": {
        "name": "Kaelista, Caminhante do Astral",
        "faction": Faction.ARCANE, "rarity": Rarity.S, "role": "Support",
        "base_stats": {"hp": 1100, "attack": 100, "defense": 95, "speed": 135},
        "skills": [
            {"name": "Feixe Lunar", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "launcher_chance": 0.2, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Dança das Estrelas", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Action_Advance", "multiplier": 0.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "advance_amount": 50, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Luz Fragmentada", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Heal", "multiplier": 0.5, "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.HIGH_FLOAT, "max_chases_per_turn": 2}
        ]
    },
    "Vesper": {
        "name": "Vesper, Mestra das Marionetes",
        "faction": Faction.ARCANE, "rarity": Rarity.S, "role": "Control",
        "base_stats": {"hp": 1050, "attack": 125, "defense": 90, "speed": 115},
        "skills": [
            {"name": "Fio de Éter", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "launcher_chance": 0.25, "launcher": StatusEffect.LOW_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Manipulação Cega", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage_And_CC", "multiplier": 1.2, "launcher_chance": 1.0, "launcher": StatusEffect.REPULSE, "apply_status": StatusEffect.SILENCE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Puxão de Cordas", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.KNOCKDOWN, "max_chases_per_turn": 1}
        ]
    },
    "Zephyros": {
        "name": "Zéphyros, Tempestade Viva",
        "faction": Faction.ARCANE, "rarity": Rarity.A, "role": "Carry",
        "base_stats": {"hp": 900, "attack": 140, "defense": 85, "speed": 125},
        "skills": [
            {"name": "Corte de Brisa", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "launcher_chance": 0.2, "launcher": StatusEffect.HIGH_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Ira do Furacão", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "AoE_Damage_Multihit", "multiplier": 1.3, "launcher_chance": 0, "launcher": StatusEffect.NONE, "hit_count": 8, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Rajada Súbita", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "chase_trigger": StatusEffect.REPULSE, "chase_effect": StatusEffect.LOW_FLOAT, "max_chases_per_turn": 2}
        ]
    },
    "Nyx": {
        "name": "Nyx, Devoradora de Feitiços",
        "faction": Faction.ARCANE, "rarity": Rarity.SS, "role": "Tank",
        "base_stats": {"hp": 1600, "attack": 90, "defense": 150, "speed": 95},
        "skills": [
            {"name": "Golpe Drenante", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "launcher_chance": 0.3, "launcher": StatusEffect.KNOCKDOWN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Aura de Nulificação", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Taunt_And_Shield", "multiplier": 1.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Refração", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_And_CC", "multiplier": 0.6, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE, "apply_status": StatusEffect.SILENCE, "max_chases_per_turn": 1}
        ]
    },
    "Elarion": {
        "name": "Elarion, Arquivista Arcano",
        "faction": Faction.ARCANE, "rarity": Rarity.B, "role": "Support",
        "base_stats": {"hp": 1100, "attack": 80, "defense": 95, "speed": 105},
        "skills": [
            {"name": "Projétil Mágico", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.15, "launcher": StatusEffect.LOW_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Tratado de Cura", "type": "Ultimate", "cost": 20, "cooldown": 3, "effect": "Heal", "multiplier": 1.2, "launcher_chance": 0, "launcher": StatusEffect.NONE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Inscrição de Choque", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "chase_trigger": StatusEffect.REPULSE, "chase_effect": StatusEffect.KNOCKDOWN, "max_chases_per_turn": 1}
        ]
    },
    "Caelum": {
        "name": "Caelum, Forjador de Nuvens",
        "faction": Faction.ARCANE, "rarity": Rarity.A, "role": "Control",
        "base_stats": {"hp": 1000, "attack": 110, "defense": 100, "speed": 110},
        "skills": [
            {"name": "Esfera Condensada", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.25, "launcher": StatusEffect.HIGH_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Névoa Espessa", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Damage_And_CC", "multiplier": 1.1, "launcher_chance": 1.0, "launcher": StatusEffect.LOW_FLOAT, "apply_status": StatusEffect.BLIND, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Tufão Crescente", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.HIGH_FLOAT, "max_chases_per_turn": 2}
        ]
    },
    "Irene": {
        "name": "Irène, A Dama Partida",
        "faction": Faction.ARCANE, "rarity": Rarity.S, "role": "Carry",
        "base_stats": {"hp": 950, "attack": 145, "defense": 85, "speed": 120},
        "skills": [
            {"name": "Estilhaço de Vidro", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.2, "launcher_chance": 0.2, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Quebra-Cabeças Mental", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage_And_DoT", "multiplier": 1.8, "launcher_chance": 1.0, "launcher": StatusEffect.KNOCKDOWN, "apply_status": StatusEffect.BLEED, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Caleidoscópio", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_Multihit", "multiplier": 0.5, "hit_count": 4, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.LOW_FLOAT, "max_chases_per_turn": 1}
        ]
    },
    "Thalassa": {
        "name": "Thalassa, Maré de Sangue",
        "faction": Faction.ARCANE, "rarity": Rarity.A, "role": "Tank",
        "base_stats": {"hp": 1300, "attack": 95, "defense": 120, "speed": 90},
        "skills": [
            {"name": "Tridente Pesado", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "launcher_chance": 0.25, "launcher": StatusEffect.KNOCKDOWN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Onda Sanguínea", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage_Heal", "multiplier": 1.5, "launcher_chance": 1.0, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Ressaca", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.HIGH_FLOAT, "max_chases_per_turn": 1}
        ]
    },
    "Fenris": {
        "name": "Fenris, Escravo da Lua",
        "faction": Faction.ARCANE, "rarity": Rarity.S, "role": "Carry",
        "base_stats": {"hp": 1050, "attack": 150, "defense": 90, "speed": 130},
        "skills": [
            {"name": "Garras Arcanas", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "launcher_chance": 0.3, "launcher": StatusEffect.LOW_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Frenesi Prateado", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Damage_Multihit", "multiplier": 2.2, "launcher_chance": 1.0, "launcher": StatusEffect.HIGH_FLOAT, "hit_count": 5, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Bote Furioso", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_Ignore_Def", "multiplier": 1.3, "chase_trigger": StatusEffect.REPULSE, "chase_effect": StatusEffect.KNOCKDOWN, "max_chases_per_turn": 1}
        ]
    },
    "Aeris": {
        "name": "Aeris, Sopradora de Feitiços",
        "faction": Faction.ARCANE, "rarity": Rarity.B, "role": "Support",
        "base_stats": {"hp": 1000, "attack": 85, "defense": 90, "speed": 115},
        "skills": [
            {"name": "Brisa Cortante", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "launcher_chance": 0.15, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Ventos Curativos", "type": "Ultimate", "cost": 20, "cooldown": 4, "effect": "Heal", "multiplier": 1.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Redemoinho", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.LOW_FLOAT, "max_chases_per_turn": 1}
        ]
    },

    # ==========================================
    # 🗡️ LIGA DAS SOMBRAS (13 Heróis)
    # ==========================================
    "Kaelen": {
        "name": "Kael'en, Lâmina Nebulosa",
        "faction": Faction.SHADOW,
        "rarity": Rarity.SSS,
        "role": "Control",
        "base_stats": {"hp": 1100, "attack": 160, "defense": 100, "speed": 160}, # O mais rápido do jogo
        "skills": [
            {
                "name": "Corte Oculto", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 1.2, "launcher_chance": 0.25, "launcher": StatusEffect.LOW_FLOAT,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Corte do Fim dos Tempos", "type": "Ultimate", "cost": 40, "cooldown": 3,
                "effect": "Damage_CC_Delay", "multiplier": 2.2, "launcher_chance": 1.0, "launcher": StatusEffect.LOW_FLOAT,
                "apply_status": StatusEffect.SILENCE, "delay_amount": 30, # Atraso de 30% na fila
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Voo da Rapina", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage", "multiplier": 1.6,
                "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.LOW_FLOAT,
                "max_chases_per_turn": 1
            }
        ]
    },
    "Ravena": {
        "name": "Ravena, Sacerdotisa de Sangue",
        "faction": Faction.SHADOW,
        "rarity": Rarity.SS,
        "role": "Support",
        "base_stats": {"hp": 1300, "attack": 90, "defense": 90, "speed": 120},
        "skills": [
            {
                "name": "Dreno de Vida", "type": "Basic", "cost": 0, "cooldown": 0,
                "effect": "Damage_Heal", "multiplier": 0.8, "launcher_chance": 0.15, "launcher": StatusEffect.REPULSE,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Pacto Profano", "type": "Ultimate", "cost": 20, "cooldown": 4,
                "effect": "Sacrifice_Heal_Buff", "multiplier": 0.0, # Cobra 10% HP da caster, dá Buff de Ataque Global
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Gavinhas de Sangue", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage_And_DoT", "multiplier": 0.8,
                "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE,
                "apply_status": StatusEffect.BLEED,
                "max_chases_per_turn": 2
            }
        ]
    },
    "Sylas": {
        "name": "Sylas, Dançarino dos Túmulos",
        "faction": Faction.SHADOW,
        "rarity": Rarity.S,
        "role": "Carry",
        "base_stats": {"hp": 900, "attack": 150, "defense": 80, "speed": 140},
        "skills": [
            {
                "name": "Invocação: Vulto Físico", "type": "Active", "cost": 10, "cooldown": 2,
                "effect": "Summon_Clone", "multiplier": 0.0, "launcher_chance": 0.0, "launcher": StatusEffect.NONE,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Cem Lâminas", "type": "Ultimate", "cost": 40, "cooldown": 3,
                "effect": "AoE_Damage_Multihit", "multiplier": 1.0, "hit_count": 15,
                "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE
            },
            {
                "name": "Retaliação nas Sombras", "type": "Passive", "cost": 0, "cooldown": 0,
                "effect": "Damage_And_CC", "multiplier": 1.2,
                "chase_trigger": "COMBO_10", "chase_effect": StatusEffect.NONE, # Acionado quando o combo passa de 10
                "apply_status": StatusEffect.BLIND,
                "max_chases_per_turn": 1
            }
        ]
    },
    
    "Nyssa": {
        "name": "Nyssa, A Víbora de Ébano",
        "faction": Faction.SHADOW, "rarity": Rarity.S, "role": "Carry",
        "base_stats": {"hp": 900, "attack": 145, "defense": 85, "speed": 135},
        "skills": [
            {"name": "Presa Rápida", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage_And_DoT", "multiplier": 1.1, "launcher_chance": 0.25, "launcher": StatusEffect.LOW_FLOAT, "apply_status": StatusEffect.POISON, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Dança Venenosa", "type": "Ultimate", "cost": 20, "cooldown": 3, "effect": "AoE_Damage_Multihit", "multiplier": 1.2, "launcher_chance": 0.8, "launcher": StatusEffect.KNOCKDOWN, "hit_count": 6, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Toxina Paralisante", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_And_CC", "multiplier": 0.9, "chase_trigger": StatusEffect.REPULSE, "chase_effect": StatusEffect.HIGH_FLOAT, "apply_status": StatusEffect.ROOT, "max_chases_per_turn": 1}
        ]
    },
    "Moros": {
        "name": "Moros, Senhor do Ossuário",
        "faction": Faction.SHADOW, "rarity": Rarity.SS, "role": "Control",
        "base_stats": {"hp": 1250, "attack": 120, "defense": 105, "speed": 115},
        "skills": [
            {"name": "Toque da Cripta", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "launcher_chance": 0.2, "launcher": StatusEffect.KNOCKDOWN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Prisão de Ossos", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Damage_And_CC", "multiplier": 1.4, "launcher_chance": 1.0, "launcher": StatusEffect.LOW_FLOAT, "apply_status": StatusEffect.ROOT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Lança Femural", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_Ignore_Def", "multiplier": 1.1, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.REPULSE, "max_chases_per_turn": 2}
        ]
    },
    "Lazarus": {
        "name": "Lazarus, Costureiro de Corpos",
        "faction": Faction.SHADOW, "rarity": Rarity.S, "role": "Support",
        "base_stats": {"hp": 1300, "attack": 90, "defense": 95, "speed": 100},
        "skills": [
            {"name": "Agulha Escarlate", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage_And_DoT", "multiplier": 0.9, "launcher_chance": 0.15, "launcher": StatusEffect.REPULSE, "apply_status": StatusEffect.BLEED, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Bisturi Anímico", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Sacrifice_Heal_Buff", "multiplier": 0.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE}, # Cura pagando HP
            {"name": "Transfusão", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Heal", "multiplier": 0.5, "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.LOW_FLOAT, "max_chases_per_turn": 2}
        ]
    },
    "Varik": {
        "name": "Varik, Carrasco Nefasto",
        "faction": Faction.SHADOW, "rarity": Rarity.A, "role": "Tank",
        "base_stats": {"hp": 1500, "attack": 110, "defense": 130, "speed": 85},
        "skills": [
            {"name": "Golpe de Guilhotina", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "launcher_chance": 0.3, "launcher": StatusEffect.KNOCKDOWN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Decreto de Execução", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage", "multiplier": 2.0, "launcher_chance": 1.0, "launcher": StatusEffect.HIGH_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Arrastar Correntes", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_CC_Delay", "multiplier": 0.8, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE, "delay_amount": 15, "max_chases_per_turn": 1}
        ]
    },
    "Elara": {
        "name": "Elara, Tecelã da Peste",
        "faction": Faction.SHADOW, "rarity": Rarity.A, "role": "Support",
        "base_stats": {"hp": 1100, "attack": 85, "defense": 90, "speed": 110},
        "skills": [
            {"name": "Gás Miasmico", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage_And_DoT", "multiplier": 0.8, "launcher_chance": 0.2, "launcher": StatusEffect.LOW_FLOAT, "apply_status": StatusEffect.POISON, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Epidemia", "type": "Ultimate", "cost": 40, "cooldown": 4, "effect": "Damage_And_Debuff", "multiplier": 1.2, "launcher_chance": 0, "launcher": StatusEffect.NONE, "apply_status": StatusEffect.POISON, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Esporos Contaminados", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.KNOCKDOWN, "max_chases_per_turn": 1}
        ]
    },
    "Ryo": {
        "name": "Ryo, Lâmina Sem Mestre",
        "faction": Faction.SHADOW, "rarity": Rarity.B, "role": "Carry",
        "base_stats": {"hp": 850, "attack": 140, "defense": 80, "speed": 125},
        "skills": [
            {"name": "Corte de Sacque", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.1, "launcher_chance": 0.25, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Andarilho do Vento Negro", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage_Multihit", "multiplier": 1.5, "launcher_chance": 1.0, "launcher": StatusEffect.LOW_FLOAT, "hit_count": 4, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Desembainhar Cego", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.0, "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.HIGH_FLOAT, "max_chases_per_turn": 1}
        ]
    },
    "Malakor": {
        "name": "Malakor, Profeta do Abismo",
        "faction": Faction.SHADOW, "rarity": Rarity.SS, "role": "Carry",
        "base_stats": {"hp": 1150, "attack": 150, "defense": 100, "speed": 105},
        "skills": [
            {"name": "Sussurro do Vazio", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage_And_DoT", "multiplier": 1.0, "launcher_chance": 0.2, "launcher": StatusEffect.HIGH_FLOAT, "apply_status": StatusEffect.BURN, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Invocação: Diabrete das Sobras", "type": "Active", "cost": 40, "cooldown": 4, "effect": "Summon_Clone", "multiplier": 0.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Condenação Obscura", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.3, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE, "max_chases_per_turn": 2} # Beneficiado se os clones tomarem as pancadas
        ]
    },
    "Karnak": {
        "name": "Karnak, O Subjugado",
        "faction": Faction.SHADOW, "rarity": Rarity.A, "role": "Tank",
        "base_stats": {"hp": 1700, "attack": 80, "defense": 120, "speed": 80},
        "skills": [
            {"name": "Soco Acovardado", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.8, "launcher_chance": 0.25, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Resiliência Maldita", "type": "Ultimate", "cost": 20, "cooldown": 3, "effect": "Heal_And_Shield", "multiplier": 1.0, "launcher_chance": 0, "launcher": StatusEffect.NONE, "apply_status": StatusEffect.SHIELD, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Queda Pesada", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_And_CC", "multiplier": 0.8, "chase_trigger": StatusEffect.HIGH_FLOAT, "chase_effect": StatusEffect.KNOCKDOWN, "apply_status": StatusEffect.STUN, "max_chases_per_turn": 1}
        ]
    },
    "Zael": {
        "name": "Zael, Assassino de Reis",
        "faction": Faction.SHADOW, "rarity": Rarity.S, "role": "Carry",
        "base_stats": {"hp": 950, "attack": 160, "defense": 85, "speed": 140},
        "skills": [
            {"name": "Adaga Traiçoeira", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage_And_DoT", "multiplier": 1.1, "launcher_chance": 0.3, "launcher": StatusEffect.LOW_FLOAT, "apply_status": StatusEffect.BLEED, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Marca da Morte", "type": "Ultimate", "cost": 40, "cooldown": 3, "effect": "Damage_Ignore_Def", "multiplier": 2.2, "launcher_chance": 1.0, "launcher": StatusEffect.REPULSE, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Ocultação Sombria", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 1.2, "chase_trigger": StatusEffect.KNOCKDOWN, "chase_effect": StatusEffect.HIGH_FLOAT, "max_chases_per_turn": 1}
        ]
    },
    "Vex": {
        "name": "Vex, Fantasma da Fossa",
        "faction": Faction.SHADOW, "rarity": Rarity.B, "role": "Control",
        "base_stats": {"hp": 1050, "attack": 90, "defense": 95, "speed": 105},
        "skills": [
            {"name": "Aparecer Subito", "type": "Basic", "cost": 0, "cooldown": 0, "effect": "Damage", "multiplier": 0.9, "launcher_chance": 0.15, "launcher": StatusEffect.HIGH_FLOAT, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Assombração", "type": "Ultimate", "cost": 20, "cooldown": 3, "effect": "Damage_And_CC", "multiplier": 1.0, "launcher_chance": 1.0, "launcher": StatusEffect.KNOCKDOWN, "apply_status": StatusEffect.BLIND, "chase_trigger": StatusEffect.NONE, "chase_effect": StatusEffect.NONE},
            {"name": "Eco Macabro", "type": "Passive", "cost": 0, "cooldown": 0, "effect": "Damage_CC_Delay", "multiplier": 0.7, "chase_trigger": StatusEffect.LOW_FLOAT, "chase_effect": StatusEffect.REPULSE, "delay_amount": 10, "max_chases_per_turn": 1}
        ]
    }
}

def get_hero_template(hero_key: str):
    """Retorna o template cru do herói se existir."""
    return HERO_TEMPLATES.get(hero_key)

def list_all_heroes():
    """Retorna as chaves de todos os 40 heróis para poder popular o DB."""
    return list(HERO_TEMPLATES.keys())

