import random
from typing import List, Dict, Optional
from models import Hero, Skill, SkillType, EffectType, CombatStatusEffect, HeroFaction

class EphemeralState:
    """Rastreia Status Temporais duranta a batalha (Action Value, Cooldowns, Energia)"""
    def __init__(self, attackers: List[Hero], defenders: List[Hero]):
        self.cooldowns: Dict[str, Dict[str, int]] = {} # hero_id -> {skill_id: turns_remaining}
        self.taunting_heroes: Dict[str, int] = {} # hero_id -> turns_remaining
        
        # 1. Energia Compartilhada de Equipe (Começa com 30 para não spammar turn 1)
        self.team_energy: Dict[str, int] = {"attacker": 30, "defender": 30}
        self.spirits_used_this_turn: set = set() # O espírito só bate 1x por round
        
        # 2. Action Values (O relógio de turno)
        self.action_values: Dict[str, float] = {}
        for h in attackers + defenders:
            if h.current_hp > 0:
                self.action_values[h.id] = 10000.0 / max(1, h.speed)
                
        # Limite de Chases e Tracker de Combo Multihit
        self.chased_this_turn: set = set()
        self.current_combo_hits: int = 0 

    def tick_hero_turn(self, hero_id: str):
        if hero_id in self.cooldowns:
            for s_id in list(self.cooldowns[hero_id].keys()):
                if self.cooldowns[hero_id][s_id] > 0:
                    self.cooldowns[hero_id][s_id] -= 1
        if hero_id in self.taunting_heroes:
            if self.taunting_heroes[hero_id] > 0:
                self.taunting_heroes[hero_id] -= 1
            if self.taunting_heroes[hero_id] <= 0:
                del self.taunting_heroes[hero_id]
                
    def get_energy(self, side: str) -> int:
        return self.team_energy[side]
        
    def add_energy(self, side: str, amount: int):
        self.team_energy[side] = min(100, self.team_energy[side] + amount)

    def consume_energy(self, side: str, amount: int):
        self.team_energy[side] = max(0, self.team_energy[side] - amount)

