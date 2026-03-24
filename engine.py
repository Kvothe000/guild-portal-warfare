import random
from typing import List, Dict, Optional, Set
from models import Hero, Skill, SkillType, EffectType, CombatStatusEffect, HeroFaction

# =============================================================================
# VEIL OF DOMINION — Combat Engine v2.0
# Implementa: Action Value System, Chase Combos, CC/DoT completos, Faction Shatter
# =============================================================================

class ActiveEffect:
    """Representa um efeito ativo (CC ou DoT) em um herói durante a batalha."""
    def __init__(self, effect: CombatStatusEffect, duration: int, value: float = 0.0):
        self.effect = effect
        self.duration = duration   # Turnos restantes
        self.value = value         # Valor de dano (para DoTs) ou absorção (Shield)

class EphemeralState:
    """Rastreia todo o estado volátil da batalha: AV, energia, CDs, efeitos ativos."""

    def __init__(self, attackers: List[Hero], defenders: List[Hero]):
        # Referências para resolução de "lado"
        self.attackers = attackers
        self.defenders = defenders

        # Cooldowns: hero_id → {skill_id: turnos_restantes}
        self.cooldowns: Dict[str, Dict[str, int]] = {}

        # Efeitos ativos por herói: hero_id → List[ActiveEffect]
        self.active_effects: Dict[str, List[ActiveEffect]] = {}

        # Taunt: hero_id → turns_remaining
        self.taunting_heroes: Dict[str, int] = {}

        # Energia compartilhada de time (começa com 30 para não trivializar turno 1)
        self.team_energy: Dict[str, int] = {"attacker": 30, "defender": 30}

        # Guardião Espiritual por lado
        self.attacker_spirit = None
        self.defender_spirit = None
        self.spirits_used_this_turn: Set[str] = set()

        # Action Values (relógio de turno)
        self.action_values: Dict[str, float] = {}
        for h in attackers + defenders:
            if h.current_hp > 0:
                self.action_values[h.id] = 10000.0 / max(1, h.speed)

        # Chase tracking por turno
        self.chased_this_turn: Dict[str, int] = {}  # hero_id → count de chases no turno
        self.current_combo_hits: int = 0

    # --- Energia ---
    def get_energy(self, side: str) -> int:
        return self.team_energy[side]

    def add_energy(self, side: str, amount: int):
        self.team_energy[side] = min(100, self.team_energy[side] + amount)

    def consume_energy(self, side: str, amount: int):
        self.team_energy[side] = max(0, self.team_energy[side] - amount)

    # --- Cooldowns ---
    def tick_cooldowns(self, hero_id: str):
        if hero_id in self.cooldowns:
            for s_id in list(self.cooldowns[hero_id].keys()):
                if self.cooldowns[hero_id][s_id] > 0:
                    self.cooldowns[hero_id][s_id] -= 1

    # --- Efeitos Ativos ---
    def apply_effect(self, hero_id: str, effect: CombatStatusEffect, duration: int, value: float = 0.0):
        """Aplica ou renova um efeito em um herói."""
        if hero_id not in self.active_effects:
            self.active_effects[hero_id] = []

        # Se o efeito já existe, renova a duração (não acumula, exceto DoTs)
        dot_effects = {CombatStatusEffect.Burn, CombatStatusEffect.Poison, CombatStatusEffect.Bleed}
        if effect in dot_effects:
            # DoTs podem acumular (adiciona nova instância)
            self.active_effects[hero_id].append(ActiveEffect(effect, duration, value))
        else:
            # CCs substituem instâncias existentes do mesmo tipo
            existing = [e for e in self.active_effects[hero_id] if e.effect == effect]
            if existing:
                existing[0].duration = max(existing[0].duration, duration)
            else:
                self.active_effects[hero_id].append(ActiveEffect(effect, duration, value))

    def has_effect(self, hero_id: str, effect: CombatStatusEffect) -> bool:
        effects = self.active_effects.get(hero_id, [])
        return any(e.effect == effect and e.duration > 0 for e in effects)

    def get_shield_value(self, hero_id: str) -> float:
        """Retorna o total de absorção de Shield ativo."""
        effects = self.active_effects.get(hero_id, [])
        return sum(e.value for e in effects if e.effect == CombatStatusEffect.Shield and e.duration > 0)

    def consume_shield(self, hero_id: str, damage: float) -> float:
        """Absorve dano pelo Shield. Retorna o dano remanescente."""
        effects = self.active_effects.get(hero_id, [])
        shields = [e for e in effects if e.effect == CombatStatusEffect.Shield and e.duration > 0]
        for shield in shields:
            if damage <= 0:
                break
            absorbed = min(shield.value, damage)
            shield.value -= absorbed
            damage -= absorbed
            if shield.value <= 0:
                shield.duration = 0  # Shield esgotado
        return max(0, damage)

    def tick_effects(self, hero: Hero, turn_log: dict) -> float:
        """
        Processa DoTs no início do turno do herói.
        Retorna o dano total de DoT causado.
        """
        total_dot_damage = 0.0
        effects = self.active_effects.get(hero.id, [])
        surviving = []
        for eff in effects:
            if eff.duration <= 0:
                continue
            # Aplicar DoT
            if eff.effect == CombatStatusEffect.Burn:
                dmg = max(1, int(hero.max_hp * 0.05))  # 5% HP máximo
                hero.current_hp -= dmg
                total_dot_damage += dmg
                turn_log["actions"].append({
                    "effect_type": "DOT_BURN", "actor_name": "Burn",
                    "target_name": hero.name, "damage": dmg,
                    "target_hp_remaining": max(0, hero.current_hp)
                })
            elif eff.effect == CombatStatusEffect.Poison:
                dmg = max(1, int(eff.value))
                hero.current_hp -= dmg
                total_dot_damage += dmg
                turn_log["actions"].append({
                    "effect_type": "DOT_POISON", "actor_name": "Poison",
                    "target_name": hero.name, "damage": dmg,
                    "target_hp_remaining": max(0, hero.current_hp)
                })
            elif eff.effect == CombatStatusEffect.Bleed:
                dmg = max(1, int(eff.value))
                hero.current_hp -= dmg
                total_dot_damage += dmg
                turn_log["actions"].append({
                    "effect_type": "DOT_BLEED", "actor_name": "Bleed",
                    "target_name": hero.name, "damage": dmg,
                    "target_hp_remaining": max(0, hero.current_hp)
                })
            eff.duration -= 1
            if eff.duration > 0 or eff.value > 0:  # Mantém Shield até esgotar
                surviving.append(eff)
        self.active_effects[hero.id] = surviving
        return total_dot_damage

    def tick_taunts(self, hero_id: str):
        if hero_id in self.taunting_heroes:
            self.taunting_heroes[hero_id] -= 1
            if self.taunting_heroes[hero_id] <= 0:
                del self.taunting_heroes[hero_id]


