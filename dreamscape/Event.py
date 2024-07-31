import random
import re


class Event:
    def __init__(self, event_type, entity, target=None):
        self.event_type = event_type
        self.entity = entity
        self.target = target
        self.roll_result = None
        self.success = None
        self.damage = None
        self.description = ""

    def roll(self, sides, num=1):
        """
        Rolls a given number of dice with specified sides.

        Parameters:
        sides (int): Number of sides on the die.
        num (int): Number of dice to roll.

        Returns:
        int: The total of the rolled dice.
        """
        return sum(random.randint(1, sides) for _ in range(num))

    def roll_attack(self, attack_modifier, damage_dice_str, target_ac):
        """
        Rolls an attack and determines success based on target's AC.

        Parameters:
        attack_modifier (int): The attack modifier of the attacker.
        target_ac (int): The AC of the target.
        """
        attack_roll = self.roll(20)
        to_hit_roll = attack_roll + attack_modifier
        if to_hit_roll >= target_ac:
            self.success = True
            self.description = f"{attack_roll} + {attack_modifier} = {to_hit_roll} (Hit)"
            self.roll_damage(damage_dice_str)
        else:
            self.success = False
            self.description = f"{attack_roll} + {attack_modifier} = {to_hit_roll} (Miss)"
        self.roll_result = attack_roll


    def roll_saving_throw(self, saving_throw_modifier, dc):
        """
        Rolls a saving throw and determines success based on DC.

        Parameters:
        saving_throw_modifier (int): The saving throw modifier of the entity.
        dc (int): The difficulty class of the saving throw.
        """
        save_roll = self.roll(20) + saving_throw_modifier
        if save_roll >= dc:
            self.success = True
            self.description = f"Saving Throw: {save_roll} (Success)"
        else:
            self.success = False
            self.description = f"Saving Throw: {save_roll} (Failure)"
        self.roll_result = save_roll

    def roll_ability_check(self, ability_modifier, dc):
        """
        Rolls an ability check and determines success based on DC.

        Parameters:
        ability_modifier (int): The ability modifier of the entity.
        dc (int): The difficulty class of the ability check.
        """
        ability_check_roll = self.roll(20) + ability_modifier
        if ability_check_roll >= dc:
            self.success = True
            self.description = f"Ability Check: {ability_check_roll} (Success)"
        else:
            self.success = False
            self.description = f"Ability Check: {ability_check_roll} (Failure)"
        self.roll_result = ability_check_roll

    def roll_initiative(self, dexterity_modifier):
        """
        Rolls for initiative.

        Parameters:
        dexterity_modifier (int): The dexterity modifier of the entity.
        """
        initiative_roll = self.roll(20) + dexterity_modifier
        self.description = f"Initiative Roll: {initiative_roll}"
        self.roll_result = initiative_roll


    def roll_damage(self, damage_dice_str):
        """
        Rolls for damage based on the damage dice string provided.

        Parameters:
        damage_dice_str (str): A string representing the damage dice and modifiers.
                            Example: "2d6 + 3 + 3d4 + 1" represents 2d6 + 3 + 3d4 + 1.
        """
        total_damage = 0
        damage_breakdown = []
        roll_results = []

        # Split the string into parts and remove empty parts
        parts = re.split(r'(\d+d\d+|\d+)', damage_dice_str.replace(' ', ''))
        parts = [p for p in parts if p != '' and p != '+']

        for part in parts:
            if 'd' in part:
                num, sides = map(int, part.split('d'))
                roll = [self.roll(sides) for _ in range(num)]
                roll_sum = sum(roll)
                total_damage += roll_sum
                roll_results.append(f"({', '.join(map(str, roll))})")
                damage_breakdown.append(f"{num}d{sides}: {roll_sum}")
            else:
                mod = int(part)
                total_damage += mod
                roll_results.append(f"{mod}")
                damage_breakdown.append(f"Modifier: {mod}")

        self.damage = total_damage
        self.description = f"{' + '.join(roll_results)} = {total_damage}"
        self.roll_result = total_damage


    def perform_event(self, **kwargs):
        """
        Performs the event based on its type.

        Accepts keyword arguments for specific event types:
        - attack: attack_modifier, target_ac, damage_dice_str
        - saving_throw: saving_throw_modifier, dc
        - ability_check: ability_modifier, dc
        - initiative: dexterity_modifier
        """
        if self.event_type == "attack":
            self.roll_attack(**kwargs)
        elif self.event_type == "saving_throw":
            self.roll_saving_throw(**kwargs)
        elif self.event_type == "ability_check":
            self.roll_ability_check(**kwargs)
        elif self.event_type == "initiative":
            self.roll_initiative(**kwargs)
        elif self.event_type == "damage":
            self.roll_damage(**kwargs)

# Example usage:
entity = 'bjork'
event = Event(event_type="attack", entity=entity, target=None)
event.perform_event(attack_modifier=5, damage_dice_str='2d6 + 5', target_ac=13)