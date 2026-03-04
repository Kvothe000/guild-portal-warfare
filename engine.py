import random
from typing import List
from models import Hero

class TargetSelector:
    @staticmethod
    def get_lowest_hp_target(actor: Hero, enemies: List[Hero]) -> Hero:
        alive_enemies = [e for e in enemies if e.current_hp > 0]
        if not alive_enemies:
            return None
        return min(alive_enemies, key=lambda x: x.current_hp)

class DamageCalculator:
    @staticmethod
    def calculate_basic_attack(actor: Hero, target: Hero) -> int:
        base_damage = max(1, actor.attack - (target.defense / 2.0))
        rng_multiplier = random.uniform(0.9, 1.1)
        return max(1, int(base_damage * rng_multiplier))

class CombatEngine:
    def __init__(self, attackers: List[Hero], defenders: List[Hero]):
        self.attackers = attackers
        self.defenders = defenders
        self.combat_log = []
        self.turn = 1

    def resolve_combat(self) -> dict:
        while self.turn < 100:
            alive_attackers = [a for a in self.attackers if a.current_hp > 0]
            alive_defenders = [d for d in self.defenders if d.current_hp > 0]
            
            if not alive_attackers:
                return {"winner": "defender", "log": self.combat_log}
            if not alive_defenders:
                return {"winner": "attacker", "log": self.combat_log}
                
            # Global Speed Order (True 3x3)
            alive_all = alive_attackers + alive_defenders
            alive_all.sort(key=lambda x: (x.speed, random.random()), reverse=True)
            
            turn_log = {"turn": self.turn, "actions": []}
            
            for actor in alive_all:
                if actor.current_hp <= 0:
                    continue
                    
                is_attacker = actor in self.attackers
                enemies = self.defenders if is_attacker else self.attackers
                
                # Modular Target Selection
                target = TargetSelector.get_lowest_hp_target(actor, enemies)
                if not target:
                    continue
                    
                # Modular Damage Calculation
                final_damage = DamageCalculator.calculate_basic_attack(actor, target)
                
                target.current_hp -= final_damage
                
                action_desc = {
                    "actor_id": actor.id,
                    "actor_name": actor.name,
                    "action": "Basic Attack",
                    "target_id": target.id,
                    "target_name": target.name,
                    "damage": final_damage,
                    "target_hp_remaining": max(0, target.current_hp),
                    "target_died": target.current_hp <= 0
                }
                turn_log["actions"].append(action_desc)
                
                if target.current_hp <= 0:
                    alive_remaining = [e for e in enemies if e.current_hp > 0]
                    if not alive_remaining:
                        break
                        
            self.combat_log.append(turn_log)
            self.turn += 1
            
        return {"winner": "draw", "log": self.combat_log}

def simulate_3v3_combat(attackers: List[Hero], defenders: List[Hero]) -> dict:
    engine = CombatEngine(attackers, defenders)
    return engine.resolve_combat()
