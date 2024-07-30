import requests
from bs4 import BeautifulSoup
import openai
import json
import re

# Load API key from the NOSHARING folder
with open('O:/Coding/python/gitstuff/NOSHARING/openai_api-key.json') as f:
    api_key_data = json.load(f)
    openai.api_key = api_key_data['spell_parser_key']

# Load character data from JSON file
with open('json/character_data.json') as f:
    character_data = json.load(f)

def fetch_spell_description(spell_name):
    url = f"http://dnd5e.wikidot.com/spell:{spell_name}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.find('div', class_='main-content')
        paragraphs = main_content.find_all('p')
        spell_description = '\n'.join(p.get_text() for p in paragraphs)
        return spell_description
    else:
        return None

class Spell:
    def __init__(self, name, level_cast, caster_level):
        self.name = name.replace(' ', '-').lower()
        self.level_cast = level_cast
        self.caster_level = caster_level
        self.description = fetch_spell_description(self.name)
        self.spell_slot_used = None
        self.range = None
        self.spell_attack_modifier = None
        self.spell_save_dc = None
        self.spell_save_ability = None
        self.damage_dice = None
        self.effects_applied = None
        self.effects_applied_if_failed_saving_throw = None

        if self.description:
            self.parse_spell_information()

    def parse_spell_information(self):
        # Extract basic information using regex or simple string parsing
        self.extract_basic_info()

        # Use OpenAI API to extract advanced information
        self.extract_advanced_info()

    def extract_basic_info(self):
        # Example of basic information extraction (range, default spell slot, etc.)
        range_match = re.search(r'Range: (\d+ feet|Touch|Self|Sight|Special)', self.description, re.IGNORECASE)
        self.range = range_match.group(1) if range_match else "Unknown"

    def extract_advanced_info(self):
        caster_level = character_data['Level']
        prompt = f"{self.description} and the caster is level {caster_level}"

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Only respond by filling in the following based on the information given you:\nspell attack modifier(if any): \nspell save ability (if any): \ndamage dice(formatted [# of dice]d[sides of dice]): "},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        print(response)
        parsed_response = response['choices'][0]['message']['content'].strip()
        self.parse_advanced_info_response(parsed_response)

    def parse_advanced_info_response(self, response_text):
        # Parse the response from OpenAI API to fill in the spell attributes
        # This can be done using regex or other parsing techniques
        spell_info = response_text.split('\n')
        for info in spell_info:
            if "spell attack modifier(if any):" in info:
                self.spell_attack_modifier = info.split(': ')[1].strip()
            elif "spell save ability (if any):" in info:
                self.spell_save_ability = info.split(': ')[1].strip()
            elif "damage dice(formatted [# of dice]d[sides of dice]):" in info:
                self.damage_dice = info.split(': ')[1].strip()

    def display(self):
        print(f"Spell Name: {self.name}")
        print(f"Spell Slot Used: {self.spell_slot_used}")
        print(f"Range: {self.range}")
        print(f"Spell Attack Modifier: {self.spell_attack_modifier}")
        print(f"Spell Save DC: {self.spell_save_dc}")
        print(f"Spell Save Ability: {self.spell_save_ability}")
        print(f"Damage Dice: {self.damage_dice}")
        print(f"Effects Applied: {self.effects_applied}")
        print(f"Effects Applied if Failed Saving Throw: {self.effects_applied_if_failed_saving_throw}")

# Example usage
spell = Spell(name="fire bolt", level_cast=0, caster_level=character_data['Level'])
spell.display()
