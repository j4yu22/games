#bugs: when bot gets blackjack, it loses for the player

import random
import time
import math

#game_state dictionary:
game_state = {
    'balance': 100,
    'reshuffle': False,
    'hand_count': 0,
    'split_count' : 0,
    'bot_split_count' : 0,
    'quit' : None,
    'count': 0,
    'bot_balance': 100
}

def create_deck():
    """
    Generate a standard 52-card deck using symbols for suits.

    Returns:
        deck (list of tuples): The deck, with each card as a tuple (rank, suit symbol).
    """
    suits = ['♠', '♣', '♦', '♥']  # Suit symbols
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [(suit, rank) for suit in suits for rank in ranks]
    return deck


def create_shoe(num_decks=6):
    """
    Generate a multi-deck by using the create_deck() function 'num_decks' times, 
    shuffle it, and insert a reshuffle marker card near the end.

    Parameters:
        num_decks (int): Number of standard decks to include.

    Returns:
        shoe (list of tuples): The multi-deck with a reshuffle marker card.
    """
    shoe = []
    for _ in range(num_decks):
        shoe.extend(create_deck())
    random.shuffle(shoe)   
    reshuffle_marker_position = len(shoe) - random.randint(275, 285)
    shoe.insert(reshuffle_marker_position, ('R', 'Marker'))
    game_state['reshuffle'] = False
    print("New Shoe!")
    return shoe


def draw_card(shoe):
    """
    Draw a card from the given deck, removing it from the deck. If the reshuffle marker card is drawn,
    set a flag for reshuffle and draw another card.

    Parameters:
        deck (list of tuples): The deck to draw a card from.
        reshuffle_needed (list): A single-item list used as a flag to indicate reshuffle status. It's used as a list to allow modification within the function.

    Returns:
        tuple: The drawn card (suit, rank).
    """
    if not shoe:
        print("The deck is empty...")
        return None
    card = shoe.pop()
    if card == ('R', 'Marker'):
        game_state['reshuffle'] = True
        if shoe:
            card = shoe.pop()
    value = card_eval(card)
    if value < 7:
        game_state['count'] += 1
    elif value > 9:
        game_state['count'] -= 1

    return card


def format_card(card):
    """
    Format a card tuple into a string representation.

    Parameters:
        card (tuple): The card to format, represented as (suit, rank).

    Returns:
        str: The formatted card string.
    """
    if card:
        return f"{card[0]}{card[1]}"
    return "No card"


def card_eval(card):
    """
    Determine the value of a single card in Blackjack.

    Parameters:
        card (tuple): The card, represented as (suit, rank).

    Returns:
        int: The value of the card.
    """
    rank = card[1]
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11  # Assign 11 points to Aces initially
    else:
        return int(rank)


def hand_eval(hand):
    """
    Calculate the total value of a hand in Blackjack, adjusting for Aces as needed.

    Parameters:
        hand (list of tuples): The hand to evaluate, with each card represented as (suit, rank).

    Returns:
        int: The total value of the hand, adjusted for Aces.
    """
    try:
        points = 0
        aces = 0 

        for card in hand:
            value = card_eval(card)
            points += value
            if card[1] == 'A':
                aces += 1

        while points > 21 and aces:
            points -= 10
            aces -= 1

        return points
    except:
        return '?'


def get_bet(game_state, player_hand):
    """
    Prompt the player to input a bet amount, ensuring it's within their available balance.
    Updates the game state with the current bet and the amount at stake.

    Parameters:
        game_state (dict): A dictionary containing game-related information, including the player's balance.

    """
    while True:
        try:
            bet = int(input("\nEnter your bet amount: $"))
            if 0 < bet <= game_state['balance']:
                player_hand['Player']['bet'] = bet
                game_state['balance'] -= bet
                return
            elif bet == 0:
                game_state['quit'] = True
                return
            else:
                print(f"Invalid bet. Please enter a value between 1 and {game_state['balance']}.")
        except ValueError:
            print("Invalid input. Please enter an integer value.")


