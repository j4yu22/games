import os
import re
import json
import google.auth
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

class GSheetInterpreter:
    """
    A class to handle Google Sheets operations and parse character sheet data.
    """

    def __init__(self, service_account_file, scopes):
        """
        Initializes the GSheetInterpreter with Google Sheets API credentials.

        Parameters:
        service_account_file (str): Path to the service account key file.
        scopes (list): The list of scopes for Google Sheets API access.
        """
        self.service_account_file = service_account_file
        self.scopes = scopes
        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.scopes
        )
        self.service = build('sheets', 'v4', credentials=self.creds)

    def get_batch_cell_values(self, spreadsheet_id, ranges):
        """
        Fetches the values from the specified cell ranges in the Google Sheet.

        Parameters:
        spreadsheet_id (str): The ID of the spreadsheet.
        ranges (list): The list of cell ranges to fetch the values from.

        Returns:
        dict: A dictionary with cell ranges as keys and their corresponding values as values.
        """
        sheet = self.service.spreadsheets()
        try:
            result = sheet.values().batchGet(spreadsheetId=spreadsheet_id, ranges=ranges).execute()
            value_ranges = result.get('valueRanges', [])
        except HttpError as error:
            print(f"HttpError occurred: {error}")
            return {cell_range: 'Cell not found' for cell_range in ranges}

        values_dict = {}
        for value_range in value_ranges:
            range_name = value_range.get('range')
            values = value_range.get('values', [])
            if not values:
                values_dict[range_name] = 'Not Found'
            else:
                flattened_values = ' '.join([str(item) for sublist in values for item in sublist])
                cleaned_values = re.sub(r'[^\x00-\x7F]+', '', flattened_values)
                cleaned_values = re.sub(r'\s+', ' ', cleaned_values).strip()
                values_dict[range_name] = cleaned_values
        return values_dict

    def extract_spreadsheet_id(self, url):
        """
        Extracts the spreadsheet ID from the given Google Sheets URL.

        Parameters:
        url (str): The URL of the Google Sheets document.

        Returns:
        str: The extracted spreadsheet ID.
        """
        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid Google Sheets URL")

    def parse_character_sheet(self, spreadsheet_id):
        """
        Parses the character sheet data from the Google Sheets document.

        Parameters:
        spreadsheet_id (str): The ID of the Google Sheets document.

        Returns:
        dict: The parsed character sheet data.
        """
        data = {}
        cells_to_fetch = [
            'v2.1!C6:R7', 'v2.1!T5:AD5', 'v2.1!T7:AD7', 'v2.1!AJ11:AN11',
            'v2.1!C15:D15', 'v2.1!C20:D20', 'v2.1!C25:D25', 'v2.1!C30:D30', 'v2.1!C35:D35', 'v2.1!C40:D40',
            'v2.1!H14:I15', 'v2.1!I17', 'v2.1!I18', 'v2.1!I19', 'v2.1!I20', 'v2.1!I21', 'v2.1!I22',
            'v2.1!I25', 'v2.1!I26', 'v2.1!I27', 'v2.1!I28', 'v2.1!I29', 'v2.1!I30', 'v2.1!I31', 'v2.1!I32',
            'v2.1!I33', 'v2.1!I34', 'v2.1!I35', 'v2.1!I36', 'v2.1!I37', 'v2.1!I38', 'v2.1!I39', 'v2.1!I40',
            'v2.1!I41', 'v2.1!I42', 'v2.1!R12:S13', 'v2.1!V12:W13', 'v2.1!Z12:AA13', 'v2.1!U16:AA16',
            'v2.1!R17:AA18', 'v2.1!R21:AA22', 'v2.1!C45:D46', 'v2.1!R45:Z56', 'v2.1!C59:AN85',
            'v2.1!C91:R92', 'v2.1!U91:X92', 'v2.1!AB91:AE92', 'v2.1!AI91:AL92',
            'v2.1!AG101:AH102', 'v2.1!AK101:AL102', 'v2.1!I107:J108', 'v2.1!E107:F108', 'v2.1!AG113:AH114',
            'v2.1!AK113:AL114', 'v2.1!I119:J120', 'v2.1!E119:F120', 'v2.1!AG124:AH125', 'v2.1!AK124:AL125',
            'v2.1!I129:J130', 'v2.1!E129:F130', 'v2.1!AG134:AH135', 'v2.1!AK134:AL135', 'v2.1!I138:J139',
            'v2.1!E138:F139', 'v2.1!AG142:AH143', 'v2.1!AK142:AL143',
            'v2.1!M96:AN98', 'v2.1!C100:AD104', 'v2.1!M106:AN110', 'v2.1!C112:AD116', 'v2.1!M118:AN121',
            'v2.1!C123:AD126', 'v2.1!M128:AN131', 'v2.1!C133:AD135', 'v2.1!M137:AN139', 'v2.1!C141:AD143',
            'v2.1!R32:W32', 'v2.1!R33:W33', 'v2.1!R34:W34', 'v2.1!R35:W35', 'v2.1!R36:W36',
            'v2.1!Y32:AA32', 'v2.1!Y33:AA33', 'v2.1!Y34:AA34', 'v2.1!Y35:AA35', 'v2.1!Y36:AA36',
            'v2.1!AC32:AN32', 'v2.1!AC33:AN33', 'v2.1!AC34:AN34', 'v2.1!AC35:AN35', 'v2.1!AC36:AN36'
        ]

        values = self.get_batch_cell_values(spreadsheet_id, cells_to_fetch)

        data = {
            'Character Name': values['v2.1!C6:R7'],
            'Classes_Levels': values['v2.1!T5:AD5'],
            'Race': values['v2.1!T7:AD7'],
            'Background': values['v2.1!AJ11:AN11'],
            'Ability Scores': {
                'Strength': values['v2.1!C15:D15'],
                'Dexterity': values['v2.1!C20:D20'],
                'Constitution': values['v2.1!C25:D25'],
                'Intelligence': values['v2.1!C30:D30'],
                'Wisdom': values['v2.1!C35:D35'],
                'Charisma': values['v2.1!C40:D40']
            },
            'Proficiency Bonus': values['v2.1!H14:I15'],
            'Saving Throws': {
                'Strength': values['v2.1!I17'],
                'Dexterity': values['v2.1!I18'],
                'Constitution': values['v2.1!I19'],
                'Intelligence': values['v2.1!I20'],
                'Wisdom': values['v2.1!I21'],
                'Charisma': values['v2.1!I22']
            },
            'Skills': {
                'Acrobatics': values['v2.1!I25'],
                'Animal Handling': values['v2.1!I26'],
                'Arcana': values['v2.1!I27'],
                'Athletics': values['v2.1!I28'],
                'Deception': values['v2.1!I29'],
                'History': values['v2.1!I30'],
                'Insight': values['v2.1!I31'],
                'Intimidation': values['v2.1!I32'],
                'Investigation': values['v2.1!I33'],
                'Medicine': values['v2.1!I34'],
                'Nature': values['v2.1!I35'],
                'Perception': values['v2.1!I36'],
                'Performance': values['v2.1!I37'],
                'Persuasion': values['v2.1!I38'],
                'Religion': values['v2.1!I39'],
                'Sleight of Hand': values['v2.1!I40'],
                'Stealth': values['v2.1!I41'],
                'Survival': values['v2.1!I42']
            },
            'AC': values['v2.1!R12:S13'],
            'Initiative': values['v2.1!V12:W13'],
            'Speed': values['v2.1!Z12:AA13'],
            'Hit Point Max': values['v2.1!U16:AA16'],
            'Current HP': values['v2.1!R17:AA18'],
            'Temp HP': values['v2.1!R21:AA22'],
            'Passive Perception': values['v2.1!C45:D46'],
            'Languages': values['v2.1!R45:Z56'],
            'Inventory': values['v2.1!C59:AN85'],
            'Spell Modifiers': {
                'Casting Class': values['v2.1!C91:R92'],
                'Casting Ability': values['v2.1!U91:X92'],
                'Save DC': values['v2.1!AB91:AE92'],
                'Spell Attack Modifier': values['v2.1!AI91:AL92']
            },
            'Spell Slots': {
                'Level 1': {'Current': values['v2.1!AG101:AH102'], 'Max': values['v2.1!AK101:AL102']},
                'Level 2': {'Current': values['v2.1!I107:J108'], 'Max': values['v2.1!E107:F108']},
                'Level 3': {'Current': values['v2.1!AG113:AH114'], 'Max': values['v2.1!AK113:AL114']},
                'Level 4': {'Current': values['v2.1!I119:J120'], 'Max': values['v2.1!E119:F120']},
                'Level 5': {'Current': values['v2.1!AG124:AH125'], 'Max': values['v2.1!AK124:AL125']},
                'Level 6': {'Current': values['v2.1!I129:J130'], 'Max': values['v2.1!E129:F130']},
                'Level 7': {'Current': values['v2.1!AG134:AH135'], 'Max': values['v2.1!AK134:AL135']},
                'Level 8': {'Current': values['v2.1!I138:J139'], 'Max': values['v2.1!E138:F139']},
                'Level 9': {'Current': values['v2.1!AG142:AH143'], 'Max': values['v2.1!AK142:AL143']}
            },
            'Prepared Spells and Cantrips': {
                'Cantrips': values['v2.1!M96:AN98'],
                'Level 1': values['v2.1!C100:AD104'],
                'Level 2': values['v2.1!M106:AN110'],
                'Level 3': values['v2.1!C112:AD116'],
                'Level 4': values['v2.1!M118:AN121'],
                'Level 5': values['v2.1!C123:AD126'],
                'Level 6': values['v2.1!M128:AN131'],
                'Level 7': values['v2.1!C133:AD135'],
                'Level 8': values['v2.1!M137:AN139'],
                'Level 9': values['v2.1!C141:AD143'],
            },
            'Attack Info': {
                'Attack 1': {
                    'Name': values['v2.1!R32:W32'],
                    'Bonus': values['v2.1!Y32:AA32'],
                    'Description': values['v2.1!AC32:AN32']
                },
                'Attack 2': {
                    'Name': values['v2.1!R33:W33'],
                    'Bonus': values['v2.1!Y33:AA33'],
                    'Description': values['v2.1!AC33:AN33']
                },
                'Attack 3': {
                    'Name': values['v2.1!R34:W34'],
                    'Bonus': values['v2.1!Y34:AA34'],
                    'Description': values['v2.1!AC34:AN34']
                },
                'Attack 4': {
                    'Name': values['v2.1!R35:W35'],
                    'Bonus': values['v2.1!Y35:AA35'],
                    'Description': values['v2.1!AC35:AN35']
                },
                'Attack 5': {
                    'Name': values['v2.1!R36:W36'],
                    'Bonus': values['v2.1!Y36:AA36'],
                    'Description': values['v2.1!AC36:AN36']
                }
            }
        }
        return data

    def save_to_json(self, data, output_file):
        """
        Saves the character data to a JSON file.

        Parameters:
        data (dict): The character data to save.
        output_file (str): The path to the JSON file to save the data.
        """
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)


def main():
    # Initialize the GSheetInterpreter
    service_account_file = 'O:/Coding/python/gitstuff/NOSHARING/dreamscape-430319-8e201173f32c.json'
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    gsheet_interpreter = GSheetInterpreter(service_account_file, scopes)

    # Get the spreadsheet URL and extract the ID
    spreadsheet_url = input("Enter the Google Sheets spreadsheet URL: ")
    spreadsheet_id = gsheet_interpreter.extract_spreadsheet_id(spreadsheet_url)

    # Parse character sheet
    character_data = gsheet_interpreter.parse_character_sheet(spreadsheet_id)

    # Save to JSON file
    output_file = os.path.join(os.path.dirname(__file__), 'character_data.json')
    gsheet_interpreter.save_to_json(character_data, output_file)

    # Print the fetched values
    print(f"Character data saved to {output_file}")
    print(json.dumps(character_data, indent=4))


if __name__ == "__main__":
    main()
