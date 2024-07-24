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


    def extract_spreadsheet_id(url):
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
        

    def spell_filter(self, spell_list):
        """
        Filters out 'Not Found' entries from a list of spells.

        Parameters:
        spell_list (list): A list containing spell names.

        Returns:
        list: A list with 'Not Found' entries removed.
        """
        return [spell for spell in spell_list if spell != 'Not Found']


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
            'v2.1!C6:R7', 'v2.1!AL6:AM7','v2.1!T5:AD5', 'v2.1!T7:AD7', 'v2.1!AJ11:AN11',
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
            'v2.1!AC32:AN32', 'v2.1!AC33:AN33', 'v2.1!AC34:AN34', 'v2.1!AC35:AN35', 'v2.1!AC36:AN36',
            'v2.1!N96:T96', 'v2.1!N97:T97', 'v2.1!N98:T98', 'v2.1!X96:AD96', 'v2.1!X97:AD97', 'v2.1!X98:AD98',
            'v2.1!AH96:AN96', 'v2.1!AH97:AN97', 'v2.1!AH98:AN98', 'v2.1!X100:AD100', 'v2.1!X101:AD101',
            'v2.1!X102:AD102', 'v2.1!X103:AD103', 'v2.1!X104:AD104', 'v2.1!N100:T100', 'v2.1!N101:T101',
            'v2.1!N102:T102', 'v2.1!N103:T103', 'v2.1!N104:T104', 'v2.1!D100:J100', 'v2.1!D101:J101',
            'v2.1!D102:J102', 'v2.1!D103:J103', 'v2.1!D104:J104', 'v2.1!N106:T106', 'v2.1!N107:T107',
            'v2.1!N108:T108', 'v2.1!N109:T109', 'v2.1!N110:T110', 'v2.1!X106:AD106', 'v2.1!X107:AD107',
            'v2.1!X108:AD108', 'v2.1!X109:AD109', 'v2.1!X110:AD110', 'v2.1!AH106:AN106', 'v2.1!AH107:AN107',
            'v2.1!AH108:AN108', 'v2.1!AH109:AN109', 'v2.1!AH110:AN110', 'v2.1!X112:AD112', 'v2.1!X113:AD113',
            'v2.1!X114:AD114', 'v2.1!X115:AD115', 'v2.1!X116:AD116', 'v2.1!N112:T112', 'v2.1!N113:T113',
            'v2.1!N114:T114', 'v2.1!N115:T115', 'v2.1!N116:T116', 'v2.1!D112:J112', 'v2.1!D113:J113',
            'v2.1!D114:J114', 'v2.1!D115:J115', 'v2.1!D116:J116', 'v2.1!N118:T118', 'v2.1!N119:T119', 'v2.1!N120:T120',
            'v2.1!N121:T121', 'v2.1!X118:AD118', 'v2.1!X119:AD119', 'v2.1!X120:AD120', 'v2.1!X121:AD121', 'v2.1!AH118:AN118',
            'v2.1!AH119:AN119', 'v2.1!AH120:AN120', 'v2.1!AH121:AN121', 'v2.1!X123:AD123', 'v2.1!X124:AD124',
            'v2.1!X125:AD125', 'v2.1!X126:AD126', 'v2.1!N123:T123', 'v2.1!N124:T124', 'v2.1!N125:T125', 'v2.1!N126:T126',
            'v2.1!D123:J123', 'v2.1!D124:J124', 'v2.1!D125:J125', 'v2.1!D126:J126', 'v2.1!N128:T128', 'v2.1!N129:T129',
            'v2.1!N130:T130', 'v2.1!N131:T131', 'v2.1!X128:AD128', 'v2.1!X129:AD129', 'v2.1!X130:AD130', 'v2.1!X131:AD131',
            'v2.1!AH128:AN128', 'v2.1!AH129:AN129', 'v2.1!AH130:AN130', 'v2.1!AH131:AN131', 'v2.1!X133:AD133',
            'v2.1!X134:AD134', 'v2.1!X135:AD135', 'v2.1!N133:T133', 'v2.1!N134:T134', 'v2.1!N135:T135', 'v2.1!D133:J133',
            'v2.1!D134:J134', 'v2.1!D135:J135', 'v2.1!N137:T137', 'v2.1!N138:T138', 'v2.1!N139:T139', 'v2.1!X137:AD137',
            'v2.1!X138:AD138', 'v2.1!X139:AD139', 'v2.1!AH137:AN137', 'v2.1!AH138:AN138', 'v2.1!AH139:AN139',
            'v2.1!X141:AD141', 'v2.1!X142:AD142', 'v2.1!X143:AD143', 'v2.1!N141:T141', 'v2.1!N142:T142', 'v2.1!N143:T143',
            'v2.1!D141:J141', 'v2.1!D142:J142', 'v2.1!D143:J143'
        ]

        values = self.get_batch_cell_values(spreadsheet_id, cells_to_fetch)

        data = {
            'Character Name': values['v2.1!C6:R7'],
            'Level': values['v2.1!AL6:AM7'],
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
                'Cantrips': {
                    'Cantrips': self.spell_filter([
                        values['v2.1!N96:T96'], values['v2.1!N97:T97'], values['v2.1!N98:T98'], values['v2.1!X96:AD96'], values['v2.1!X97:AD97'], 
                        values['v2.1!X98:AD98'], values['v2.1!AH96:AN96'], values['v2.1!AH97:AN97'], values['v2.1!AH98:AN98']
                    ])
                },
                'Level 1': {
                    'Level 1': self.spell_filter([
                        values['v2.1!X100:AD100'], values['v2.1!X101:AD101'], values['v2.1!X102:AD102'], values['v2.1!X103:AD103'], values['v2.1!X104:AD104'], 
                        values['v2.1!N100:T100'], values['v2.1!N101:T101'], values['v2.1!N102:T102'], values['v2.1!N103:T103'], values['v2.1!N104:T104'], 
                        values['v2.1!D100:J100'], values['v2.1!D101:J101'], values['v2.1!D102:J102'], values['v2.1!D103:J103'], values['v2.1!D104:J104']
                    ])
                },
                'Level 2': {
                    'Level 2': self.spell_filter([
                        values['v2.1!N106:T106'], values['v2.1!N107:T107'], values['v2.1!N108:T108'], values['v2.1!N109:T109'], values['v2.1!N110:T110'], 
                        values['v2.1!X106:AD106'], values['v2.1!X107:AD107'], values['v2.1!X108:AD108'], values['v2.1!X109:AD109'], values['v2.1!X110:AD110'], 
                        values['v2.1!AH106:AN106'], values['v2.1!AH107:AN107'], values['v2.1!AH108:AN108'], values['v2.1!AH109:AN109'], values['v2.1!AH110:AN110']
                    ])
                },
                'Level 3': {
                    'Level 3': self.spell_filter([
                        values['v2.1!X112:AD112'], values['v2.1!X113:AD113'], values['v2.1!X114:AD114'], values['v2.1!X115:AD115'], values['v2.1!X116:AD116'], 
                        values['v2.1!N112:T112'], values['v2.1!N113:T113'], values['v2.1!N114:T114'], values['v2.1!N115:T115'], values['v2.1!N116:T116'], 
                        values['v2.1!D112:J112'], values['v2.1!D113:J113'], values['v2.1!D114:J114'], values['v2.1!D115:J115'], values['v2.1!D116:J116']
                    ])
                },
                'Level 4': {
                    'Level 4': self.spell_filter([
                        values['v2.1!N118:T118'], values['v2.1!N119:T119'], values['v2.1!N120:T120'], values['v2.1!N121:T121'], values['v2.1!X118:AD118'], 
                        values['v2.1!X119:AD119'], values['v2.1!X120:AD120'], values['v2.1!X121:AD121'], values['v2.1!AH118:AN118'], values['v2.1!AH119:AN119'], 
                        values['v2.1!AH120:AN120'], values['v2.1!AH121:AN121']
                    ])
                },
                'Level 5': {
                    'Level 5': self.spell_filter([
                        values['v2.1!X123:AD123'], values['v2.1!X124:AD124'], values['v2.1!X125:AD125'], values['v2.1!X126:AD126'], values['v2.1!N123:T123'], 
                        values['v2.1!N124:T124'], values['v2.1!N125:T125'], values['v2.1!N126:T126'], values['v2.1!D123:J123'], values['v2.1!D124:J124'], 
                        values['v2.1!D125:J125'], values['v2.1!D126:J126']
                    ])
                },
                'Level 6': {
                    'Level 6': self.spell_filter([
                        values['v2.1!N128:T128'], values['v2.1!N129:T129'], values['v2.1!N130:T130'], values['v2.1!N131:T131'], values['v2.1!X128:AD128'], 
                        values['v2.1!X129:AD129'], values['v2.1!X130:AD130'], values['v2.1!X131:AD131'], values['v2.1!AH128:AN128'], values['v2.1!AH129:AN129'], 
                        values['v2.1!AH130:AN130'], values['v2.1!AH131:AN131']
                    ])
                },
                'Level 7': {
                    'Level 7': self.spell_filter([
                        values['v2.1!X133:AD133'], values['v2.1!X134:AD134'], values['v2.1!X135:AD135'], values['v2.1!N133:T133'], values['v2.1!N134:T134'], 
                        values['v2.1!N135:T135'], values['v2.1!D133:J133'], values['v2.1!D134:J134'], values['v2.1!D135:J135']
                    ])
                },
                'Level 8': {
                    'Level 8': self.spell_filter([
                        values['v2.1!N137:T137'], values['v2.1!N138:T138'], values['v2.1!N139:T139'], values['v2.1!X137:AD137'], values['v2.1!X138:AD138'], 
                        values['v2.1!X139:AD139'], values['v2.1!AH137:AN137'], values['v2.1!AH138:AN138'], values['v2.1!AH139:AN139']
                    ])
                },
                'Level 9': {
                    'Level 9': self.spell_filter([
                        values['v2.1!X141:AD141'], values['v2.1!X142:AD142'], values['v2.1!X143:AD143'], values['v2.1!N141:T141'], values['v2.1!N142:T142'], 
                        values['v2.1!N143:T143'], values['v2.1!D141:J141'], values['v2.1!D142:J142'], values['v2.1!D143:J143']
                    ])
                }
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


    def get_spreadsheet_url(gsheet_interpreter):
        """
        Prompts the user to enter a Google Sheets URL and extracts the spreadsheet ID.

        Parameters:
        gsheet_interpreter (GSheetInterpreter): The GSheetInterpreter instance.

        Returns:
        str: The extracted spreadsheet ID.
        """
        while True:
            try:
                spreadsheet_url = input("Enter the Gsheet v2.1 character sheet: ")
                spreadsheet_id = GSheetInterpreter.extract_spreadsheet_id(spreadsheet_url)
                return spreadsheet_id
            except ValueError as e:
                print(e)
                print("Please enter the sharable link from your Gsheet v2.1 character sheet.")
                print("Template link: https://docs.google.com/spreadsheets/d/1ApmbXHTln99fPTUpanyQRTXNzXbQ8UBTt3Uq8xInQKw/edit")


    def run():
        # Initialize the GSheetInterpreter
        service_account_file = 'O:/Coding/python/gitstuff/NOSHARING/dreamscape-430319-8e201173f32c.json'
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        gsheet_interpreter = GSheetInterpreter(service_account_file, scopes)

        # Get the spreadsheet URL and extract the ID
        spreadsheet_id = GSheetInterpreter.get_spreadsheet_url(gsheet_interpreter)

        # Parse character sheet
        character_data = gsheet_interpreter.parse_character_sheet(spreadsheet_id)

        # Save to JSON file
        output_file = os.path.join(os.path.dirname(__file__), 'json/character_data.json')
        gsheet_interpreter.save_to_json(character_data, output_file)

        # Print the fetched values
        print(f"Character data saved to {output_file}")
        print(json.dumps(character_data, indent=4))


def main():
    GSheetInterpreter.run()


if __name__ == "__main__":
    main()