def get_bot_bet(game_state, bot_hand, true_count):
    while True:
        try:
            if 2 < true_count < 6:
                proposed_bet = true_count * 10
                bot_bet = min(proposed_bet, game_state['bot_balance'])
            elif true_count > 6:
                bot_bet = min(60, game_state['bot_balance'])
            else:
                bot_bet = min(1, game_state['bot_balance'])

            bot_bet = math.floor(bot_bet)  # Ensure bet is an integer

            if bot_bet > 0:
                bot_hand['Bot']['bet'] = bot_bet
                game_state['bot_balance'] -= bot_bet
                print(f"Bot bets ${bot_bet}")
                return
            else:
                return
        except ValueError:
            print("Bot Borken.")


def display_hand(hand):
    """
    Display a hand of cards, formatted, followed by the total points of the hand.

    Parameters:
        hand_name (str): A label for the hand (e.g., "Dealer's Hand" or "Your Hand").
        hand (list of tuples): The hand to display, with each card represented as (suit, rank).

    Returns:
        None
    """
    formatted_hand = ' '.join([f"|{card[0]}{card[1]}|" for card in hand])
    points = hand_eval(hand)

    output = f"{formatted_hand} TOTAL: {points}"
    return output


def check_blkjk(player_hand, dealer_hand):
    player_b = False
    dealer_b = False
    if hand_eval(player_hand['Player']['cards']) == 21:
        player_b = True
    if hand_eval(dealer_hand) == 21:
        dealer_b = True
    if player_b and not dealer_b:
        return 1
    elif player_b and dealer_b:
        return 2
    elif dealer_b and not player_b:
        return 3
    else:
        return None
    

def check_bot_blkjk(bot_hand, dealer_hand):
    player_b = False
    dealer_b = False
    if hand_eval(bot_hand['Bot']['cards']) == 21:
        player_b = True
    if hand_eval(dealer_hand) == 21:
        dealer_b = True
    if player_b and not dealer_b:
        return 1
    elif player_b and dealer_b:
        return 2
    elif dealer_b and not player_b:
        return 3
    else:
        return None


def bot_surrender(bot_hand):
    if hand_eval(bot_hand['Bot']['cards']) == 15 or hand_eval(bot_hand['Bot']['cards']) == 16:
        return 'y'

    else:
        return 'n'


def insurance(player_hand, dealer_hand, checks):
    if card_eval(dealer_hand[0]) == 11: #only an option if dealer shows an Ace
        print(f"Dealer's Hand: {display_hand([dealer_hand[0], ('', '?')])}")
        print(f"Player Hand: {display_hand(player_hand['Player']['cards'])}\n")
        while True:    
            surrender = input("Surrender? (Y/N) ")
            print('\n')  
            if surrender.lower() == 'y':
                surrender = True
                break
            elif surrender.lower() == 'n':
                surrender = False
                break
            else:
                print("Invalid input. Enter Y or N.")
        
        if surrender == True and checks == 3:
            print('Good call.')
            game_state['balance'] += player_hand['Player']['bet'] / 2
            return True
        if surrender == True and checks != 3:
            print("Little baby got scared.")
            game_state['balance'] += player_hand['Player']['bet'] / 2
            return True
        if surrender == False and checks == 3:
            print(r"""
                _________
                |/      |
                |      (_)
                |      \|/
                |       |
                |      / \
                |
             ___|___
            """)
            print("Your turn.")
            return True
        else:
            return None


def bot_insurance(bot_hand, dealer_hand, checks):
    if card_eval(dealer_hand[0]) == 11: #only an option if dealer shows an Ace
        print(f"Dealer's Hand: {display_hand([dealer_hand[0], ('', '?')])}")
        print(f"Bot Hand: {display_hand(bot_hand['Bot']['cards'])}\n")
        while True:    
            surrender = bot_surrender(bot_hand)
            print('\n')  
            if surrender.lower() == 'y':
                surrender = True
                break
            elif surrender.lower() == 'n':
                surrender = False
                break
            else:
                print("Invalid input. Enter Y or N.")
        
        if surrender == True and checks == 3:
            print('Bot made a good call.')
            game_state['balance'] += bot_hand['Bot']['bet'] / 2
            return True
        if surrender == True and checks != 3:
            print("Bot got scared.")
            game_state['balance'] += bot_hand['Bot']['bet'] / 2
            return True
        if surrender == False and checks == 3:
            return True
        else:
            return None


