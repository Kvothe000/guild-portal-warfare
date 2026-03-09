from database import SessionLocal
from models import Player, PlayerWallet, GachaBanner, HeroFaction, HeroRarity, PlayerBannerState
from gacha_service import pull_from_banner
from crud_economy import init_player_wallet

def test_pity_system():
    print("Iniciando Teste do Motor de Gacha (Hard Pity 100 Tiros)...")
    db = SessionLocal()
    
    # Prepara o ambiente do Teste
    test_player = db.query(Player).filter(Player.username == "gacha_tester").first()
    if not test_player:
        test_player = Player(username="gacha_tester", email="gachatest@test.com", password_hash="hash")
        db.add(test_player)
        db.commit()
        db.refresh(test_player)
        
    wallet = init_player_wallet(db, test_player.id)
    # Enche a carteira para permitir 100 rolagens no baú premium (Custa 150 = 15.000 diamantes)
    wallet.crystals_premium = 50000 
    
    # Limpa o histórico anterior se existir
    state = db.query(PlayerBannerState).filter(PlayerBannerState.player_id == test_player.id).first()
    if state:
        state.pity_counter_sss = 0
    db.commit()
    
    # Acha o banner da Vanguarda
    banner = db.query(GachaBanner).filter(GachaBanner.faction_focus == HeroFaction.Vanguard).first()
    if not banner:
        print("Erro: Banner da Vanguarda não encontrado no BD.")
        return
        
    print(f"Testando Banner: {banner.name}")
    print(f"Buscando o Rosto do Banner (Pity SSS)...")
    
    pity_hit = False
    rolls_done = 0
    
    for i in range(1, 105):
        res = pull_from_banner(db, test_player.id, banner.id)
        hero = res["hero"]
        
        rolls_done += 1
        
        if hero.rarity == HeroRarity.SSS:
            print(f"🔥 SSS Encontrado no Tiro #{i}! Herói: {hero.name} (É Pity Forçado? {res['is_hard_pity']})")
            pity_hit = True
            break
            
        if i % 25 == 0:
            print(f"Tiro #{i} -> Veio um {hero.rarity.value} ({hero.name}). Pity Counter atual: {res['pity_counter_sss']}")
            
    if pity_hit and res['is_hard_pity']:
        print("\n✅ VERIFICAÇÃO CONCLUÍDA: O sistema bloqueou a frustração e entregou o SSS garantido no Hard Pity.")
    elif pity_hit and not res['is_hard_pity']:
        print("\n✅ VERIFICAÇÃO CONCLUÍDA: Sorte absurda! Tirou o SSS antes do Pity bater.")
    else:
        print("\n❌ FALHA NO TESTE: O Pity passou de 100 rolagens e não entregou o SSS.")
        
    db.close()

if __name__ == "__main__":
    test_pity_system()
