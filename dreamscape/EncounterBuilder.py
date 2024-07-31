import json
import random
import math
from Entity import Entity

class EncounterBuilder:
    def __init__(self, monster_file_path, character_file_path):
        self.monster_file_path = monster_file_path
        self.character_file_path = character_file_path
        self.monster_data = self.load_monster_data()
        self.cr_index = self.create_cr_index()
        self.character_data = self.load_character_data()

    def load_monster_data(self):
        with open(self.monster_file_path, 'r') as file:
            return json.load(file)

    def create_cr_index(self):
        cr_index = {}
        for monster in self.monster_data:
            cr = self.parse_cr(monster['Challenge'])
            if cr not in cr_index:
                cr_index[cr] = []
            cr_index[cr].append(monster)
        return cr_index

    def parse_cr(self, cr_str):
        if '(' in cr_str:
            cr_str = cr_str.split('(')[0].strip()
        if '/' in cr_str:
            numerator, denominator = map(int, cr_str.split('/'))
            return numerator / denominator
        return float(cr_str)

    def load_character_data(self):
        with open(self.character_file_path, 'r') as file:
            return json.load(file)

    def get_player_level(self):
        return int(self.character_data['Level'])  # Assuming the level is directly available

    def get_target_cr(self, player_cr, difficulty):
        difficulty_modifiers = {
            'easy': 0.5,
            'medium': 0.7,
            'hard': 1.0,
            'deadly': 1.5
        }
        if difficulty not in difficulty_modifiers:
            raise ValueError("Invalid difficulty level. Choose from 'easy', 'medium', 'hard', 'deadly'.")
        return player_cr * difficulty_modifiers[difficulty]

    def select_monsters_for_encounter(self, target_cr):
        encounter = []
        remaining_cr = target_cr

        while remaining_cr > 1:
            possible_monsters = [m for cr, monsters in self.cr_index.items() if cr <= remaining_cr for m in monsters]
            if not possible_monsters:
                break
            monster = random.choice(possible_monsters)
            encounter.append(monster)
            remaining_cr -= self.parse_cr(monster['Challenge'])

        # if empty due to low target CR, fill one monster
        if not encounter:
            possible_monsters = [m for cr, monsters in self.cr_index.items() if cr <= remaining_cr for m in monsters]
            monster = random.choice(possible_monsters)
            encounter.append(monster)

        return encounter

    def generate_encounter(self, difficulty):
        player_level = self.get_player_level()
        player_cr = math.ceil(player_level / 2)
        target_cr = self.get_target_cr(player_cr, difficulty)
        return self.select_monsters_for_encounter(target_cr)

    def display_encounter(self, encounter):
        entities = []
        for monster in encounter:
            entity = Entity(
                name=monster['name'],
                meta=monster['meta'],
                ac=monster['Armor Class'],
                hp=monster['Hit Points'],
                speed=monster['Speed'],
                attributes={
                    'STR': monster['STR'],
                    'DEX': monster['DEX'],
                    'CON': monster['CON'],
                    'INT': monster['INT'],
                    'WIS': monster['WIS'],
                    'CHA': monster['CHA']
                },
                senses=monster.get('Senses', ''),
                languages=monster.get('Languages', ''),
                challenge=monster['Challenge'],
                traits=monster.get('Traits', ''),
                actions=monster.get('Actions', '')
            )
            entities.append(entity)
            entity.display()

    def save_encounter(self, encounter, output_file):
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(encounter, json_file, indent=4)

    def run(self, difficulty):
        encounter = self.generate_encounter(difficulty)
        self.save_encounter(encounter, 'json/current_encounter.json')

# Example usage:
if __name__ == "__main__":
    monster_file_path = 'json/srd_5e_monsters.json'
    character_file_path = 'json/character_data.json'
    encounter_builder = EncounterBuilder(monster_file_path, character_file_path)
    while True:
        try:
            difficulty = input("Enter encounter difficulty (easy, medium, hard, deadly): ").lower()
            if difficulty == 'quit':
                break
            encounter_builder.run(difficulty)
        except ValueError as e:
            print(e)
