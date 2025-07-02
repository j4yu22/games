import json
from collections import defaultdict

"""
Creates a new JSON where words are grouped by their length and definitions are stripped.

Input:
    dictionary_file (JSON): Original dictionary with word definitions.

Output:
    output_file (JSON): Dictionary where each key is a word length and the value is a list of words of that length.
"""

def strip_definitions_and_group_by_length(dictionary_file: str, output_file: str):
    with open(dictionary_file, 'r', encoding='utf-8') as f:
        word_dict = json.load(f)

    grouped = defaultdict(list)

    for word in word_dict:
        grouped[str(len(word))].append(word)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(grouped, f, ensure_ascii=False, indent=2)


# Example usage
if __name__ == '__main__':
    strip_definitions_and_group_by_length('dictionary.json', 'sorted_dict.json')
