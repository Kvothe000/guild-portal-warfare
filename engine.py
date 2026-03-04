import random
from typing import List, Dict
from models import Hero, Skill, SkillType, EffectType

class EphemeralState:
    """Rastreia Status Temporais duranta a batalha, pois não persistimos turn-by-turn do BD"""
    def __init__(self):
        self.cooldowns: Dict[str, Dict[str, int]] = {} # hero_id -> {skill_id: turns_remaining}
        self.taunting_heroes: Dict[str, int] = {} # hero_id -> turns_remaining
        self.mana: Dict[str, int] = {} # hero_id -> current_mana

    def tick_hero_turn(self, hero_id: str):
        # Reduzir CDs
        if hero_id in self.cooldowns:
            for s_id in list(self.cooldowns[hero_id].keys()):
                if self.cooldowns[hero_id][s_id] > 0:
                    self.cooldowns[hero_id][s_id] -= 1
        # Reduzir Taunt
        if hero_id in self.taunting_heroes:
            if self.taunting_heroes[hero_id] > 0:
                self.taunting_heroes[hero_id] -= 1
            if self.taunting_heroes[hero_id] <= 0:
                del self.taunting_heroes[hero_id]
                
    def get_mana(self, hero: Hero) -> int:
        if hero.id not in self.mana:
            self.mana[hero.id] = hero.current_mana # Inicia com a mana que veio do banco
        return self.mana[hero.id]
        
    def add_mana(self, hero: Hero, amount: int):
        current = self.get_mana(hero)
        self.mana[hero.id] = min(hero.max_mana, current + amount)
        hero.current_mana = self.mana[hero.id] # Sincroniza para o Object do log

    def consume_mana(self, hero: Hero, amount: int):
        current = self.get_mana(hero)
        self.mana[hero.id] = max(0, current - amount)
        hero.current_mana = self.mana[hero.id]


class TargetSelector:
    @staticmethod
    def get_enemy_target(actor: Hero, enemies: List[Hero], state: EphemeralState) -> Hero:
        alive_enemies = [e for e in enemies if e.current_hp > 0]
        if not alive_enemies:
            return None
            
        # 1. Verifica se alguém no time inimigo tem Taunt ativo
        taunters = [e for e in alive_enemies if e.id in state.taunting_heroes and state.taunting_heroes[e.id] > 0]
        if taunters:
            return random.choice(taunters)
            
        # 2. Comportamento Padrão de Focus
        return min(alive_enemies, key=lambda x: x.current_hp)
        
    @staticmethod
    def get_ally_target(actor: Hero, allies: List[Hero], state: EphemeralState) -> Hero:
        alive_allies = [a for a in allies if a.current_hp > 0]
        if not alive_allies:
            return None
        # Healers focam sempre no aliado com menos HP 
        return min(alive_allies, key=lambda x: x.current_hp / (x.max_hp or 1))

class ActionResolver:
    @staticmethod
    def decide_skill(actor: Hero, state: EphemeralState) -> Skill:
        # Se não tiver skills, retorna um basic attack improvisado
        if not actor.skills:
            return None
            
        # Tenta usar Ultimate se tiver mana
        ultimates = [s for s in actor.skills if s.skill_type == SkillType.Ultimate]
        for ult in ultimates:
            if state.get_mana(actor) >= (ult.energy_cost or actor.max_mana):
                return ult
                
        # Tenta usar Ativas se não tiverem em CD
        actives = [s for s in actor.skills if s.skill_type == SkillType.Active]
        for act in actives:
            cds = state.cooldowns.get(actor.id, {})
            if cds.get(act.id, 0) <= 0:
                return act
                
        # Fallback para Basic Attack registrado
        basics = [s for s in actor.skills if s.skill_type == SkillType.Basic]
        if basics:
            return random.choice(basics)
            
        return None