def bot_logic(game_state, bot_hand, dealer_hand, bot_key, first_turn):
    """
    Decide the bot's action based on its simple rules.

    Parameters:
        game_state (dict): A dictionary containing the current state of the game.

    Returns:
        str: The action the bot should take ('h' for hit, 's' for stand, 'd' for double down, 'sp' for split).
    """
    bots_hand = bot_hand[bot_key]['cards']
    dealer_card = dealer_hand[0]
    dealer_value = int(dealer_card[1]) if dealer_card[1].isnumeric() else 10 if dealer_card[1] in ['J', 'Q', 'K'] else 11
    player_total = hand_eval(bots_hand)
    is_soft = 'A' in [card[1] for card in bots_hand] and player_total <= 11
    is_pair = len(bots_hand) == 2 and bots_hand[0][1] == bots_hand[1][1]
    special_cheat_sheet = {
        ('A',2): ["H", "D/H", "D/H", "D/H", "D/H", "H", "H", "H", "H", "H"],
        ('A',3): ["H", "D/H", "D/H", "D/H", "D/H", "H", "H", "H", "H", "H"],
        ('A',4): ["H", "D/H", "D/H", "D/H", "D/H", "H", "H", "H", "H", "H"],
        ('A',5): ["H", "D/H", "D/H", "D/H", "D/H", "H", "H", "H", "H", "H"],
        ('A',6): ["H", "D/H", "D/H", "D/H", "D/H", "H", "S", "S", "H", "H"],
        ('A',7): ["S", "D/S", "D/S", "D/S", "D/S", "S", "S", "H", "H", "H"],
        ('A',8): ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
        ('A',9): ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
        (2,2): ["P/H", "P/H", "P/H", "P", "P", "H", "H", "H", "H", "H"],
        (3,3): ["P/H", "P/H", "P/H", "P", "P", "H", "H", "H", "H", "H"],
        (4,4): ["H", "H", "H", "P/H", "P/H", "H", "H", "H", "H", "H"],
        (5,5): ["D/H", "D/H", "D/H", "D/H", "D/H", "D/H", "D/H", "D/H", "H", "H"],
        (6,6): ["P/H", "P/H", "P", "P", "P", "H", "H", "H", "H", "H"],
        (7,7): ["P", "P", "P", "P", "P", "P", "H", "H", "H", "H"],
        (8,8): ["P", "P", "P", "P", "P", "P", "P", "P", "P", "P"],
        (9,9): ["P", "P", "P", "P", "P", "S", "P", "P", "S", "S"],
        (10,10): ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
        ('A','A'): ["P", "P", "P", "P", "P", "P", "P", "P", "P", "P"],
    }

    general_cheat_sheet = {
        (5): ["H"] * 10,
        (6): ["H"] * 10,
        (7): ["H"] * 10,
        (8): ["H"] * 10,
        (9): ["H", "D/H", "D/H", "D/H", "D/H", "H", "H", "H", "H", "H"],
        (10): ["D/H"] * 8 + ["H"] + ["H"],
        (11): ["D/H"] * 10,
        (12): ["H", "H", "S", "S", "S", "H", "H", "H", "H", "H"],
        (13): ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
        (14): ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
        (15): ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
        (16): ["S", "S", "S", "S", "S", "H", "H", "H", "H", "H"],
        (17): ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
        (18): ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
        (19): ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
        (20): ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
        (21): ["S", "S", "S", "S", "S", "S", "S", "S", "S", "S"],
    }

    # Make decision based on cheat sheets
    decision = None
    if is_pair:
        pair_value = bots_hand[0][1]  # Assuming both cards in the pair have the same value
        decision = special_cheat_sheet.get(('A', pair_value) if pair_value == 'A' else (int(pair_value), int(pair_value)), ["H"] * 10)[dealer_value - 2]
    elif is_soft:
        decision = special_cheat_sheet.get(('A', player_total - 11), ["H"] * 10)[dealer_value - 2]
    else:
        decision = general_cheat_sheet.get(player_total, ["H"] * 10)[dealer_value - 2]

    # Parse the decision and apply context-specific logic
    if 'D' in decision and first_turn and game_state['balance'] >= bot_hand[bot_key]['bet'] * 2:
        return 'd'  # Double down if allowed and sufficient balance
    elif 'P' in decision and is_pair and game_state['balance'] >= bot_hand[bot_key]['bet']:
        return 'sp'  # Split if allowed and sufficient balance
    elif 'H' in decision:
        return 'h'  # Hit if 'H' is an option
    elif 'S' in decision:
        return 's'  # Stand if 'S' is an option
    else:
        return 'h'  # Default to hit if no other action is specified or valid
    

