import pdfplumber
import json
import re
import os

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

def safe_search(pattern, text):
    match = re.search(pattern, text)
    return match.group(1).strip() if match else "Not Found"

def parse_character_sheet(text):
    data = {}

    # Print the raw text for debugging
    print("Raw PDF text:\n", text)

    # General character information
    data['Character Name'] = safe_search(r'\bNAME\b\s+([^\n]+)', text)
    data['Classes_Levels'] = safe_search(r'\bCLASS\(ES\) & LEVEL\(S\)\s+([^\n]+)', text)
    data['Race'] = safe_search(r'\bRACE\b\s+([^\n]+)', text)
    
    # Ability Scores
    data['Ability Scores'] = {
        'Strength': safe_search(r'STR\s*\d*\s*([\d]+)', text),
        'Dexterity': safe_search(r'DEX\s*\d*\s*([\d]+)', text),
        'Constitution': safe_search(r'CON\s*\d*\s*([\d]+)', text),
        'Intelligence': safe_search(r'INT\s*\d*\s*([\d]+)', text),
        'Wisdom': safe_search(r'WIS\s*\d*\s*([\d]+)', text),
        'Charisma': safe_search(r'CHA\s*\d*\s*([\d]+)', text)
    }

    # Proficiency Bonus
    data['Proficiency Bonus'] = safe_search(r'PROFICIENCY BONUS\s+(\+\d+)', text)

    # Saving Throws
    data['Saving Throws'] = {
        'Strength': safe_search(r'Strength\s*\+?([\d]+)', text),
        'Dexterity': safe_search(r'Dexterity\s*\+?([\d]+)', text),
        'Constitution': safe_search(r'Constitution\s*\+?([\d]+)', text),
        'Intelligence': safe_search(r'Intelligence\s*\+?([\d]+)', text),
        'Wisdom': safe_search(r'Wisdom\s*\+?([\d]+)', text),
        'Charisma': safe_search(r'Charisma\s*\+?([\d]+)', text)
    }

    # Skills
    skills = [
        'Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception',
        'History', 'Insight', 'Intimidation', 'Investigation', 'Medicine',
        'Nature', 'Perception', 'Performance', 'Persuasion', 'Religion',
        'Sleight of Hand', 'Stealth', 'Survival'
    ]
    data['Skills'] = {skill: safe_search(rf'{skill}\s*\(.*?\)\s*\+?([\d]+)', text) for skill in skills}

    # AC, Initiative, Speed, Hit Points
    data['AC'] = safe_search(r'\bAC\b\s+([\d]+)', text)
    data['Initiative'] = safe_search(r'\bINIT\b\s+([\d]+)', text)
    data['Speed'] = safe_search(r'\bSPEED\b\s+([\d]+)', text)
    data['Hit Point Max'] = safe_search(r'Hit Point Max\s+([\d]+)', text)
    data['Current HP'] = safe_search(r'CURRENT HIT POINTS\s+([\d]+)', text)
    data['Temp HP'] = safe_search(r'TEMPORARY HIT POINTS\s+([\d]+)', text)

    # Attacks and Notes
    attacks_pattern = re.compile(r'NAME\s+ATK BONUS\s+DAMAGE/TYPE\s+([^\n]+)\s*\+?([\d]+)\s*([^\n]+)', re.DOTALL)
    data['Attacks and Notes'] = [
        {
            'Attack Name': match[0].strip(),
            'Atk Bonus': match[1].strip(),
            'Damage Type': match[2].strip()
        }
        for match in attacks_pattern.findall(text)
    ]

    # Passive Perception
    data['Passive Perception'] = safe_search(r'PASSIVE WISDOM \(PERCEPTION\)\s+([\d]+)', text)

    # Languages
    data['Languages'] = safe_search(r'LANGUAGES\s+([^\n]+)', text)

    # Features and Traits
    data['Features and Traits'] = safe_search(r'FEATURES & TRAITS\s+([^\n]+)', text)

    # Spellcasting Information
    data['Spellcasting'] = {
        'Class': safe_search(r'SPELLCASTING\s+CLASS\s+([^\n]+)', text),
        'Ability': safe_search(r'SPELLCASTING\s+ABILITY\s+([^\n]+)', text),
        'Save DC': safe_search(r'SPELL SAVE DC\s+([\d]+)', text),
        'Attack Bonus': safe_search(r'SPELL ATTACK BONUS\s+(\+\d+)', text),
    }

    # Spell Slots
    spell_slots_pattern = re.compile(r'(\d+)\s*:\s*\[?(\d+)\]?')
    data['Spell Slots'] = {match[0]: match[1] for match in spell_slots_pattern.findall(text)}

    # Prepared Spells and Cantrips
    spells_pattern = re.compile(r'(CANTRIPS|LEVEL \d+ SPELLS)(.*?)\s*(?=CANTRIPS|LEVEL \d+ SPELLS|$)', re.DOTALL)
    data['Prepared Spells and Cantrips'] = {
        match[0]: [spell.strip() for spell in match[1].split('\n') if spell.strip()]
        for match in spells_pattern.findall(text)
    }

    return data

def save_to_json(data, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    default_directory = os.path.join(os.path.expanduser("~"), "Downloads")
    pdf_name = input(f"Enter the name of the character sheet PDF (default directory is {default_directory}): ")
    pdf_path = os.path.join(default_directory, pdf_name)

    if not os.path.isfile(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return

    text = extract_text_from_pdf(pdf_path)
    character_data = parse_character_sheet(text)
    
    output_file = os.path.join(os.path.dirname(__file__), 'character_data.json')
    save_to_json(character_data, output_file)
    
    print(f"Character data saved to {output_file}")
    
    # Print the contents of the JSON file
    with open(output_file, 'r') as json_file:
        data = json.load(json_file)
        print(json.dumps(data, indent=4))

if __name__ == "__main__":
    main()
