import json
from collections import Counter

def remix_word(word, length, sorted_dict_path='sorted_dict.json'):
    with open(sorted_dict_path, 'r') as file:
        word_dict = json.load(file)
    candidates = word_dict.get(str(length), [])
    target_count = Counter(word.lower())
    matches = [w for w in candidates if Counter(w.lower()) == target_count]

    return matches


def parse_phrase(phrase):
    # break the phrase into words around spaces
    remixed_phrase = []
    words = phrase.split()
    for word in words:
        length = len(word)
        remixed_word = remix_word(word, length)
        remixed_phrase.append(remixed_word)
    return remixed_phrase

def main():
    while True:    
        phrase = input("Enter the mixed phrase ('q' to quit): ")
        remixed_phrase = parse_phrase(phrase)
        print("Corrected phrase:", remixed_phrase)

if __name__ == '__main__':
    main()