class TargetSelector:
    @staticmethod
    def get_enemy_target(actor: Hero, enemies: List[Hero], state: EphemeralState) -> Optional[Hero]:
        alive_enemies = [e for e in enemies if e.current_hp > 0 and e.team_slot is not None]
        if not alive_enemies:
            return None

        # Prioridade de Taunt
        taunters = [e for e in alive_enemies if e.id in state.taunting_heroes and state.taunting_heroes[e.id] > 0]
        if taunters:
            return random.choice(taunters)

        # Sem slot definido (clones sem posição): atacar o de menor HP
        if actor.team_slot is None:
            return min(alive_enemies, key=lambda x: x.current_hp)

        # Targeting por linha (row do grid 3x3)
        actor_row = (actor.team_slot - 1) // 3
        enemies_in_row = [e for e in alive_enemies if (e.team_slot - 1) // 3 == actor_row]

        if enemies_in_row:
            return min(enemies_in_row, key=lambda x: x.team_slot)
        return min(alive_enemies, key=lambda x: x.team_slot)

    @staticmethod
    def get_ally_target(actor: Hero, allies: List[Hero]) -> Optional[Hero]:
        """Seleciona o aliado com menor % de HP para cura."""
        alive_allies = [a for a in allies if a.current_hp > 0]
        if not alive_allies:
            return None
        return min(alive_allies, key=lambda x: x.current_hp / max(1, x.max_hp))


class ActionResolver:
    @staticmethod
    def decide_skill(actor: Hero, side: str, state: EphemeralState) -> Optional[Skill]:
        if not actor.skills:
            return None

        is_silenced = state.has_effect(actor.id, CombatStatusEffect.Silence)

        # Ultimate — prioridade máxima (bloqueada pelo Silence)
        if not is_silenced:
            ultimates = [s for s in actor.skills if s.skill_type == SkillType.Ultimate]
            for ult in ultimates:
                if state.get_energy(side) >= (ult.energy_cost or 0):
                    return ult

        # Active — segundo em prioridade (bloqueada pelo Silence)
        if not is_silenced:
            actives = [s for s in actor.skills if s.skill_type == SkillType.Active]
            for act in actives:
                if state.cooldowns.get(actor.id, {}).get(act.id, 0) <= 0:
                    if state.get_energy(side) >= (act.energy_cost or 0):
                        return act

        # Basic — sempre disponível
        basics = [s for s in actor.skills if s.skill_type == SkillType.Basic]
        if basics:
            return random.choice(basics)

        return None


class FactionMechanics:
    @staticmethod
    def is_shatter(attacker: Hero, defender: Hero) -> bool:
        """Triângulo de facção: Vanguarda > Sombras > Arcano > Vanguarda."""
        a, d = attacker.faction, defender.faction
        if a == HeroFaction.Vanguard and d == HeroFaction.Shadow:
            return True
        if a == HeroFaction.Shadow and d == HeroFaction.Arcane:
            return True
        if a == HeroFaction.Arcane and d == HeroFaction.Vanguard:
            return True
        return False

    @staticmethod
    def get_random_chase_status() -> CombatStatusEffect:
        return random.choice([
            CombatStatusEffect.Knockdown,
            CombatStatusEffect.HighFloat,
            CombatStatusEffect.LowFloat,
            CombatStatusEffect.Repulse
        ])


class EffectApplier:
    """Centraliza a aplicação de efeitos de status em um alvo após um hit."""

    # Mapeamento de CC para duração padrão (em turnos do alvo)
    CC_DURATIONS = {
        CombatStatusEffect.Stun: 1,
        CombatStatusEffect.Silence: 2,
        CombatStatusEffect.Blind: 2,
        CombatStatusEffect.Root: 2,
    }

    DOT_DURATIONS = {
        CombatStatusEffect.Burn: 2,
        CombatStatusEffect.Poison: 3,
        CombatStatusEffect.Bleed: 3,
    }

    @staticmethod
    def apply_skill_status(skill: Skill, target: Hero, attacker: Hero, state: EphemeralState, turn_log: dict):
        """Aplica o `apply_status` de uma skill no alvo."""
        if not skill:
            return
        apply_status = getattr(skill, 'apply_status', CombatStatusEffect.NoneEffect)
        if apply_status == CombatStatusEffect.NoneEffect:
            return

        if apply_status == CombatStatusEffect.Shield:
            # Shield: concede ao attacker (habilidade de suporte)
            shield_val = attacker.attack * getattr(skill, 'multiplier', 0.5)
            state.apply_effect(attacker.id, CombatStatusEffect.Shield, 3, shield_val)
            turn_log["actions"].append({
                "effect_type": "SHIELD_APPLIED", "actor_name": attacker.name,
                "shield_value": int(shield_val)
            })
            return

        # CC
        if apply_status in EffectApplier.CC_DURATIONS:
            duration = EffectApplier.CC_DURATIONS[apply_status]
            state.apply_effect(target.id, apply_status, duration)
            turn_log["actions"].append({
                "effect_type": "CC_APPLIED", "actor_name": attacker.name,
                "target_name": target.name, "status": apply_status.value, "duration": duration
            })

        # DoT
        elif apply_status in EffectApplier.DOT_DURATIONS:
            # Valor base do DoT: 15% do ataque do caster por tick
            dot_value = attacker.attack * 0.15
            duration = EffectApplier.DOT_DURATIONS[apply_status]
            state.apply_effect(target.id, apply_status, duration, dot_value)
            turn_log["actions"].append({
                "effect_type": "DOT_APPLIED", "actor_name": attacker.name,
                "target_name": target.name, "status": apply_status.value,
                "dot_per_tick": int(dot_value), "duration": duration
            })


class DamageCalculator:
    @staticmethod
    def calculate(attacker: Hero, target: Hero, multiplier: float, state: EphemeralState, ignore_def: bool = False) -> int:
        """
        Calcula dano final com variância, defesa e Blind.
        Aplica absorção de Shield antes de reduzir HP.
        """
        # Blind: 50% de chance de errar completamente
        if state.has_effect(attacker.id, CombatStatusEffect.Blind):
            if random.random() < 0.5:
                return 0  # Miss

        defense = 0 if ignore_def else target.defense / 2.0
        base = max(1, (attacker.attack * multiplier) - defense)
        # Variância de ±10%
        final = max(1, int(base * random.uniform(0.9, 1.1)))

        # Absorção de Shield
        shield_remaining = state.get_shield_value(target.id)
        if shield_remaining > 0:
            final = int(state.consume_shield(target.id, final))

        return final


class ChaseReactor:
    @staticmethod
    def process_chases(
        initial_actor: Hero,
        target: Hero,
        status_triggered: CombatStatusEffect,
        allies: List[Hero],
        enemies: List[Hero],
        state: EphemeralState,
        turn_log: dict,
        side: str
    ):
        current_status = status_triggered
        chase_chain_active = True

        while chase_chain_active and target.current_hp > 0:
            chase_chain_active = False

            # Ordenar por posição no grid (slot menor = prioridade maior, fiel ao Naruto Online)
            possible_chasers = [a for a in allies if a.current_hp > 0]
            possible_chasers.sort(key=lambda x: (x.team_slot or 99))

            for chaser in possible_chasers:
                # Herói stunado não pode chasar
                if state.has_effect(chaser.id, CombatStatusEffect.Stun):
                    continue

                chaser_count = state.chased_this_turn.get(chaser.id, 0)

                for s in chaser.skills:
                    if s.skill_type != SkillType.Passive:
                        continue

                    valid_trigger = False
                    trigger_val = s.chase_trigger

                    # Chase por status de combate
                    if trigger_val == current_status.value:
                        valid_trigger = True
                    # Chase por contagem de combo (ex: "COMBO_10")
                    elif isinstance(trigger_val, str) and trigger_val.startswith("COMBO_"):
                        req = int(trigger_val.split("_")[1])
                        if state.current_combo_hits >= req:
                            valid_trigger = True

                    max_allowed = getattr(s, 'max_chases_per_turn', 1)

                    if valid_trigger and chaser_count < max_allowed:
                        state.chased_this_turn[chaser.id] = chaser_count + 1

                        # Verificar se ignora defesa
                        ignore_def = (s.effect_type == EffectType.Damage_Ignore_Def)
                        final_damage = DamageCalculator.calculate(chaser, target, s.multiplier, state, ignore_def)

                        if final_damage > 0:
                            target.current_hp -= final_damage

                        hits = getattr(s, 'hit_count', 1)
                        state.current_combo_hits += hits

                        # Delay de Action Value pelo chase
                        delay_amount = getattr(s, 'delay_amount', 0)
                        if delay_amount > 0 and target.current_hp > 0 and target.id in state.action_values:
                            delay_av = (delay_amount / 100.0) * (10000.0 / max(1, target.speed))
                            state.action_values[target.id] += delay_av

                        turn_log["actions"].append({
                            "actor_id": chaser.id, "actor_name": chaser.name,
                            "skill_used": s.name, "effect_type": "CHASE_COMBO",
                            "triggered_by": trigger_val,
                            "target_id": target.id, "target_name": target.name,
                            "damage": final_damage,
                            "target_hp_remaining": max(0, target.current_hp),
                            "target_died": target.current_hp <= 0,
                            "combo_count": state.current_combo_hits
                        })

                        # Aplicar apply_status da skill de chase
                        if target.current_hp > 0:
                            EffectApplier.apply_skill_status(s, target, chaser, state, turn_log)

                        # Atualizar status da chain e reiniciar busca
                        if s.chase_effect != CombatStatusEffect.NoneEffect:
                            current_status = s.chase_effect
                            chase_chain_active = True
                            break

                if chase_chain_active:
                    break  # Reinicia o while para procurar próximo chaser com novo status

            # Nenhum herói pôde chasar — tentar o Guardião Espiritual
            if not chase_chain_active:
                spirit = state.attacker_spirit if side == "attacker" else state.defender_spirit
                if spirit and side not in state.spirits_used_this_turn:
                    if spirit.chase_trigger == current_status:
                        state.spirits_used_this_turn.add(side)

                        final_damage = DamageCalculator.calculate(
                            initial_actor, target, spirit.damage_multiplier, state
                        )
                        if final_damage > 0:
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
        self.state.attacker_spirit = attacker_spirit
        self.state.defender_spirit = defender_spirit
        self.max_ticks = 1000  # Previne loops infinitos

    def resolve_combat(self) -> dict:
        tick_count = 0

        while tick_count < self.max_ticks:
            alive_attackers = [a for a in self.attackers if a.current_hp > 0]
            alive_defenders = [d for d in self.defenders if d.current_hp > 0]

            if not alive_attackers:
                return {"winner": "defender", "log": self.combat_log}
            if not alive_defenders:
                return {"winner": "attacker", "log": self.combat_log}

            # --- Time Manipulation: quem tem menor AV age primeiro ---
            valid_av = {hid: av for hid, av in self.state.action_values.items()
                        if any(h.id == hid and h.current_hp > 0 for h in alive_attackers + alive_defenders)}
            if not valid_av:
                break

            next_actor_id = min(valid_av, key=valid_av.get)
            av_step = valid_av[next_actor_id]

            for h_id in self.state.action_values:
                self.state.action_values[h_id] -= av_step

            actor = next((h for h in alive_attackers + alive_defenders if h.id == next_actor_id), None)

            if not actor or actor.current_hp <= 0:
                if next_actor_id in self.state.action_values:
                    del self.state.action_values[next_actor_id]
                continue

            # Resetar AV do ator
            self.state.action_values[actor.id] = 10000.0 / max(1, actor.speed)
            tick_count += 1

            is_attacker = actor in self.attackers
            side = "attacker" if is_attacker else "defender"
            enemies = self.defenders if is_attacker else self.attackers
            allies = self.attackers if is_attacker else self.defenders

            turn_log = {"tick": tick_count, "actor": actor.name, "side": side, "actions": []}

            # Resetar rastreamento de chase por turno
            self.state.chased_this_turn.clear()
            self.state.current_combo_hits = 0

            # --- Processar DoTs no início do turno ---
            self.state.tick_effects(actor, turn_log)

            # Se o DoT matou o ator, pula o turno
            if actor.current_hp <= 0:
                self.combat_log.append(turn_log)
                continue

            # --- Verificar Stun: pula todo o turno ---
            if self.state.has_effect(actor.id, CombatStatusEffect.Stun):
                # Ticket o stun (decai duração)
                stun_effects = self.state.active_effects.get(actor.id, [])
                for e in stun_effects:
                    if e.effect == CombatStatusEffect.Stun:
                        e.duration -= 1
                turn_log["actions"].append({
                    "effect_type": "STUNNED", "actor_name": actor.name,
                    "note": "Turno pulado por Stun"
                })
                self.combat_log.append(turn_log)
                continue

            # --- Decair CDs e Taunts ---
            self.state.tick_cooldowns(actor.id)
            self.state.tick_taunts(actor.id)

            # --- Escolher habilidade ---
            skill = ActionResolver.decide_skill(actor, side, self.state)

            action_desc = {
                "actor_id": actor.id, "actor_name": actor.name,
                "skill_used": skill.name if skill else "Basic Attack",
                "effect_type": skill.effect_type.value if skill else "Damage"
            }

            # --- Geração/consumo de Energia ---
            if not skill or skill.skill_type == SkillType.Basic:
                self.state.add_energy(side, 10)
            elif skill.skill_type in (SkillType.Ultimate, SkillType.Active):
                self.state.consume_energy(side, skill.energy_cost or 0)
                if skill.skill_type == SkillType.Active:
                    if actor.id not in self.state.cooldowns:
                        self.state.cooldowns[actor.id] = {}
                    self.state.cooldowns[actor.id][skill.id] = skill.cooldown

            # ==================================================================
            # BRANCH DE EFEITO — decide o que a skill faz
            # ==================================================================
            effect = skill.effect_type if skill else None

            # --- CURA ---
            if effect == EffectType.Heal or (skill and "Heal" in skill.effect_type.value and "Shield" not in skill.effect_type.value and "Sacrifice" not in skill.effect_type.value):
                target = TargetSelector.get_ally_target(actor, allies)
                if target:
                    heal = int(actor.attack * (skill.multiplier if skill else 0.5))
                    target.current_hp = min(target.max_hp, target.current_hp + heal)
                    action_desc.update({"target_name": target.name, "healed": heal})

            # --- CURA + SHIELD ---
            elif skill and skill.effect_type == EffectType.Heal_And_Shield:
                target = TargetSelector.get_ally_target(actor, allies)
                if target:
                    heal = int(actor.attack * skill.multiplier)
                    target.current_hp = min(target.max_hp, target.current_hp + heal)
                    shield_val = actor.attack * skill.multiplier
                    self.state.apply_effect(target.id, CombatStatusEffect.Shield, 3, shield_val)
                    action_desc.update({
                        "target_name": target.name, "healed": heal,
                        "shield_applied": int(shield_val)
                    })

            # --- SACRIFICE_HEAL_BUFF: Clérigos sombrios (paga HP, cura/bufa time) ---
            elif skill and skill.effect_type == EffectType.Sacrifice_Heal_Buff:
                sacrifice = int(actor.max_hp * 0.10)
                actor.current_hp = max(1, actor.current_hp - sacrifice)
                # Cura o aliado com menor HP
                heal_target = TargetSelector.get_ally_target(actor, allies)
                if heal_target:
                    heal = int(actor.max_hp * 0.25)
                    heal_target.current_hp = min(heal_target.max_hp, heal_target.current_hp + heal)
                    action_desc.update({
                        "sacrificed_hp": sacrifice, "target_name": heal_target.name,
                        "healed": heal
                    })

            # --- ACTION ADVANCE: avança aliado na ordem de turno ---
            elif skill and skill.effect_type == EffectType.Action_Advance:
                advance_target = TargetSelector.get_ally_target(actor, allies)
                if advance_target and advance_target.id in self.state.action_values:
                    adv = (skill.advance_amount / 100.0) * (10000.0 / max(1, advance_target.speed))
                    self.state.action_values[advance_target.id] = max(0.0, self.state.action_values[advance_target.id] - adv)
                    action_desc.update({"target_name": advance_target.name, "action_advanced_pct": skill.advance_amount})

            # --- TAUNT ---
            elif skill and skill.effect_type in (EffectType.Taunt, EffectType.Taunt_And_Shield):
                self.state.taunting_heroes[actor.id] = 2  # Provoca por 2 turnos
                if skill.effect_type == EffectType.Taunt_And_Shield:
                    shield_val = actor.max_hp * 0.15
                    self.state.apply_effect(actor.id, CombatStatusEffect.Shield, 2, shield_val)
                action_desc.update({"taunt_applied": True, "shield_applied": skill.effect_type == EffectType.Taunt_And_Shield})
                # Ainda pode atacar de frente (o taunt é passivo)
                target = TargetSelector.get_enemy_target(actor, enemies, self.state)
                if target:
                    multiplier = skill.multiplier if skill else 1.0
                    final_damage = DamageCalculator.calculate(actor, target, multiplier, self.state)
                    if final_damage > 0:
                        target.current_hp -= final_damage
                    action_desc.update({
                        "target_name": target.name, "damage": final_damage,
                        "target_hp_remaining": max(0, target.current_hp), "target_died": target.current_hp <= 0
                    })

            # --- SUMMON CLONE ---
            elif skill and skill.effect_type == EffectType.Summon_Clone:
                used_slots = {h.team_slot for h in allies if h.team_slot is not None}
                available = [i for i in range(1, 10) if i not in used_slots]
                if available:
                    front = [s for s in available if s in [1, 4, 7]]
                    chosen_slot = front[0] if front else available[0]
                    clone = Hero(
                        id=f"clone_{actor.id}_{tick_count}",
                        name=f"Vulto ({actor.name})",
                        faction=actor.faction, rarity=actor.rarity,
                        attack=int(actor.attack * 0.5),
                        defense=int(actor.defense * 0.5),
                        speed=max(1, int(actor.speed * 0.8)),
                        max_hp=int(actor.max_hp * 0.3),
                        current_hp=int(actor.max_hp * 0.3),
                        team_slot=chosen_slot
                    )
                    setattr(clone, 'is_clone', True)
                    allies.append(clone)
                    self.state.action_values[clone.id] = 10000.0 / max(1, clone.speed)
                    action_desc.update({"summoned_clone": clone.name, "slot": chosen_slot})

            # --- DANO (padrão + variantes) ---
            else:
                target = TargetSelector.get_enemy_target(actor, enemies, self.state)
                if target:
                    multiplier = skill.multiplier if skill else 1.0
                    ignore_def = skill and skill.effect_type == EffectType.Damage_Ignore_Def

                    # Shatter de facção
                    is_shattered = False
                    if skill and skill.skill_type in (SkillType.Active, SkillType.Ultimate):
                        if FactionMechanics.is_shatter(actor, target):
                            multiplier *= 1.5
                            is_shattered = True

                    final_damage = DamageCalculator.calculate(actor, target, multiplier, self.state, ignore_def)

                    if final_damage > 0:
                        target.current_hp -= final_damage

                    hits = getattr(skill, 'hit_count', 1) if skill else 1
                    self.state.current_combo_hits += hits

                    action_desc.update({
                        "target_id": target.id, "target_name": target.name,
                        "damage": final_damage,
                        "target_hp_remaining": max(0, target.current_hp),
                        "target_died": target.current_hp <= 0,
                        "shatter_triggered": is_shattered,
                        "is_miss": final_damage == 0 and state_has_blind(actor, self.state)
                    })

                    # Action Delay (empurra o inimigo na ordem de turno)
                    delay_amount = getattr(skill, 'delay_amount', 0) if skill else 0
                    if delay_amount > 0 and target.current_hp > 0 and target.id in self.state.action_values:
                        delay_av = (delay_amount / 100.0) * (10000.0 / max(1, target.speed))
                        self.state.action_values[target.id] += delay_av

                    # Aplicar apply_status da skill no alvo
                    if skill and target.current_hp > 0:
                        EffectApplier.apply_skill_status(skill, target, actor, self.state, turn_log)

                    # Determinar status de launch para cadeia de chase
                    status_launched = CombatStatusEffect.NoneEffect
                    if is_shattered:
                        status_launched = FactionMechanics.get_random_chase_status()
                        action_desc["shatter_status"] = status_launched.value
                    elif skill and skill.launcher_status != CombatStatusEffect.NoneEffect:
                        if final_damage > 0:  # Só lança se acertou
                            status_launched = skill.launcher_status
                    elif (not skill or skill.skill_type == SkillType.Basic):
                        base_chance = getattr(actor, 'base_launcher_chance', 0.0)
                        base_status = getattr(actor, 'base_launcher_status', CombatStatusEffect.NoneEffect)
                        if base_status != CombatStatusEffect.NoneEffect and random.random() < base_chance:
                            status_launched = base_status

                    if status_launched != CombatStatusEffect.NoneEffect:
                        action_desc["status_applied"] = status_launched.value

                    turn_log["actions"].append(action_desc)

                    # Iniciar cadeia de chases se o alvo ainda estiver vivo
                    if status_launched != CombatStatusEffect.NoneEffect and target.current_hp > 0:
                        ChaseReactor.process_chases(
                            actor, target, status_launched,
                            allies, enemies, self.state, turn_log, side
                        )

                    self.combat_log.append(turn_log)
                    continue

            turn_log["actions"].append(action_desc)
            self.combat_log.append(turn_log)

        return {"winner": "draw", "log": self.combat_log}


def state_has_blind(actor: Hero, state: EphemeralState) -> bool:
    """Helper para verificar blind na action_desc."""
    return state.has_effect(actor.id, CombatStatusEffect.Blind)


def simulate_3v3_combat(attackers: List[Hero], defenders: List[Hero],
                        attacker_spirit=None, defender_spirit=None) -> dict:
    engine = CombatEngine(attackers, defenders, attacker_spirit, defender_spirit)
    return engine.resolve_combat()