class CombatEngine:
    def __init__(self, attackers: List[Hero], defenders: List[Hero]):
        self.attackers = attackers
        self.defenders = defenders
        self.combat_log = []
        self.turn = 1
        self.state = EphemeralState()

    def resolve_combat(self) -> dict:
        while self.turn < 100:
            alive_attackers = [a for a in self.attackers if a.current_hp > 0]
            alive_defenders = [d for d in self.defenders if d.current_hp > 0]
            
            if not alive_attackers:
                return {"winner": "defender", "log": self.combat_log}
            if not alive_defenders:
                return {"winner": "attacker", "log": self.combat_log}
                
            alive_all = alive_attackers + alive_defenders
            alive_all.sort(key=lambda x: (x.speed, random.random()), reverse=True)
            
            turn_log = {"turn": self.turn, "actions": []}
            
            for actor in alive_all:
                if actor.current_hp <= 0:
                    continue
                    
                is_attacker = actor in self.attackers
                enemies = self.defenders if is_attacker else self.attackers
                allies = self.attackers if is_attacker else self.defenders
                
                # 1. Regeneração de Mana e Updates de Cooldown
                self.state.add_mana(actor, 20) # 20 mana por turno
                self.state.tick_hero_turn(actor.id)
                
                # 2. Decidir o golpe
                skill = ActionResolver.decide_skill(actor, self.state)
                
                action_desc = {
                    "actor_id": actor.id,
                    "actor_name": actor.name,
                    "skill_used": skill.name if skill else "Basic Attack Fallback",
                    "effect_type": skill.effect_type.value if skill else "Damage"
                }
                
                # 3. Executar o Efeito
                if not skill or skill.effect_type == EffectType.Damage:
                    target = TargetSelector.get_enemy_target(actor, enemies, self.state)
                    if target:
                        multiplier = skill.multiplier if skill else 1.0
                        base_damage = max(1, (actor.attack * multiplier) - (target.defense / 2.0))
                        final_damage = max(1, int(base_damage * random.uniform(0.9, 1.1)))
                        target.current_hp -= final_damage
                        
                        action_desc.update({
                            "target_id": target.id, "target_name": target.name,
                            "damage": final_damage, "target_hp_remaining": max(0, target.current_hp),
                            "target_died": target.current_hp <= 0
                        })
                        
                elif skill.effect_type == EffectType.Heal:
                    target = TargetSelector.get_ally_target(actor, allies, self.state)
                    if target:
                        heal_amount = int(actor.attack * skill.multiplier)
                        target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                        
                        action_desc.update({
                            "target_id": target.id, "target_name": target.name,
                            "healed": heal_amount, "target_hp_remaining": target.current_hp
                        })
                        
                elif skill.effect_type == EffectType.Taunt:
                    self.state.taunting_heroes[actor.id] = 2 # Taunt dura 2 rodadas
                    action_desc.update({
                        "target_id": actor.id, "target_name": "Self",
                        "status_applied": "Taunt"
                    })
                    
                elif skill.effect_type == EffectType.Buff:
                    # MVP: Buff de Cura ou Buff Falso
                    action_desc.update({"status_applied": "Buff (Visual MVP)"})

                # 4. Debitar Custos e Inserir Cooldowns
                if skill:
                    if skill.skill_type == SkillType.Ultimate:
                        self.state.consume_mana(actor, skill.energy_cost or actor.max_mana)
                    elif skill.skill_type == SkillType.Active:
                        if actor.id not in self.state.cooldowns:
                            self.state.cooldowns[actor.id] = {}
                        self.state.cooldowns[actor.id][skill.id] = skill.cooldown

                turn_log["actions"].append(action_desc)
                
            self.combat_log.append(turn_log)
            self.turn += 1
            
        return {"winner": "draw", "log": self.combat_log}

def simulate_3v3_combat(attackers: List[Hero], defenders: List[Hero]) -> dict:
    engine = CombatEngine(attackers, defenders)
    return engine.resolve_combat()
