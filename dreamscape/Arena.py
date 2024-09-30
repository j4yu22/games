import json
import random
from EncounterBuilder import EncounterBuilder
from Entity import Entity
from Event import Event

class CombatTracker:
    def __init__(self, character_file, encounter_file, monster_file, log_file='roll_log.txt'):
        self.character_file = character_file
        self.encounter_file = encounter_file
        self.monster_file = monster_file
        self.log_file = log_file
        self.character = self.load_character()
        self.character['Current HP'] = int(self.character['Current HP'])
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
            actions = enemy_data['Actions']
            if isinstance(actions, str):
                try:
                    actions = json.loads(actions)
                except json.JSONDecodeError:
                    actions = {'Unknown Action': {'Name': 'Unknown Action', 'Bonus': '', 'Damage': '', 'Description': actions}}
            enemy = Entity(
                name=enemy_data['name'],
                meta=enemy_data['meta'],
                ac=enemy_data['Armor Class'],
                hp=enemy_data['Hit Points'],
                speed=enemy_data['Speed'],
                attributes={
                    'STR': int(enemy_data['STR']),
                    'DEX': int(enemy_data['DEX']),
                    'CON': int(enemy_data['CON']),
                    'INT': int(enemy_data['INT']),
                    'WIS': int(enemy_data['WIS']),
                    'CHA': int(enemy_data['CHA'])
                },
                senses=enemy_data.get('Senses', ''),
                languages=enemy_data.get('Languages', ''),
                challenge=enemy_data['Challenge'],
                traits=enemy_data.get('Traits', ''),
                actions=actions
            )
            enemies.append(enemy)
        return enemies

    def roll_initiative(self, entity):
        dexterity_modifier = (int(entity.attributes['DEX']) - 10) // 2
        event = Event(event_type="initiative", entity=entity.name)
        event.roll_initiative(dexterity_modifier)
        event.write_log_to_file(self.log_file)
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
                'STR': int(self.character['Ability Scores']['Strength']),
                'DEX': int(self.character['Ability Scores']['Dexterity']),
                'CON': int(self.character['Ability Scores']['Constitution']),
                'INT': int(self.character['Ability Scores']['Intelligence']),
                'WIS': int(self.character['Ability Scores']['Wisdom']),
                'CHA': int(self.character['Ability Scores']['Charisma'])
            },
            senses="",
            languages=self.character['Languages'],
            challenge="",
            traits="",
            actions=self.character['Attack Info']
        )
        
        player_initiative = self.roll_initiative(player_entity)
        
        initiatives.append((player_initiative, player_entity))
        
        initiatives.sort(key=lambda x: (x[0], int(x[1].attributes['DEX'])), reverse=True)
        return initiatives

    def display_status(self):
        for initiative, entity in self.initiative_order:
            if entity.meta == "Player Character":
                print(f"{entity.name}: {self.character['Current HP']} / {self.character['Hit Point Max']}; Initiative: {initiative}")
            else:
                status = "Healthy" if entity.current_hp > (entity.hp // 3) else "Bloodied" if entity.current_hp > 0 else "Dead"
                print(f"{entity.name}: {status}; Initiative: {initiative}")
        print()

    def run_combat(self):
        round_counter = 0
        while self.enemies and self.character['Current HP'] > 0:
            round_counter += 1
            print(f"--- Round {round_counter} ---")
            self.display_status()

            for initiative, entity in self.initiative_order:
                if entity.current_hp <= 0:
                    continue
                
                # Placeholder for turn logic
                self.turn(entity)

            # Remove dead enemies
            self.enemies = [enemy for enemy in self.enemies if enemy.current_hp > 0]

            if not self.enemies:
                print("All enemies are defeated. You win!")
                break

        if self.character['Current HP'] <= 0:
            print("You have been defeated.")

    def turn(self, entity):
        # Placeholder for turn logic
        if entity.meta == "Player Character":
            print("It's your turn!")
            # Here, you can prompt the player for an action
        else:
            print(f"{entity.name} (enemy) takes its turn.")
            # Add enemy behavior logic here


if __name__ == "__main__":
    monster_file_path = 'json/srd_5e_monsters.json'
    character_file_path = 'json/character_data.json'
    encounter_file_path = 'json/current_encounter.json'

    combat_tracker = CombatTracker(character_file_path, encounter_file_path, monster_file_path)
    combat_tracker.run_combat()
