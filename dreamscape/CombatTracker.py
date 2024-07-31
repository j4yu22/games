# CombatTracker.py
import json
import random
from EncounterBuilder import EncounterBuilder
from Entity import Entity
from Event import Event

class CombatTracker:
    def __init__(self, character_file, encounter_file, monster_file):
        self.character_file = character_file
        self.encounter_file = encounter_file
        self.monster_file = monster_file
        self.character = self.load_character()
        self.character['Current HP'] = int(self.character['Current HP'])  # Ensure Current HP is an integer
        self.enemies = self.build_encounter()
        self.initiative_order = self.determine_initiative()

    def load_character(self):
        with open(self.character_file, 'r') as file:
            character_data = json.load(file)
        return character_data

    def build_encounter(self):
        difficulty = input("Enter encounter difficulty (easy, medium, hard, deadly): ").lower()
        encounter_builder = EncounterBuilder(self.monster_file, self.character_file)
        encounter = encounter_builder.generate_encounter(difficulty)
        enemies = []
        for enemy_data in encounter:
            enemy = Entity(
                name=enemy_data['name'],
                meta=enemy_data['meta'],
                ac=enemy_data['Armor Class'],
                hp=enemy_data['Hit Points'],
                speed=enemy_data['Speed'],
                attributes={
                    'STR': enemy_data['STR'],
                    'DEX': enemy_data['DEX'],
                    'CON': enemy_data['CON'],
                    'INT': enemy_data['INT'],
                    'WIS': enemy_data['WIS'],
                    'CHA': enemy_data['CHA']
                },
                senses=enemy_data.get('Senses', ''),
                languages=enemy_data.get('Languages', ''),
                challenge=enemy_data['Challenge'],
                traits=enemy_data.get('Traits', ''),
                actions=enemy_data.get('Actions', '')
            )
            enemies.append(enemy)
        return enemies

    def roll_initiative(self, entity):
        event = Event(event_type="initiative", entity=entity)
        event.roll_initiative(int(entity.attributes['DEX']))
        return event.roll_result

    def determine_initiative(self):
        initiatives = [(self.roll_initiative(enemy), enemy) for enemy in self.enemies]
        
        player_entity = Entity(
            name=self.character['Character Name'],
            meta="Player Character",
            ac=self.character['AC'],
            hp=self.character['Hit Point Max'],
            speed=self.character['Speed'],
            attributes={
                'STR': self.character['Ability Scores']['Strength'],
                'DEX': self.character['Ability Scores']['Dexterity'],
                'CON': self.character['Ability Scores']['Constitution'],
                'INT': self.character['Ability Scores']['Intelligence'],
                'WIS': self.character['Ability Scores']['Wisdom'],
                'CHA': self.character['Ability Scores']['Charisma']
            },
            senses="",
            languages=self.character['Languages'],
            challenge="",
            traits="",
            actions=""
        )
        
        player_initiative = self.roll_initiative(player_entity)
        
        initiatives.append((player_initiative, player_entity))
        
        initiatives.sort(key=lambda x: (x[0], int(x[1].attributes['DEX'])), reverse=True)
        return [entity for _, entity in initiatives]

    def display_status(self):
        print(f"{self.character['Character Name']}: {self.character['Current HP']} / {self.character['Hit Point Max']}")
        for enemy in self.enemies:
            status = "Healthy" if enemy.current_hp > (enemy.hp // 3) else "Bloodied" if enemy.current_hp > 0 else "Dead"
            print(f"{enemy.name}: {status}")
        print()  # Remove the additional newline here

    def run_combat(self):
        while self.enemies and self.character['Current HP'] > 0:
            self.display_status()
            # Simulate combat turns here
            # For now, just decrease HP of enemies for demonstration
            for enemy in self.enemies:
                if enemy.current_hp > 0:
                    enemy.current_hp -= 10  # Placeholder for actual combat logic

            # Remove dead enemies
            self.enemies = [enemy for enemy in self.enemies if enemy.current_hp > 0]

if __name__ == "__main__":
    monster_file_path = 'json/srd_5e_monsters.json'
    character_file_path = 'json/character_data.json'
    encounter_file_path = 'json/current_encounter.json'

    combat_tracker = CombatTracker(character_file_path, encounter_file_path, monster_file_path)
    combat_tracker.run_combat()
