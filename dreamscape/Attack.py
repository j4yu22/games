import re
import openai
import json

# Load API key from the NOSHARING folder
with open('O:/Coding/python/gitstuff/NOSHARING/openai_api-key.json') as f:
    api_key_data = json.load(f)
    openai.api_key = api_key_data['spell_parser_key']

class Attack:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.damage_dice = None
        self.extraction_method = None

        self.parse_attack_information()

    def parse_attack_information(self):
        # Extract damage dice using regex
        self.extract_damage_dice()

        # If regex fails to extract damage dice, use OpenAI API
        if not self.damage_dice:
            self.extract_advanced_info()

    def extract_damage_dice(self):
        # Extract damage dice and modifiers for the primary target
        # Regex to find dice rolls and numerical modifiers in the format 2d4, +5, etc.
        matches = re.findall(r'\b\d+d\d+\b|\b\d+\b', self.description.split('|')[0])
        if matches:
            self.damage_dice = ' + '.join(matches)
            self.extraction_method = "Regex"

    def extract_advanced_info(self):
        prompt = f"Extract only the damage dice against the primary target from this attack description: {self.description}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract only the damage dice against the primary target from the attack description."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        parsed_response = response['choices'][0]['message']['content'].strip()
        self.damage_dice = parsed_response
        self.extraction_method = "AI"

    def display(self):
        print(f"Attack Name: {self.name}")
        print(f"Damage Dice: {self.damage_dice}")
        print(f"Extraction Method: {self.extraction_method}")

# Example usage
if __name__ == "__main__":
    attack = Attack(name="Flaming Twinblade", description="2d4+5[magical slashing]+2d8 + 2d6[fire-GFB]|***Simple Melee Weapon Attack.*** finesse, +1AC, 1d8 + 3 fire to adjacent target(GFB), effects of animated shield")
    attack.display()
