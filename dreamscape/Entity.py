import re

class Entity:
    def __init__(self, name, meta, ac, hp, speed, attributes, senses, languages, challenge, traits, actions):
        self.name = name
        self.meta = meta
        self.ac = ac
        self.hp = hp
        self.speed = speed
        self.attributes = attributes
        self.senses = senses
        self.languages = languages
        self.challenge = challenge
        self.traits = traits
        self.actions = self.parse_actions(actions)

    def parse_actions(self, actions):
        action_list = []

        # Splitting the actions string into individual action descriptions
        action_descriptions = re.split(r'(?=<p><em><strong>)', actions)
        for action in action_descriptions:
            if action.strip():
                action_name = self.extract_action_name(action)
                atk_mod = self.extract_atk_mod(action)
                save_dc = self.extract_save_dc(action)
                damage = self.extract_damage(action)
                description = self.extract_description(action)
                action_list.append({
                    'name': action_name,
                    'atk_mod': atk_mod,
                    'save_dc': save_dc,
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
        # Extract all instances of Hit: x (damage)
        matches = re.findall(r'Hit: \d+ \(([\d+d+\- ]+)\)', action)
        return ', '.join(matches) if matches else None

    def extract_description(self, action):
        description = re.sub(r'<.*?>', '', action)  # Remove HTML tags
        description = re.sub(r'[\r\n]', '', description)  # Remove newlines
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
            if action['save_dc']:
                print(f"  Save DC: {action['save_dc']}")
            print(f"  Description: {action['description']}")
        print()

# Example usage:
if __name__ == "__main__":
    entity = Entity(
        name="Example Monster",
        meta="Medium fiend, lawful evil",
        ac="15 (Natural Armor)",
        hp="45 (7d8 + 14)",
        speed="30 ft.",
        attributes={"STR": "17", "DEX": "12", "CON": "14", "INT": "6", "WIS": "13", "CHA": "6"},
        senses="Darkvision 60 ft., Passive Perception 10",
        languages="Infernal",
        challenge="3 (700 XP)",
        traits="<p><em><strong>Keen Hearing and Smell.</strong></em> The hound has advantage on Wisdom (Perception) checks that rely on hearing or smell.</p>",
        actions="<p><em><strong>Bite.</strong></em> <em>Melee Weapon Attack:</em> +5 to hit, reach 5 ft., one target. <em>Hit:</em> 7 (1d8 + 3) piercing damage.</p>"
    )
    entity.display()
