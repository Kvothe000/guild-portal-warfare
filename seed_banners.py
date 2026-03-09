from database import SessionLocal
from models import GachaBanner, HeroFaction

def seed_banners():
    db = SessionLocal()
    
    # Check if already seeded
    existing = db.query(GachaBanner).first()
    if existing:
        print("Banners already seeded.")
        db.close()
        return

    banners_to_create = [
        GachaBanner(
            name="Altar de Recrutamento Comum",
            description="Sacrifique Prata (Summon Tickets) para invocar heróis em massa.",
            faction_focus=None, # Dropa genéricos
            cost_amount=1,
            cost_currency="summon_tickets",
            hard_pity_count=999 # Sem pity realista aqui
        ),
        GachaBanner(
            name="Baú da Vanguarda de Aço",
            description="Use Aethérium para invocar defensores implacáveis (Drop Rate Aumentado para Válkios).",
            faction_focus=HeroFaction.Vanguard,
            cost_amount=150,
            cost_currency="premium_aetherium",
            hard_pity_count=100
        ),
        GachaBanner(
            name="Baú do Círculo Etereal",
            description="Use Aethérium para invocar magos devastadores (Drop Rate Aumentado para Seraphine).",
            faction_focus=HeroFaction.Arcane,
            cost_amount=150,
            cost_currency="premium_aetherium",
            hard_pity_count=100
        ),
        GachaBanner(
            name="Baú da Liga das Sombras",
            description="Use Aethérium para invocar assassinos letais (Drop Rate Aumentado para Kael'en).",
            faction_focus=HeroFaction.Shadow,
            cost_amount=150,
            cost_currency="premium_aetherium",
            hard_pity_count=100
        )
    ]
    
    db.add_all(banners_to_create)
    db.commit()
    print("Successfully seeded 4 foundational Gacha Banners into the database!")
    db.close()

if __name__ == "__main__":
    seed_banners()
