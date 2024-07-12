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

def safe_split_line(line, index, default="Not Found"):
    parts = line.split()
    if isinstance(index, tuple):  # Check if index is a tuple indicating a range
        start, end = index
        if end == -1:
            return ' '.join(parts[start:])  # Return from start index to the end
        else:
            return ' '.join(parts[start:end + 1]) if len(parts) > start else default
    else:
        return parts[index] if len(parts) > index else default

def extract_inventory(text):
    inventory_pattern = re.compile(r"EQUIPPED ITEMS\s+(.*?)\s+FEATURES & TRAITS", re.DOTALL)
    match = inventory_pattern.search(text)
    if match:
        inventory_text = match.group(1).strip()
        return inventory_text.split('\n')
    return ["Not Found"]

def parse_attack_info(attack_info):
    parsed_attacks = []
    for attack in attack_info:
        if attack.strip() == "- -":
            parsed_attacks.append({
                'Attack Name': '-',
                'Attack Modifier': '-',
                'Attack Description': '-'
            })
        else:
            match = re.search(r"(.+?)\s+(\+\d+)\s+(.+)", attack)
            if match:
                parsed_attacks.append({
                    'Attack Name': match.group(1).strip(),
                    'Attack Modifier': match.group(2).strip(),
                    'Attack Description': match.group(3).strip()
                })
            else:
                parsed_attacks.append({
                    'Attack Name': 'Not Found',
                    'Attack Modifier': 'Not Found',
                    'Attack Description': 'Not Found'
                })
    return parsed_attacks

def extract_spell_info(text):
    # Remove unnecessary characters and prepare text for processing
    cleaned_text = text.replace('\u25c9', '').replace('〇', '').replace('CANTRIPS', '').replace('SLOTS MAX', '').strip()

    spell_lines = cleaned_text.split('\n')

    spells = {
        "Cantrips": [],
        "Level 1": [],
        "Level 2": [],
        "Level 3": [],
        "Level 4": [],
        "Level 5": [],
        "Level 6": [],
        "Level 7": [],
        "Level 8": [],
        "Level 9": []
    }

    slots = {
        "Level 1": {"current": 0, "max": 0},
        "Level 2": {"current": 0, "max": 0},
        "Level 3": {"current": 0, "max": 0},
        "Level 4": {"current": 0, "max": 0},
        "Level 5": {"current": 0, "max": 0},
        "Level 6": {"current": 0, "max": 0},
        "Level 7": {"current": 0, "max": 0},
        "Level 8": {"current": 0, "max": 0},
        "Level 9": {"current": 0, "max": 0}
    }

    # Extracting spell slots
    slot_lines = [81, 86, 91, 96, 100, 104, 108, 112, 116]

    for i, line_number in enumerate(slot_lines):
        try:
            parts = re.findall(r'\d+', spell_lines[line_number])
            if i % 2 == 0:  # Even index: current on left, max on right
                slots[f"Level {i + 1}"]["current"] = int(parts[0])
                slots[f"Level {i + 1}"]["max"] = int(parts[1])
            else:  # Odd index: max on left, current on right
                slots[f"Level {i + 2}"]["max"] = int(parts[0])
                slots[f"Level {i + 2}"]["current"] = int(parts[1])
        except IndexError:
            slots[f"Level {i + 1}"]["current"] = 0
            slots[f"Level {i + 1}"]["max"] = 0
        except ValueError:
            slots[f"Level {i + 1}"]["current"] = 0
            slots[f"Level {i + 1}"]["max"] = 0

    # Extracting spells
    spell_section = re.search(r"ABILITY SAVE DC ATTACK BONUS\s+(.*?)\s+AGE HEIGHT WEIGHT SIZE", text, re.DOTALL).group(1)
    spell_lines = spell_section.split('\n')

    current_level = "Cantrips"
    level_pattern = re.compile(r'Level (\d+)')

    for line in spell_lines:
        line = line.strip()
        if not line:
            continue
        if "Level 1" in line:
            current_level = "Level 1"
        elif "Level 2" in line:
            current_level = "Level 2"
        elif "Level 3" in line:
            current_level = "Level 3"
        elif "Level 4" in line:
            current_level = "Level 4"
        elif "Level 5" in line:
            current_level = "Level 5"
        elif "Level 6" in line:
            current_level = "Level 6"
        elif "Level 7" in line:
            current_level = "Level 7"
        elif "Level 8" in line:
            current_level = "Level 8"
        elif "Level 9" in line:
            current_level = "Level 9"
        else:
            spells[current_level].append(line)

    return spells, slots