def bot_turn(shoe, player_hand, bot_hand, dealer_hand, game_state, first_turn=True):
    """
    Manage the player's turn, offering options to hit, stand, double down, or split if applicable.

    """
    if game_state['bot_split_count'] < 1:    
        print('\n---Bot Turn---')
    try:
        for bot_key in bot_hand:
            try:
                hand_number = int(bot_key.split(' ')[1])
                if hand_number < game_state['bot_split_count'] - 2:
                    continue
            except (IndexError, ValueError):
                if bot_key != 'Bot':
                    continue

            first_turn = True
            if bot_key != 'Bot':
                print(f'\n-{bot_key} Hand-')
            card1 = card_eval(bot_hand[bot_key]['cards'][0])
            card2 = card_eval(bot_hand[bot_key]['cards'][1])
            
            while True:
                options = "Hit (h) / Stand (s)"

                if first_turn and game_state['balance'] >= bot_hand[bot_key]['bet']:
                    options += " / Double Down (d)"

                if first_turn and card1 == card2 and game_state['balance'] >= bot_hand[bot_key]['bet']:
                    options += " / Split (sp)"

                if first_turn == True:
                    for key in player_hand:
                        print(f"{key} Hand: {display_hand(player_hand[key]['cards'])}")
                    print(f"Dealer's Hand: {display_hand([dealer_hand[0], ('', '?')])}")
                    print('')
                    print(f"{bot_key} Hand: {display_hand(bot_hand[bot_key]['cards'])}\n")

                if hand_eval(bot_hand[bot_key]['cards']) == 21:
                    break

                bot_choice = bot_logic(game_state, bot_hand, dealer_hand, bot_key, first_turn)
                time.sleep(0.5)

                if bot_choice == 'h':  # Hit
                    bot_hand[bot_key]['cards'].append(draw_card(shoe))
                    if hand_eval(bot_hand[bot_key]['cards']) > 21:  # Check for bust
                        first_turn = False
                        print(f"{display_hand(bot_hand[bot_key]['cards'])}")
                        #time.sleep(1)
                        print('Busted')
                        break
                    print(f"{display_hand(bot_hand[bot_key]['cards'])}")
                    first_turn = False

                elif bot_choice == 's':  # Stand
                    first_turn = False
                    break

                elif bot_choice == 'd' and first_turn:
                    if game_state['balance'] >= bot_hand[bot_key]['bet']:
                        game_state['balance'] -= bot_hand[bot_key]['bet']
                        bot_hand[bot_key]['bet'] += bot_hand[bot_key]['bet']
                        bot_hand[bot_key]['cards'].append(draw_card(shoe))
                        print(f"{display_hand(bot_hand[bot_key]['cards'])}")
                        if hand_eval(bot_hand[bot_key]['cards']) > 21:  # Check for bust
                            #time.sleep(1)
                            print('Busted')
                        first_turn = False
                        break
                    else:
                        print("Bot doesnt have enough balance to double down.")

                elif bot_choice == 'd' and not first_turn:
                    bot_hand[bot_key]['cards'].append(draw_card(shoe))
                    if hand_eval(bot_hand[bot_key]['cards']) > 21:  # Check for bust
                        first_turn = False
                        print(f"{display_hand(bot_hand[bot_key]['cards'])}")
                        #time.sleep(1)
                        print('Busted')
                        break
                    print(f"{display_hand(bot_hand[bot_key]['cards'])}")
                    first_turn = False       

                elif bot_choice == 'sp' and first_turn and card1 == card2 and game_state['balance'] >= bot_hand[key]['bet']: 
                    game_state['balance'] -= bot_hand[bot_key]['bet']
                    first_turn = False
                    hand1 = f"Bot {game_state['bot_split_count'] + 1}"
                    hand2 = f"Bot {game_state['bot_split_count'] + 2}"
                    game_state['bot_split_count'] += 2

                    bot_hand[hand1] = {'cards': [bot_hand[bot_key]['cards'][0], draw_card(shoe)], 'bet': bot_hand[key]['bet']}
                    bot_hand[hand2] = {'cards': [bot_hand[bot_key]['cards'][1], draw_card(shoe)], 'bet': bot_hand[key]['bet']}

                    del bot_hand[bot_key]
                    bot_turn(shoe, player_hand, bot_hand, dealer_hand, game_state)
                    break
                else:
                    print("Bot gave invalid input.")
    except Exception as e:
        pass


