import random
import time

def create_deck():
    suits = ['♠', '♣', '♦', '♥']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [(rank, suit) for suit in suits for rank in ranks]

def shuffle_deck(deck):
    random.shuffle(deck)

def draw_card(deck):
    return deck.pop()

def baccarat_hand_value(hand):
    total = sum(baccarat_card_value(card) for card in hand) % 10
    return total

def baccarat_card_value(card):
    rank, suit = card
    if rank in ['J', 'Q', 'K', '10']:
        return 0
    elif rank == 'A':
        return 1
    else:
        return int(rank)

def should_player_draw_third_card(player_hand):
    return baccarat_hand_value(player_hand) <= 5

def should_banker_draw_third_card(banker_hand, player_hand):
    banker_value = baccarat_hand_value(banker_hand)
    if banker_value >= 7:
        return False
    if banker_value <= 2:
        return True
    
    player_third_card_value = 0 if len(player_hand) < 3 else baccarat_card_value(player_hand[2])
    
    if banker_value == 3 and player_third_card_value != 8:
        return True
    elif banker_value == 4 and player_third_card_value in range(2, 8):
        return True
    elif banker_value == 5 and player_third_card_value in range(4, 8):
        return True
    elif banker_value == 6 and player_third_card_value in range(6, 8):
        return True
    return False

def format_card(card):
    return f"|{card[0]}{card[1]}|"

def format_hand(hand):
    return ' '.join(format_card(card) for card in hand)

def display_table(player_hand, banker_hand, game_state):
    player_cards = format_hand(player_hand)
    banker_cards = format_hand(banker_hand)
    player_bet = game_state['player_bet']
    banker_bet = game_state['banker_bet']
    tie_bet = game_state['tie_bet']

    # Formatting bets to only show if they're greater than 0
    p_bet = f'           ${player_bet:<13}|' if player_bet > 0 else '                         |'
    b_bet = f'           ${banker_bet:<7}' if banker_bet > 0 else '                  '
    t_bet = f'| Tie: ${tie_bet}' if tie_bet > 0 else ''

    # Calculating hand values
    player_value = baccarat_hand_value(player_hand)
    banker_value = baccarat_hand_value(banker_hand)

    table_format = f"""
    {'        Player':<24} | {'        Banker'}
    {player_cards:<16}SCORE: {player_value} | {banker_cards:<16}SCORE: {banker_value}
    {p_bet}{b_bet}{t_bet}
    """
    print(table_format)


def play_baccarat_round(deck, game_state):
    player_hand = [draw_card(deck), draw_card(deck)]
    banker_hand = [draw_card(deck), draw_card(deck)]
    
    display_table(player_hand, banker_hand, game_state)
    print('\n')
    # Player's turn to draw third card
    if should_player_draw_third_card(player_hand):
        player_hand.append(draw_card(deck))
    
    # Banker's turn to draw third card
    if should_banker_draw_third_card(banker_hand, player_hand):
        banker_hand.append(draw_card(deck))
    
    # Final value calculation
    player_final_value = baccarat_hand_value(player_hand)
    banker_final_value = baccarat_hand_value(banker_hand)

    time.sleep(2)
    display_table(player_hand, banker_hand, game_state)

    return player_final_value, banker_final_value

def get_bet(game_state):
    while True:
        bet_input = input("Place your bet: ").lower().replace(" ", "").split(",")
        valid_bet = True
        total_bet_amount = 0

        for bet in bet_input:
            if len(bet) < 2 or bet[0] not in ['p', 'b', 't'] or not bet[1:].isdigit():
                print("Invalid bet format. Try again.")
                valid_bet = False
                break

            bet_type, bet_amount = bet[0], int(bet[1:])
            total_bet_amount += bet_amount

            if total_bet_amount > game_state['balance']:
                print("Total bet amount exceeds your current balance. Try again.")
                valid_bet = False
                break

            if bet_type == 'p':
                game_state['player_bet'] += bet_amount
            elif bet_type == 'b':
                game_state['banker_bet'] += bet_amount
            elif bet_type == 't':
                game_state['tie_bet'] += bet_amount

        if valid_bet:
            game_state['balance'] -= total_bet_amount
            break

    
def total(game_state, player_final_value, banker_final_value):
    if player_final_value > banker_final_value:
        print("Player wins!")
        if game_state['player_bet']:
            game_state['balance'] += game_state['player_bet'] * 2
    elif player_final_value < banker_final_value:
        print("Banker wins!")
        if game_state['banker_bet']:
            game_state['balance'] += game_state['banker_bet'] * 2
    else:
        print("It's a tie!")
        if game_state['tie_bet']:
            game_state['balance'] += game_state['tie_bet'] * 9

def main():
    game_state = {
        'balance': 100,
        'player_bet': 0,
        'banker_bet': 0,
        'tie_bet': 0,
    }

    deck = create_deck()
    shuffle_deck(deck)

    while game_state['balance'] > 0:
        print(f"\nCurrent balance: ${game_state['balance']}")
        get_bet(game_state)
        player_final, banker_final = play_baccarat_round(deck, game_state)

        total(game_state, player_final, banker_final)
        # Check for reshuffle
        if len(deck) < 6:
            deck = create_deck()
            shuffle_deck(deck)
            print("Reshuffling deck...")

        # Reset bets after each round
        game_state['player_bet'] = 0
        game_state['banker_bet'] = 0
        game_state['tie_bet'] = 0

    print(f"Your final balance is: ${game_state['balance']}")

if __name__ == "__main__":
    main()