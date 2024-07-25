import json

class Character:
    def __init__(self, character_data):
        self.character_name = character_data['Character Name']
        self.level = character_data['Level']
        self.classes_levels = character_data['Classes_Levels']
        self.race = character_data['Race']
        self.background = character_data['Background']
        self.ability_scores = self.parse_ability_scores(character_data['Ability Scores'])
        self.proficiency_bonus = character_data['Proficiency Bonus']
        self.saving_throws = self.parse_saving_throws(character_data['Saving Throws'])
        self.skills = self.parse_skills(character_data['Skills'])
        self.ac = character_data['AC']
        self.initiative = character_data['Initiative']
        self.speed = character_data['Speed']
        self.hit_point_max = character_data['Hit Point Max']
        self.current_hp = character_data['Current HP']
        self.temp_hp = character_data['Temp HP']
        self.passive_perception = character_data['Passive Perception']
        self.languages = character_data['Languages']
        self.inventory = character_data['Inventory']
        self.spell_modifiers = self.parse_spell_modifiers(character_data['Spell Modifiers'])
        self.spell_slots = self.parse_spell_slots(character_data['Spell Slots'])
        self.prepared_spells_and_cantrips = self.parse_prepared_spells_and_cantrips(character_data['Prepared Spells and Cantrips'])
        self.attack_info = self.parse_attack_info(character_data['Attack Info'])

    def parse_ability_scores(self, ability_scores):
        return {
            'Strength': ability_scores['Strength'],
            'Dexterity': ability_scores['Dexterity'],
            'Constitution': ability_scores['Constitution'],
            'Intelligence': ability_scores['Intelligence'],
            'Wisdom': ability_scores['Wisdom'],
            'Charisma': ability_scores['Charisma']
        }

    def parse_saving_throws(self, saving_throws):
        return {
            'Strength': saving_throws['Strength'],
            'Dexterity': saving_throws['Dexterity'],
            'Constitution': saving_throws['Constitution'],
            'Intelligence': saving_throws['Intelligence'],
            'Wisdom': saving_throws['Wisdom'],
            'Charisma': saving_throws['Charisma']
        }

    def parse_skills(self, skills):
        return {
            'Acrobatics': skills['Acrobatics'],
            'Animal Handling': skills['Animal Handling'],
            'Arcana': skills['Arcana'],
            'Athletics': skills['Athletics'],
            'Deception': skills['Deception'],
            'History': skills['History'],
            'Insight': skills['Insight'],
            'Intimidation': skills['Intimidation'],
            'Investigation': skills['Investigation'],
            'Medicine': skills['Medicine'],
            'Nature': skills['Nature'],
            'Perception': skills['Perception'],
            'Performance': skills['Performance'],
            'Persuasion': skills['Persuasion'],
            'Religion': skills['Religion'],
            'Sleight of Hand': skills['Sleight of Hand'],
            'Stealth': skills['Stealth'],
            'Survival': skills['Survival']
        }

    def parse_spell_modifiers(self, spell_modifiers):
        return {
            'Casting Class': spell_modifiers['Casting Class'],
            'Casting Ability': spell_modifiers['Casting Ability'],
            'Save DC': spell_modifiers['Save DC'],
            'Spell Attack Modifier': spell_modifiers['Spell Attack Modifier']
        }

    def parse_spell_slots(self, spell_slots):
        return {
            'Level 1': spell_slots['Level 1'],
            'Level 2': spell_slots['Level 2'],
            'Level 3': spell_slots['Level 3'],
            'Level 4': spell_slots['Level 4'],
            'Level 5': spell_slots['Level 5'],
            'Level 6': spell_slots['Level 6'],
            'Level 7': spell_slots['Level 7'],
            'Level 8': spell_slots['Level 8'],
            'Level 9': spell_slots['Level 9']
        }

    def parse_prepared_spells_and_cantrips(self, prepared_spells_and_cantrips):
        return {
            'Cantrips': prepared_spells_and_cantrips['Cantrips'],
            'Level 1': prepared_spells_and_cantrips['Level 1'],
            'Level 2': prepared_spells_and_cantrips['Level 2'],
            'Level 3': prepared_spells_and_cantrips['Level 3'],
            'Level 4': prepared_spells_and_cantrips['Level 4'],
            'Level 5': prepared_spells_and_cantrips['Level 5'],
            'Level 6': prepared_spells_and_cantrips['Level 6'],
            'Level 7': prepared_spells_and_cantrips['Level 7'],
            'Level 8': prepared_spells_and_cantrips['Level 8'],
            'Level 9': prepared_spells_and_cantrips['Level 9']
        }

    def parse_attack_info(self, attack_info):
        return {
            'Attack 1': attack_info['Attack 1'],
            'Attack 2': attack_info['Attack 2'],
            'Attack 3': attack_info['Attack 3'],
            'Attack 4': attack_info['Attack 4'],
            'Attack 5': attack_info['Attack 5']
        }

# Load character data from the JSON file
with open('json/character_data.json') as f:
    character_data = json.load(f)

# Create a Character object
character = Character(character_data)

# Print specific attributes for verification
print(f"Attack 1 Name: {character.attack_info['Attack 1']['Name']}")
print(f"Acrobatics: {character.skills['Acrobatics']}")
print(f"Speed: {character.speed}")