def player_turn(shoe, player_hand, bot_hand, dealer_hand, game_state, first_turn=True):
    """
    Manage the player's turn, offering options to hit, stand, double down, or split if applicable.

    """
    if game_state['split_count'] < 1:    
        print('\n---Player Turn---')
    try:
        for key in player_hand:
            try:
                hand_number = int(key.split(' ')[1])
                if hand_number < game_state['split_count'] - 2:
                    continue
            except (IndexError, ValueError):
                if key != 'Player':
                    continue

            first_turn = True
            if key != 'Player':
                print(f'\n-{key} Hand-')
            card1 = card_eval(player_hand[key]['cards'][0])
            card2 = card_eval(player_hand[key]['cards'][1])
            
            while True:
                options = "Hit (h) / Stand (s)"

                if first_turn and game_state['balance'] >= player_hand[key]['bet']:
                    options += " / Double Down (d)"

                if first_turn and card1 == card2 and game_state['balance'] >= player_hand[key]['bet']:
                    options += " / Split (sp)"

                if first_turn == True:
                    for bot_key in bot_hand:
                        print(f"{bot_key} Hand: {display_hand(bot_hand[bot_key]['cards'])}")
                    print(f"Dealer's Hand: {display_hand([dealer_hand[0], ('', '?')])}")
                    print('')
                    print(f"{key} Hand: {display_hand(player_hand[key]['cards'])}\n")

                if hand_eval(player_hand[key]['cards']) == 21:
                    break

                player_choice = input(f"{options} ").lower()
                time.sleep(0.5)

                if player_choice == 'h':  # Hit
                    player_hand[key]['cards'].append(draw_card(shoe))
                    if hand_eval(player_hand[key]['cards']) > 21:  # Check for bust
                        first_turn = False
                        print(f"{display_hand(player_hand[key]['cards'])}")
                        time.sleep(1)
                        print('Busted')
                        break
                    print(f"{display_hand(player_hand[key]['cards'])}")
                    first_turn = False

                elif player_choice == 's':  # Stand
                    first_turn = False
                    break

                elif player_choice == 'd' and first_turn:
                    if game_state['balance'] >= player_hand[key]['bet']:
                        game_state['balance'] -= player_hand[key]['bet']
                        player_hand[key]['bet'] += player_hand[key]['bet']
                        player_hand[key]['cards'].append(draw_card(shoe))
                        print(f"{display_hand(player_hand[key]['cards'])}")
                        if hand_eval(player_hand[key]['cards']) > 21:  # Check for bust
                            time.sleep(1)
                            print('Busted')
                        first_turn = False
                        break
                    else:
                        print("Not enough balance to double down.")

                elif player_choice == 'sp' and first_turn and card1 == card2 and game_state['balance'] >= player_hand[key]['bet']: 
                    game_state['balance'] -= player_hand[key]['bet']
                    first_turn = False
                    hand1 = f"Number {game_state['split_count'] + 1}"
                    hand2 = f"Number {game_state['split_count'] + 2}"
                    game_state['split_count'] += 2

                    player_hand[hand1] = {'cards': [player_hand[key]['cards'][0], draw_card(shoe)], 'bet': player_hand[key]['bet']}
                    player_hand[hand2] = {'cards': [player_hand[key]['cards'][1], draw_card(shoe)], 'bet': player_hand[key]['bet']}

                    del player_hand[key]
                    player_turn(shoe, player_hand, bot_hand, dealer_hand, game_state)
                    break
                else:
                    print("Invalid input.")
    except Exception as e:
        pass

