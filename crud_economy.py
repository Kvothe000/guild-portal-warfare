from sqlalchemy.orm import Session
import models
import schemas_economy
import random

# ==========================================
# CONFIGURAÇÕES DO BANNER (Drop Rates & Pity)
# ==========================================
GACHA_COST_CRYSTAL = 100
GACHA_COST_TICKET = 1

PITY_MAX_ROLLS = 60 # Cópia garantida de herói raro no 60º Roll

# Mock de Banco de Heróis possíveis para MVP (Sem encher o DB com templates lentos de editar)
AVAILABLE_HEROES = [
    # Rare (S-Tier) - 1% Drop
    {"name": "Rei dos Portais", "role": models.HeroRole.Carry, "base_attack": 50, "base_hp": 300, "rarity": "S"},
    {"name": "Anjo da Guarda", "role": models.HeroRole.Support, "base_attack": 15, "base_hp": 250, "rarity": "S"},
    {"name": "Colosso de Pedra", "role": models.HeroRole.Tank, "base_attack": 10, "base_hp": 600, "rarity": "S"},
    
    # Uncommon (A-Tier) - 19% Drop
    {"name": "Ladino Sombras", "role": models.HeroRole.Carry, "base_attack": 30, "base_hp": 150, "rarity": "A"},
    {"name": "Curandeira Elfica", "role": models.HeroRole.Support, "base_attack": 12, "base_hp": 180, "rarity": "A"},
    {"name": "Mago do Fogo", "role": models.HeroRole.Control, "base_attack": 35, "base_hp": 140, "rarity": "A"},
    
    # Common (Random Fodder) - 80% Drop
    {"name": "Soldado Raso", "role": models.HeroRole.Tank, "base_attack": 8, "base_hp": 120, "rarity": "Common"},
    {"name": "Arqueiro Novato", "role": models.HeroRole.Carry, "base_attack": 15, "base_hp": 90, "rarity": "Common"},
    {"name": "Acólito Aprendiz", "role": models.HeroRole.Support, "base_attack": 5, "base_hp": 100, "rarity": "Common"},
]

# --- CRUD CARTEIRA ---

def init_player_wallet(db: Session, player_id: str):
    """Injeta a carteira em jogadores virgens se não existir no DB"""
    existing = db.query(models.PlayerWallet).filter(models.PlayerWallet.player_id == player_id).first()
    if existing:
        return existing
    
    # Bonus de boas vindas para MVP (10 Rolls grátis)
    new_wallet = models.PlayerWallet(player_id=player_id, crystals_premium=1500, summon_tickets=2)
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet

def get_player_wallet(db: Session, player_id: str):
    wallet = db.query(models.PlayerWallet).filter(models.PlayerWallet.player_id == player_id).first()
    if not wallet:
        wallet = init_player_wallet(db, player_id)
    return wallet

# --- LÓGICA DO GACHA MATH (O Coração da Retenção Monetária) ---

def roll_gacha_logic(wallet: models.PlayerWallet) -> dict:
    """Rola o dado obedecendo o Pity System. Retorna o dict do herói escolhido."""
    wallet.pity_counter += 1
    
    is_pity_hit = wallet.pity_counter >= PITY_MAX_ROLLS
    roll = random.random() # 0.0 a 1.0
    
    # S-Tier / Pity
    if is_pity_hit or roll <= 0.01: # 1% Chance
        wallet.pity_counter = 0 # Reseta Pity
        pool = [h for h in AVAILABLE_HEROES if h["rarity"] == "S"]
        return random.choice(pool)
        
    # A-Tier
    elif roll <= 0.20: # 19% Chance (já que 0.01 foi pra S)
        pool = [h for h in AVAILABLE_HEROES if h["rarity"] == "A"]
        return random.choice(pool)
        
    # Common Fodder 
    else: # 80% Chance
        pool = [h for h in AVAILABLE_HEROES if h["rarity"] == "Common"]
        return random.choice(pool)

def execute_gacha_pull(db: Session, player_id: str, amount: int, currency: str):
    """Realiza a checagem financeira e devolve a N quantidade de heróis na Pool do jogador"""
    if amount not in [1, 10]:
        raise ValueError("Gacha pulls só suportam 1 ou 10 evocações simultâneas.")
        
    wallet = get_player_wallet(db, player_id)
    
    # 1. Anti-Exploit Financeiro
    if currency == "crystal":
        cost = GACHA_COST_CRYSTAL * amount
        if wallet.crystals_premium < cost:
            raise ValueError(f"Cristais insuficientes. Custa {cost}, você tem {wallet.crystals_premium}.")
        wallet.crystals_premium -= cost
            
    elif currency == "ticket":
        cost = GACHA_COST_TICKET * amount
        if wallet.summon_tickets < cost:
            raise ValueError(f"Tickets insuficientes. Custa {cost}, você tem {wallet.summon_tickets}.")
        wallet.summon_tickets -= cost
    else:
        raise ValueError("Moeda de pull inválida.")
        
    # 2. Rolar e criar os Heróis
    pulled_heroes = []
    for _ in range(amount):
        template = roll_gacha_logic(wallet)
        
        # O Gacha instável cria variações minúsculas (+- 5%) nos atributos lidos da tabela (IVs system falso)
        iv_mod = random.uniform(0.95, 1.05)
        
        new_hero = models.Hero(
            player_id=player_id,
            name=template["name"],
            role=template["role"],
            attack=int(template["base_attack"] * iv_mod),
            max_hp=int(template["base_hp"] * iv_mod),
            current_hp=int(template["base_hp"] * iv_mod)
        )
        db.add(new_hero)
        pulled_heroes.append(new_hero)
        
    db.commit()
    
    # Refresh em todo mundo para carregar os IDs
    for h in pulled_heroes:
        db.refresh(h)
        
    return pulled_heroes, wallet
