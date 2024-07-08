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

def parse_character_sheet(text):
    data = {}

    # Debug print statement to inspect the text content
    print(text)

    def safe_search(pattern, text):
        match = re.search(pattern, text)
        return match.group(1).strip() if match else "Not Found"

    # Using regex to extract data; this needs to be customized based on the exact PDF layout
    data['Name'] = safe_search(r'PLAYER NAME\s+([^\n]+)', text)
    data['Class_Level'] = safe_search(r'CLASS\(ES\) & LEVEL\(S\)\s+([^\n]+)', text)
    data['Race'] = safe_search(r'RACE\s+([^\n]+)', text)
    data['Experience'] = safe_search(r'EXPERIENCE\s+([^\n]+)', text)
    data['Background'] = safe_search(r'BACKGROUND:\s+([^\n]+)', text)
    data['Alignment'] = safe_search(r'ALIGNMENT:\s+([^\n]+)', text)
    
    # Attributes
    data['Attributes'] = {
        'Strength': safe_search(r'STR\s+(\d+)', text),
        'Dexterity': safe_search(r'DEX\s+(\d+)', text),
        'Constitution': safe_search(r'CON\s+(\d+)', text),
        'Intelligence': safe_search(r'INT\s+(\d+)', text),
        'Wisdom': safe_search(r'WIS\s+(\d+)', text),
        'Charisma': safe_search(r'CHA\s+(\d+)', text)
    }

    # Proficiencies
    data['Proficiencies'] = {
        'Armor': safe_search(r'Armor Proficiencies:\s+([^\n]+)', text),
        'Weapons': safe_search(r'Weapon Proficiencies:\s+([^\n]+)', text),
        'Tools': safe_search(r'Tool Proficiency:\s+([^\n]+)', text),
        'Languages': safe_search(r'LANGUAGES\s+([^\n]+)', text)
    }

    # Skills (only listing a few for example purposes)
    data['Skills'] = {
        'Acrobatics': safe_search(r'Acrobatics \(Dex\)\s+\+?(\d+)', text),
        'Animal Handling': safe_search(r'Animal Handling\(Wis\)\s+\+?(\d+)', text),
        'Arcana': safe_search(r'Arcana\(Int\)\s+\+?(\d+)', text)
    }

    # Add other necessary fields similarly...

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

if __name__ == "__main__":
    main()