def dealer_turn(shoe, dealer_hand, player_hand, bot_hand):
    """
    Manage the dealer's turn, following standard Blackjack rules.
    The dealer hits on 16 or below and stands on 17 or above.

    Parameters:
        shoe (list of tuples): The current shoe from which cards are drawn.
        dealer_hand (list of tuples): The dealer's current hand.

    Returns:
        list of tuples: The dealer's final hand after completing their turn.
    """
    print("\n---Dealer's Turn---")
    for key in player_hand:
        print(f"{key} Hand: {display_hand(player_hand[key]['cards'])}")
    for bot_key in bot_hand:
        print(f"{bot_key} Hand: {display_hand(bot_hand[bot_key]['cards'])}")
    print(f"\nDealer Hand: {display_hand(dealer_hand)}")
    while True:
        time.sleep(0.5)
        points = hand_eval(dealer_hand)
        if points < 17:
            dealer_hand.append(draw_card(shoe))
            print(f"Dealer hits: {display_hand(dealer_hand)}")
            points = hand_eval(dealer_hand)
            if points > 21:
                print(f"Dealer busted.")
                break
        else:
            print(f"Dealer stands.")
            break

    return dealer_hand


def total(player_hand, bot_hand, dealer_hand, game_state):
    """
    Compare each player hand to the dealer's hand and update the game state based on the results.
   
    Parameters:
        bot_hands (list of tuples): A list containing player hand(s).
        dealer_hand (list of tuples): The dealer's hand.
        game_state (dict): The current state of the game, including the balance and bet.

    Returns:
        None: The function modifies the game_state in place.
    """
    dealer_points = hand_eval(dealer_hand)
    x = 0
    print(f"\n---Final---")
    for bot_key in bot_hand:  # This loop will work for one or multiple player hands.
        bot_points = hand_eval(bot_hand[bot_key]['cards'])
        if x < 1:
            print(f"Dealer's Hand: {display_hand(dealer_hand)}\n")
            x += 1
        print(f"{bot_key} Hand: {display_hand(bot_hand[bot_key]['cards'])}")

        if int(bot_points) > 21:  # Player busts
            print("Bot loses.")
        elif dealer_points > 21 or bot_points > dealer_points:  # Dealer busts or player has higher points
            print("Bot wins.")
            game_state['bot_balance'] += bot_hand[bot_key]['bet'] * 2  # Double the bet and add to the balance
        elif bot_points == dealer_points:  # Push
            print("Bot gets push.")
            game_state['bot_balance'] += bot_hand[bot_key]['bet']  # Return the bet to the balance
        else:  # Dealer has higher points
            print("Bot loses.")

    for key in player_hand:  # This loop will work for one or multiple player hands.
        player_points = hand_eval(player_hand[key]['cards'])
        if x < 1:
            print(f"Dealer's Hand: {display_hand(dealer_hand)}")
            x += 1
        print(f"{key} Hand: {display_hand(player_hand[key]['cards'])}")

        if int(player_points) > 21:  # Player busts
            print("You lose.")
        elif dealer_points > 21 or player_points > dealer_points:  # Dealer busts or player has higher points
            print("You win.")
            game_state['balance'] += player_hand[key]['bet'] * 2  # Double the bet and add to the balance
        elif player_points == dealer_points:  # Push
            print("Its a push.")
            game_state['balance'] += player_hand[key]['bet']  # Return the bet to the balance
        else:  # Dealer has higher points
            print("You lose.")

    # Reset the bet after the round is completed
    for key in player_hand:    
        player_hand[key]['bet'] = 0
    for bot_key in bot_hand:
        bot_hand[bot_key]['bet'] = 0


