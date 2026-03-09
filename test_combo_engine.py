from models import Hero, Skill, SkillType, EffectType, CombatStatusEffect
from engine import simulate_3v3_combat
import json

def run_test():
    # Atacantes
    warrior = Hero(
        id="warrior_1", name="Guerreiro Frontal", attack=50, defense=20, speed=100, team_slot=1, current_hp=1000, 
        base_launcher_chance=1.0, base_launcher_status=CombatStatusEffect.Knockdown, max_mana=100, current_mana=0
    )
    
    mage = Hero(
        id="mage_1", name="Mago Eletrocutador", attack=100, defense=10, speed=50, team_slot=4, current_hp=800, max_mana=100, current_mana=0,
        base_launcher_chance=0.0, base_launcher_status=CombatStatusEffect.NoneEffect
    )
    mage_chase = Skill(
        id="skill_mage", name="Relâmpago do Ar (Chase)", skill_type=SkillType.Passive, effect_type=EffectType.Damage,
        multiplier=1.5, chase_trigger=CombatStatusEffect.Knockdown, chase_effect=CombatStatusEffect.HighFloat, hero=mage
    )
    mage.skills = [mage_chase]

    archer = Hero(
        id="archer_1", name="Arqueiro de Elite", attack=80, defense=15, speed=80, team_slot=7, current_hp=800, max_mana=100, current_mana=0,
        base_launcher_chance=0.0, base_launcher_status=CombatStatusEffect.NoneEffect
    )
    archer_chase = Skill(
        id="skill_archer", name="Chuva de Flechas (Chase)", skill_type=SkillType.Passive, effect_type=EffectType.Damage,
        multiplier=1.2, chase_trigger=CombatStatusEffect.HighFloat, chase_effect=CombatStatusEffect.LowFloat, hero=archer
    )
    archer.skills = [archer_chase]
    
    # Defensor
    boss = Hero(
        id="boss_1", name="Ogre Defensor", attack=20, defense=0, speed=10, team_slot=2, current_hp=5000, max_mana=100, current_mana=0,
        base_launcher_chance=0.0, base_launcher_status=CombatStatusEffect.NoneEffect
    )
    
    print("Iniciando Combate Teste de Chase...")
    result = simulate_3v3_combat([warrior, mage, archer], [boss])
    
    # Pega apenas o primeiro turno para análise
    first_turn = result["log"][0]
    print(f"Status do 1º Turno: {len(first_turn['actions'])} Ações Registradas")
    
    for action in first_turn["actions"]:
        if "skill_used" in action:
            print(f"-> {action['actor_name']} usou {action['skill_used']} no {action['target_name']}! Dano: {action.get('damage', 0)}")
            if "status_applied" in action and action["status_applied"]:
                print(f"   [!] Status Aplicado -> {action['status_applied']}")

if __name__ == "__main__":
    run_test()
