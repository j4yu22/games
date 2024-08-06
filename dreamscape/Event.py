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
        self.log = []

    def roll(self, sides, num=1):
        rolls = [random.randint(1, sides) for _ in range(num)]
        total = sum(rolls)
        if self.event_type == "initiative":
            self.log.append(f"{self.entity} rolled a {sides}-sided die: {rolls} = {total}")
        return total

    def roll_attack(self, attack_modifier, damage_dice_str, target_ac):
        attack_roll = self.roll(20)
        to_hit_roll = attack_roll + attack_modifier
        self.log.append(f"{self.entity} rolled attack: [{attack_roll}] + {attack_modifier} = {to_hit_roll}")
        if to_hit_roll >= target_ac:
            self.success = True
            self.description = f"{attack_roll} + {attack_modifier} = {to_hit_roll} (Hit)"
            self.roll_damage(damage_dice_str)
        else:
            self.success = False
            self.description = f"{attack_roll} + {attack_modifier} = {to_hit_roll} (Miss)"
        self.roll_result = attack_roll

    def roll_saving_throw(self, saving_throw_modifier, dc):
        save_roll = self.roll(20) + saving_throw_modifier
        self.log.append(f"{self.entity} rolled saving throw: [{save_roll - saving_throw_modifier}] + {saving_throw_modifier} = {save_roll} (DC: {dc})")
        if save_roll >= dc:
            self.success = True
            self.description = f"Saving Throw: {save_roll} (Success)"
        else:
            self.success = False
            self.description = f"Saving Throw: {save_roll} (Failure)"
        self.roll_result = save_roll

    def roll_ability_check(self, ability_modifier, dc):
        ability_check_roll = self.roll(20) + ability_modifier
        self.log.append(f"{self.entity} rolled ability check: [{ability_check_roll - ability_modifier}] + {ability_modifier} = {ability_check_roll} (DC: {dc})")
        if ability_check_roll >= dc:
            self.success = True
            self.description = f"Ability Check: {ability_check_roll} (Success)"
        else:
            self.success = False
            self.description = f"Ability Check: {ability_check_roll} (Failure)"
        self.roll_result = ability_check_roll

    def roll_initiative(self, dexterity_modifier):
        initiative_roll = self.roll(20) + dexterity_modifier
        self.log.append(f"{self.entity} rolled initiative: [{initiative_roll - dexterity_modifier}] + {dexterity_modifier} = {initiative_roll}")
        self.description = f"Initiative Roll: {initiative_roll}"
        self.roll_result = initiative_roll

    def roll_damage(self, damage_dice_str):
        total_damage = 0
        damage_breakdown = []
        roll_results = []

        try:
            # Extract dice notation using regex
            parts = re.findall(r'\d+d\d+|\+\d+', damage_dice_str)
            for part in parts:
                if 'd' in part:
                    num, sides = map(int, part.split('d'))
                    rolls = [self.roll(sides) for _ in range(num)]
                    roll_sum = sum(rolls)
                    total_damage += roll_sum
                    roll_results.append(f"({', '.join(map(str, rolls))})")
                    damage_breakdown.append(f"{num}d{sides}: {roll_sum}")
                else:
                    mod = int(part)
                    total_damage += mod
                    roll_results.append(f"{mod}")
                    damage_breakdown.append(f"Modifier: {mod}")
        except ValueError as e:
            # Handle parsing error by logging and optionally calling OpenAI API
            self.log.append(f"Error parsing damage dice: {e}")
            # Here you would call the OpenAI API to handle the error
            # For example:
            # response = openai.Completion.create(
            #     model="text-davinci-003",
            #     prompt="Provide a suitable response for a D&D damage roll calculation.",
            #     max_tokens=50
            # )
            # total_damage = response['choices'][0]['text'].strip()

        self.damage = total_damage
        self.description = f"{' + '.join(roll_results)} = {total_damage}"
        self.log.append(f"{self.entity} rolled damage: {' + '.join(roll_results)} = {total_damage}")
        self.roll_result = total_damage

    def perform_event(self, **kwargs):
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

    def get_log(self):
        return self.log

    def write_log_to_file(self, filename):
        with open(filename, 'a') as file:
            for log_entry in self.log:
                file.write(log_entry + '\n')