def round():
    """
    Play a round of blackjack
    """
    rebuy_counter = 0
    bot_rebuy_counter = 0
    shoe = create_shoe()
    while True:
        bot_net = game_state['bot_balance'] - ((bot_rebuy_counter * 100) + 100)
        true_count = game_state['count'] / (len(shoe) / 50)
        if game_state['balance'] < 1:
            loss = 100 + rebuy_counter * 100
            while True:
                rebuy = input("You have no money. Take out a loan? (Y/N) ")
                if rebuy.lower() == 'y':
                    rebuy = True
                    break
                elif rebuy.lower() == 'n':
                    rebuy = False
                    break
                else:
                    print("Invalid input. Enter Y or N. ")

            if rebuy == True:
                game_state['balance'] = 100
                rebuy_counter += 1
                print("Good decision. Now you can make gazillions. ")

            else:
                print(f"You bought back in {rebuy_counter} times and lost a total of ${loss:.2f}. The bot is at ${bot_net:.2f} See you next week!")
                break
        
        if game_state['bot_balance'] < 1:
            game_state["bot_balance"] = 100
            bot_rebuy_counter += 1

        player_hand = {
            'Player': {
                'cards': [],
                'bet': 0,
            },
        }

        bot_hand = {
            'Bot': {
                'cards': [],
                'bet': 0,
            },
        }
        print(f"\nThe bot has ${game_state['bot_balance']:.2f}")
        print(f"You have ${game_state['balance']:.2f}")
        
        get_bet(game_state, player_hand)
        get_bot_bet(game_state, bot_hand, true_count)

        if game_state['quit'] == True:
            net = game_state['balance'] - (100 + rebuy_counter * 100)
            print(f"Quitter :(  Here's your net: ${net:.2f}, the bot is at ${bot_net:.2f} See you next week.")
            break

        player_hand['Player']['cards'] = [draw_card(shoe), draw_card(shoe)]
        bot_hand['Bot']['cards'] = [draw_card(shoe), draw_card(shoe)]
        dealer_hand = [draw_card(shoe), draw_card(shoe)]

        bot_checks = check_bot_blkjk(bot_hand, dealer_hand)
        checks = check_blkjk(player_hand, dealer_hand)

        if checks == 1:
            for key in player_hand:
                print(f"{key} Hand: {display_hand(player_hand[key]['cards'])}")
            print(f"Dealer Hand: {display_hand(dealer_hand)}")
            print('You got Blackjack!!!')
            game_state['balance'] += player_hand['Player']['bet'] * 1.5 + player_hand['Player']['bet']
            continue
        elif checks == 2:
            for key in player_hand:
                print(f"{key} Hand: {display_hand(player_hand[key]['cards'])}")
            print(f"\nDealer Hand: {display_hand(dealer_hand)}")
            print('Yikes...')
            game_state['balance'] += player_hand['Player']['bet']
            continue

        if bot_checks == 1:
            for bot_key in bot_hand:
                print(f"{bot_key} Hand: {display_hand(bot_hand[bot_key]['cards'])}")
            print(f"Dealer Hand: {display_hand(dealer_hand)}")
            print('Bot got Blackjack!')
            game_state['bot_balance'] += bot_hand['Bot']['bet'] * 1.5 + bot_hand['Bot']['bet']
            continue
        elif bot_checks == 2:
            for bot_key in bot_hand:
                print(f"{bot_key} Hand: {display_hand(bot_hand[bot_key]['cards'])}")
            print(f"\nDealer Hand: {display_hand(dealer_hand)}")
            print('Oof...')
            game_state['bot_balance'] += bot_hand['Bot']['bet']
            continue
        
        fold = insurance(player_hand, dealer_hand, checks)
        bot_fold = bot_insurance(bot_hand, dealer_hand, bot_checks)
        if fold != True:
            player_turn(shoe, player_hand, bot_hand, dealer_hand, game_state)
        if bot_fold != True:
            bot_turn(shoe, player_hand, bot_hand, dealer_hand, game_state)
        busted = True
        for key in player_hand:
            if hand_eval(player_hand[key]['cards']) <= 21:
                busted = False

        for bot_key in bot_hand:
            if hand_eval(bot_hand[bot_key]['cards']) <= 21:
                busted = False
        if busted == False:
            dealer_hand = dealer_turn(shoe, dealer_hand, player_hand, bot_hand)

        total(player_hand, bot_hand, dealer_hand, game_state)
        #count logic
        print(f"Running count: {game_state['count']}")
        print(f"True count: {true_count:.0f}")
        #resets
        game_state['split_count'] = 0
        game_state['bot_split_count'] = 0
        if game_state['reshuffle'] == True:
            shoe = create_shoe()
            game_state['count'] = 0
            game_state['reshuffle'] == False

    #time.sleep(5)
def main():
    round()

if __name__ == "__main__":
    main()