def parse_character_sheet(text):
    data = {}

    # Extract relevant lines
    lines = text.split('\n')

    # Extract information using the updated safe_split_line function
    data['Character Name'] = safe_split_line(lines[1], 0)
    data['Classes_Levels'] = safe_split_line(lines[0], (0, 4))
    data['Race'] = safe_split_line(lines[2], 0)
    data['Background'] = safe_split_line(lines[8], (1, -1))
    data['Ability Scores'] = {
        'Strength': safe_split_line(lines[12], 0),
        'Dexterity': safe_split_line(lines[20], 0),
        'Constitution': safe_split_line(lines[25], 0),
        'Intelligence': safe_split_line(lines[32], 0),
        'Wisdom': safe_split_line(lines[37], 0),
        'Charisma': safe_split_line(lines[42], 0)
    }
    data['Proficiency Bonus'] = safe_split_line(lines[9], 1)
    data['Saving Throws'] = {
        'Strength': safe_split_line(lines[17], 2),
        'Dexterity': safe_split_line(lines[18], 3),
        'Constitution': safe_split_line(lines[19], 2),
        'Intelligence': safe_split_line(lines[20], 3),
        'Wisdom': safe_split_line(lines[21], 4),
        'Charisma': safe_split_line(lines[23], 2)
    }
    data['Skills'] = {
        'Acrobatics': safe_split_line(lines[25], 2),
        'Animal Handling': safe_split_line(lines[27], 2),
        'Arcana': safe_split_line(lines[28], 2),
        'Athletics': safe_split_line(lines[29], 3),
        'Deception': safe_split_line(lines[30], 1),
        'History': safe_split_line(lines[32], 2),
        'Insight': safe_split_line(lines[33], 3),
        'Intimidation': safe_split_line(lines[34], 2),
        'Investigation': safe_split_line(lines[35], 2),
        'Medicine': safe_split_line(lines[36], 1),
        'Nature': safe_split_line(lines[37], 2),
        'Perception': safe_split_line(lines[38], 2),
        'Performance': safe_split_line(lines[39], 2),
        'Persuasion': safe_split_line(lines[40], 2),
        'Religion': safe_split_line(lines[41], 1),
        'Sleight of Hand': safe_split_line(lines[42], 2),
        'Stealth': safe_split_line(lines[43], 2),
        'Survival': safe_split_line(lines[44], 1)
    }
    data['AC'] = safe_split_line(lines[9], 0)
    data['Initiative'] = safe_split_line(lines[9], 1)
    data['Speed'] = safe_split_line(lines[10], 1)
    data['Hit Point Max'] = safe_split_line(lines[15], 3)
    data['Current HP'] = safe_split_line(lines[17], 5)
    data['Temp HP'] = safe_split_line(lines[21], (6, -1))
    
    attack_info = [
        safe_split_line(lines[34], (5, -1)),
        safe_split_line(lines[35], (5, -1)),
        safe_split_line(lines[36], (3, -1)),
        safe_split_line(lines[37], (5, -1)),
        safe_split_line(lines[38], (4, -1))
    ]
    data['Attack Info'] = parse_attack_info(attack_info)
    
    data['Passive Perception'] = safe_split_line(lines[47], 0)
    data['Languages'] = [
        safe_split_line(lines[48], 0),
        safe_split_line(lines[49], 0), 
        safe_split_line(lines[50], 0)
    ]
    data['Inventory'] = extract_inventory(text)
    
    data['Spellcasting'] = {
        'Class': safe_split_line(lines[72], 0),
        'Ability': safe_split_line(lines[73], 0),
        'Save DC': safe_split_line(lines[71], 0),
        'Attack Bonus': safe_split_line(lines[71], 1)
    }
    spells, slots = extract_spell_info(text)
    data['Spell Slots'] = slots
    data['Prepared Spells and Cantrips'] = spells
    
    return data

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

def save_raw_text(text, output_file):
    with open(output_file, 'w', encoding='utf-8') as raw_text_file:
        raw_text_file.write(text)

def main():
    default_directory = os.path.join(os.path.expanduser("~"), "Downloads")
    pdf_name = input(f"Enter the name of the character sheet PDF (default directory is {default_directory}): ")
    pdf_path = os.path.join(default_directory, pdf_name)

    if not os.path.isfile(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return

    text = extract_text_from_pdf(pdf_path)
    
    # Save raw text to file
    raw_text_file = os.path.join(os.path.dirname(__file__), 'rawText.txt')
    save_raw_text(text, raw_text_file)
    
    character_data = parse_character_sheet(text)
    
    output_file = os.path.join(os.path.dirname(__file__), 'character_data.json')
    save_to_json(character_data, output_file)
    
    print(f"Character data saved to {output_file}")
    print(json.dumps(character_data, indent=4))

if __name__ == "__main__":
    main()