class TargetSelector:
    @staticmethod
    def get_enemy_target(actor: Hero, enemies: List[Hero], state: EphemeralState) -> Optional[Hero]:
        alive_enemies = [e for e in enemies if e.current_hp > 0 and e.team_slot is not None]
        if not alive_enemies: return None
            
        taunters = [e for e in alive_enemies if e.id in state.taunting_heroes and state.taunting_heroes[e.id] > 0]
        if taunters: return random.choice(taunters)
            
        if actor.team_slot is None:
            return min(alive_enemies, key=lambda x: x.current_hp)

        actor_row = (actor.team_slot - 1) // 3
        enemies_in_row = [e for e in alive_enemies if (e.team_slot - 1) // 3 == actor_row]
        
        if enemies_in_row: return min(enemies_in_row, key=lambda x: x.team_slot)
        else: return min(alive_enemies, key=lambda x: x.team_slot)
            
    @staticmethod
    def get_ally_target(actor: Hero, allies: List[Hero], state: EphemeralState) -> Optional[Hero]:
        alive_allies = [a for a in allies if a.current_hp > 0]
        if not alive_allies: return None
        return min(alive_allies, key=lambda x: x.current_hp / (x.max_hp or 1))

class ActionResolver:
    @staticmethod
    def decide_skill(actor: Hero, side: str, state: EphemeralState) -> Optional[Skill]:
        if not actor.skills: return None
        
        # Validação do Silêncio (Não pode usar Magias/Ativas)
        # Assumindo que o Stun pula o turno do ActionResolver depois, aqui o Silence filtra skills
        
        ultimates = [s for s in actor.skills if s.skill_type == SkillType.Ultimate]
        for ult in ultimates:
            if state.get_energy(side) >= (ult.energy_cost or 0):
                return ult
                
        actives = [s for s in actor.skills if s.skill_type == SkillType.Active]
        for act in actives:
            if state.cooldowns.get(actor.id, {}).get(act.id, 0) <= 0:
                if state.get_energy(side) >= (act.energy_cost or 0):
                    return act
                
        basics = [s for s in actor.skills if s.skill_type == SkillType.Basic]
        if basics: return random.choice(basics)
            
        return None

class FactionMechanics:
    @staticmethod
    def is_shatter(attacker: Hero, defender: Hero) -> bool:
        """ 3. Faction Shatter Mechanics: Aço > Sombras > Arcano > Aço """
        a, d = attacker.faction, defender.faction
        if a == HeroFaction.Vanguard and d == HeroFaction.Shadow: return True
        if a == HeroFaction.Shadow and d == HeroFaction.Arcane: return True
        if a == HeroFaction.Arcane and d == HeroFaction.Vanguard: return True
        return False
        
    @staticmethod
    def get_random_chase_status() -> CombatStatusEffect:
        return random.choice([
            CombatStatusEffect.Knockdown, CombatStatusEffect.HighFloat, 
            CombatStatusEffect.LowFloat, CombatStatusEffect.Repulse
        ])

class ChaseReactor:
    @staticmethod
    def process_chases(
        initial_actor: Hero, target: Hero, status_triggered: CombatStatusEffect, 
        allies: List[Hero], enemies: List[Hero], state: EphemeralState, turn_log: dict
    ):
        current_status = status_triggered
        chase_chain_active = True
        
        while chase_chain_active and target.current_hp > 0:
            chase_chain_active = False
            possible_chasers = [a for a in allies if a.current_hp > 0]
            # Ordenar por velocidade
            possible_chasers.sort(key=lambda x: x.speed, reverse=True)
            
            for chaser in possible_chasers:
                # Quantos chases esse cara já deu no turno?
                chaser_count = len([x for x in state.chased_this_turn if x == chaser.id])
                
                # Busca skills ativáveis
                for s in chaser.skills:
                    if s.skill_type == SkillType.Passive:
                        # Checa se o trigger é o status físico OU o combo numérico
                        valid_trigger = False
                        if s.chase_trigger == current_status.value:
                            valid_trigger = True
                        elif s.chase_trigger.startswith("COMBO_"):
                            req_combo = int(s.chase_trigger.split("_")[1])
                            if state.current_combo_hits >= req_combo:
                                valid_trigger = True
                                
                        max_allowed = getattr(s, 'max_chases_per_turn', 1)
                        
                        if valid_trigger and chaser_count < max_allowed:
                            state.chased_this_turn.add(chaser.id)
                            # Chase acontece
                            final_damage = max(1, int((chaser.attack * s.multiplier) - (target.defense / 2.0)))
                            target.current_hp -= final_damage
                            state.current_combo_hits += getattr(s, 'hit_count', 1)
                            
                            turn_log["actions"].append({
                                "actor_id": chaser.id, "actor_name": chaser.name,
                                "skill_used": s.name, "effect_type": "CHASE_COMBO",
                                "triggered_by": s.chase_trigger,
                                "target_id": target.id, "target_name": target.name,
                                "damage": final_damage,
                                "target_hp_remaining": max(0, target.current_hp),
                                "target_died": target.current_hp <= 0
                            })
                            
                            # Atualiza status e reseta a busca para a cadeia continuar
                            if s.chase_effect != CombatStatusEffect.NoneEffect:
                                current_status = s.chase_effect
                                chase_chain_active = True
                                break # Break the skills loop, and let while loop restart search
                    if chase_chain_active:
                        break
                        
            # Cadeira falhou nos herois vivos, checar o Guardião Espiritual (se não usado)
            if not chase_chain_active:
                side = "attacker" if initial_actor in state.attackers else "defender"
                spirit = state.attacker_spirit if side == "attacker" else state.defender_spirit
                if spirit and side not in state.spirits_used_this_turn:
                    if spirit.chase_trigger == current_status:
                        state.spirits_used_this_turn.add(side)
                        
                        final_damage = max(1, int((initial_actor.attack * spirit.damage_multiplier) - (target.defense / 2.0)))
                        target.current_hp -= final_damage
                        
                        turn_log["actions"].append({
                            "actor_id": spirit.id, "actor_name": f"(Guardião) {spirit.name}",
                            "skill_used": "Invocação Guardiã", "effect_type": "SPIRIT_CHASE",
                            "triggered_by": spirit.chase_trigger.value,
                            "target_id": target.id, "target_name": target.name,
                            "damage": final_damage,
                            "target_hp_remaining": max(0, target.current_hp),
                            "target_died": target.current_hp <= 0
                        })
                        
                        if spirit.chase_effect != CombatStatusEffect.NoneEffect:
                            current_status = spirit.chase_effect
                            chase_chain_active = True

class CombatEngine:
    def __init__(self, attackers: List[Hero], defenders: List[Hero], 
                 attacker_spirit=None, defender_spirit=None):
        self.attackers = attackers
        self.defenders = defenders
        self.combat_log = []
        self.state = EphemeralState(attackers, defenders)
        self.state.attackers = attackers # Reference for side resolution
        self.state.attacker_spirit = attacker_spirit
        self.state.defender_spirit = defender_spirit
        self.max_ticks = 1000 # Previne loops infinitos

    def resolve_combat(self) -> dict:
        tick_count = 0
        
        while tick_count < self.max_ticks:
            alive_attackers = [a for a in self.attackers if a.current_hp > 0]
            alive_defenders = [d for d in self.defenders if d.current_hp > 0]
            
            if not alive_attackers: return {"winner": "defender", "log": self.combat_log}
            if not alive_defenders: return {"winner": "attacker", "log": self.combat_log}
                
            # 2. Time Manipulation (Avança Action Value)
            # Acha o herói com a menor distãncia (AV)
            next_actor_id = min(self.state.action_values, key=self.state.action_values.get)
            av_step = self.state.action_values[next_actor_id]
            
            # Subtrai esse step de todos
            for h_id in self.state.action_values:
                self.state.action_values[h_id] -= av_step
                
            # Pega o herói ativo
            actor = next((h for h in alive_attackers + alive_defenders if h.id == next_actor_id), None)
            
            if not actor or actor.current_hp <= 0:
                del self.state.action_values[next_actor_id]
                continue
                
            # Reseta AV do actor
            self.state.action_values[actor.id] = 10000.0 / max(1, actor.speed)
            tick_count += 1
            
            is_attacker = actor in self.attackers
            side = "attacker" if is_attacker else "defender"
            enemies = self.defenders if is_attacker else self.attackers
            allies = self.attackers if is_attacker else self.defenders
            
            turn_log = {"tick": tick_count, "actor": actor.name, "actions": []}
            self.state.chased_this_turn.clear()
            self.state.current_combo_hits = 0
            
            self.state.tick_hero_turn(actor.id)
            
            skill = ActionResolver.decide_skill(actor, side, self.state)
            
            action_desc = {
                "actor_id": actor.id, "actor_name": actor.name,
                "skill_used": skill.name if skill else "Basic Attack",
                "effect_type": skill.effect_type.value if skill else "Damage"
            }
            
            # 1. Energia Compartilhada
            if not skill or skill.skill_type == SkillType.Basic:
                self.state.add_energy(side, 10) # Básico gera 10
            elif skill.skill_type == SkillType.Ultimate or skill.skill_type == SkillType.Active:
                self.state.consume_energy(side, skill.energy_cost or 0)
                if skill.skill_type == SkillType.Active:
                    if actor.id not in self.state.cooldowns: self.state.cooldowns[actor.id] = {}
                    self.state.cooldowns[actor.id][skill.id] = skill.cooldown

            # Execução de Combate Padrão
            target = TargetSelector.get_enemy_target(actor, enemies, self.state)
            if target and (not skill or skill.effect_type != EffectType.Heal):
                # Calcular dano
                multiplier = skill.multiplier if skill else 1.0
                base_damage = max(1, (actor.attack * multiplier) - (target.defense / 2.0))
                
                # SHATTER MECHANIC
                is_shattered = False
                if skill and skill.skill_type in [SkillType.Active, SkillType.Ultimate]:
                    if FactionMechanics.is_shatter(actor, target):
                        base_damage *= 1.5 # 50% de bonus de facção
                        is_shattered = True
                        
                final_damage = max(1, int(base_damage * random.uniform(0.9, 1.1)))
                target.current_hp -= final_damage
                self.state.current_combo_hits += getattr(skill, 'hit_count', 1) if skill else 1
                
                action_desc.update({
                    "target_id": target.id, "target_name": target.name,
                    "damage": final_damage, "target_hp_remaining": max(0, target.current_hp),
                    "target_died": target.current_hp <= 0,
                    "shatter_triggered": is_shattered
                })
                
                # ACTION DELAY / ADVANCE INIMITER (Ex: Empurra o alvo)
                if skill and getattr(skill, 'delay_amount', 0) > 0 and target.current_hp > 0:
                    delay_av = (skill.delay_amount / 100.0) * (10000.0 / target.speed)
                    self.state.action_values[target.id] += delay_av
                
                status_launched = CombatStatusEffect.NoneEffect
                if is_shattered:
                    status_launched = FactionMechanics.get_random_chase_status()
                    action_desc["shatter_status"] = status_launched.value
                elif skill and skill.launcher_status != CombatStatusEffect.NoneEffect:
                    status_launched = skill.launcher_status
                elif (not skill or skill.skill_type == SkillType.Basic) and actor.base_launcher_status != CombatStatusEffect.NoneEffect:
                    if random.random() < actor.base_launcher_chance:
                        status_launched = actor.base_launcher_status
                        
                if status_launched != CombatStatusEffect.NoneEffect:
                    action_desc["status_applied"] = status_launched.value
                    turn_log["actions"].append(action_desc)
                    if target.current_hp > 0:
                        ChaseReactor.process_chases(actor, target, status_launched, allies, enemies, self.state, turn_log)
                    self.combat_log.append(turn_log)
                    continue

            # Buffs e Curas Específicos
            elif skill and skill.effect_type == EffectType.Heal:
                target = TargetSelector.get_ally_target(actor, allies, self.state)
                if target:
                    heal_amount = int(actor.attack * skill.multiplier)
                    target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                    action_desc.update({"target_id": target.id, "target_name": target.name, "healed": heal_amount})
                    
            elif skill and skill.effect_type == EffectType.Action_Advance:
                target = TargetSelector.get_ally_target(actor, allies, self.state) # Idealmente buffaria ally c/ mais Atk
                if target:
                    adv_av = (skill.advance_amount / 100.0) * (10000.0 / target.speed)
                    self.state.action_values[target.id] = max(0.0, self.state.action_values[target.id] - adv_av)
                    action_desc.update({"target_id": target.id, "target_name": target.name, "action_advanced": True})

            elif skill and skill.effect_type.value == "Summon_Clone":
                used_slots = [h.team_slot for h in allies if h.team_slot is not None]
                available_slots = [i for i in range(1, 10) if i not in used_slots]
                if available_slots:
                    # Tenta colocar clones na Linha de Frente (1, 4, 7) para comerem o Aggro inimigo
                    front_slots = [s for s in available_slots if s in [1, 4, 7]]
                    chosen_slot = front_slots[0] if front_slots else available_slots[0]
                    
                    clone = Hero(
                        id=f"clone_{actor.id}_{tick_count}",
                        name=f"Vulto ({actor.name})",
                        faction=actor.faction,
                        rarity=actor.rarity,
                        attack=actor.attack * 0.5,
                        defense=actor.defense * 0.5,
                        speed=int(max(1, actor.speed * 0.8)),
                        max_hp=int(actor.max_hp * 0.3),
                        current_hp=int(actor.max_hp * 0.3),
                        team_slot=chosen_slot
                    )
                    setattr(clone, 'is_clone', True)
                    
                    allies.append(clone)
                    self.state.action_values[clone.id] = 10000.0 / max(1, clone.speed)
                    action_desc.update({"summoned_clone": clone.name, "slot": chosen_slot})

            turn_log["actions"].append(action_desc)
            self.combat_log.append(turn_log)

        return {"winner": "draw", "log": self.combat_log}

def simulate_3v3_combat(attackers: List[Hero], defenders: List[Hero],
                        attacker_spirit=None, defender_spirit=None) -> dict:
    engine = CombatEngine(attackers, defenders, attacker_spirit, defender_spirit)
    return engine.resolve_combat()
