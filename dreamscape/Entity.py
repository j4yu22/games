# Entity.py
import re
from Event import Event


class Entity:
    def __init__(self, name, meta, ac, hp, speed, attributes, senses, languages, challenge, traits, actions):
        self.name = name
        self.meta = meta
        self.ac = self.extract_ac(ac)
        self.hp = self.roll_hp(hp)
        self.current_hp = self.hp  # Initialize current_hp with max hp
        self.speed = speed
        self.attributes = attributes
        self.senses = senses
        self.languages = languages
        self.challenge = challenge
        self.traits = traits
        self.actions = self.parse_actions(actions)


    def extract_ac(self, ac_str):
        if isinstance(ac_str, int):
            return ac_str
        match = re.search(r'\d+', ac_str)
        return int(match.group()) if match else 0

    def roll_hp(self, hp_str):
        if isinstance(hp_str, int):
            return hp_str
        match = re.search(r'(\d+)d(\d+)(\s*[+-]\s*\d+)?', hp_str)
        if match:
            num_dice = int(match.group(1))
            die_size = int(match.group(2))
            modifier = int(match.group(3).replace(' ', '')) if match.group(3) else 0
            event = Event(event_type="roll", entity=self.name)
            total_hp = event.roll(die_size, num_dice) + modifier
            return total_hp
        return 0

    def parse_actions(self, actions):
        action_list = []
        for action_name, action_details in actions.items():
            if action_details['Name'] != 'Not Found':
                atk_mod = action_details.get('Bonus')
                damage = action_details.get('Damage')
                description = action_details.get('Description', '')
                action_list.append({
                    'name': action_name,
                    'atk_mod': atk_mod,
                    'damage': damage,
                    'description': description
                })
        return action_list

    def extract_action_name(self, action):
        match = re.search(r'<em><strong>(.*?)</strong></em>', action)
        return match.group(1).strip('.') if match else 'Unknown Action'

    def extract_atk_mod(self, action):
        match = re.search(r'(\+[\d]+) to hit', action)
        return match.group(1) if match else None

    def extract_save_dc(self, action):
        match = re.search(r'DC (\d+)', action)
        return match.group(1) if match else None

    def extract_damage(self, action):
        matches = re.findall(r'Hit: \d+ \(([\d+d+\- ]+)\)', action)
        return ', '.join(matches) if matches else None

    def extract_description(self, action):
        description = re.sub(r'<.*?>', '', action)
        description = re.sub(r'[\r\n]', '', description)
        return description.strip()

    def display(self):
        print(f"Name: {self.name}")
        print(f"Armor Class: {self.ac}")
        print(f"Hit Points: {self.hp}")
        for action in self.actions:
            print(f"Action: {action['name']}")
            if action['atk_mod']:
                print(f"  Attack Modifier: {action['atk_mod']}")
            if action['damage']:
                print(f"  Damage: {action['damage']}")
            print(f"  Description: {action['description']}")
        print()