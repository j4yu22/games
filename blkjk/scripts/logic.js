let balance = 100;
let displayed_bet = 0;
let shoe = [];
let game_state = {
    reshuffle: false,
    count: 0
};

// Update balance display
function update_balance() {
    document.getElementById('balance').textContent = balance;
}

// Update current bet display
function update_bet() {
    document.getElementById('current_bet').textContent = displayed_bet;
}

// Update chip counters
function update_counter(chip, value) {
    const counter = document.getElementById(`counter_${chip}`);
    const current_count = parseInt(counter.textContent);
    counter.textContent = current_count + value;
}

// Handle betting logic
function get_bet(bet, chip) {
    displayed_bet += bet;
    balance -= bet;
    update_balance();
    update_bet();
    update_counter(chip, bet > 0 ? 1 : -1);
}

// Event listeners for betting buttons
function betListener(buttonId, betValue, chip) {
    const button = document.getElementById(buttonId);
    button.addEventListener('click', () => {
        if (balance - betValue >= 0) {
            get_bet(betValue, chip);
        } else {
            console.log('Invalid bet: Balance would go negative');
        }
    });
    button.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        if (displayed_bet - betValue >= 0) {
            get_bet(-betValue, chip);
        } else {
            console.log('Invalid bet: Bet would go negative');
        }
    });
}

// Initialize betting listeners
betListener('bet_1', 1, 1);
betListener('bet_5', 5, 5);
betListener('bet_25', 25, 25);
betListener('bet_50', 50, 50);
betListener('bet_100', 100, 100);

// Confirm bet and move to next phase
document.getElementById('confirm_bet').addEventListener('click', confirm_bet);

function confirm_bet() {
    // Play animation of chips going to the current bet area
    // Get rid of all the get bet associated buttons
    // Reset all counters by chips
    document.querySelectorAll('.chip_counter').forEach(counter => counter.textContent = '0');
    // Move to segment 2 (deal cards, bring up options menu, etc)
    dealInitialCards();
}

// Create a deck of 52 cards
function createDeck() {
    const suits = ['♠', '♣', '♦', '♥'];
    const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
    const deck = [];
    for (const suit of suits) {
        for (const rank of ranks) {
            deck.push({ suit, rank });
        }
    }
    return deck;
}

// Create and shuffle the shoe
function createShoe(numDecks = 3) {
    shoe = [];
    for (let i = 0; i < numDecks; i++) {
        shoe = shoe.concat(createDeck());
    }
    shuffleDeck();
    const reshuffleMarkerPosition = shoe.length - Math.floor(Math.random() * (135 - 125 + 1)) - 125;
    shoe.splice(reshuffleMarkerPosition, 0, { suit: 'R', rank: 'Marker' });
    game_state.reshuffle = false;
    console.log("New Shoe!");
}

// Shuffle the deck
function shuffleDeck() {
    for (let i = shoe.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shoe[i], shoe[j]] = [shoe[j], shoe[i]];
    }
}

// Draw a card from the shoe
function drawCard() {
    if (shoe.length === 0) {
        console.log("The deck is empty...");
        return null;
    }
    let card = shoe.pop();
    if (card.suit === 'R' && card.rank === 'Marker') {
        game_state.reshuffle = true;
        if (shoe.length > 0) {
            card = shoe.pop();
        }
    }
    const value = cardEval(card);
    if (value < 7) {
        game_state.count += 1;
    } else if (value > 9) {
        game_state.count -= 1;
    }
    return card;
}

// Evaluate the card value
function cardEval(card) {
    const rank = card.rank;
    if (['J', 'Q', 'K'].includes(rank)) {
        return 10;
    } else if (rank === 'A') {
        return 11;
    } else {
        return parseInt(rank);
    }
}

// Deal initial cards
function dealInitialCards() {
    const playerCards = [drawCard(), drawCard()];
    const dealerCards = [drawCard(), drawCard()];

    updateHand('player_hand', playerCards);
    updateHand('dealer_hand', dealerCards, true);
}

// Update hand display
function updateHand(handId, cards, hideFirstCard = false) {
    const handElement = document.getElementById(handId);
    handElement.innerHTML = '';
    cards.forEach((card, index) => {
        const cardElement = document.createElement('li');
        cardElement.className = 'card';
        if (hideFirstCard && index === 0) {
            //TEMP: make sure you fix the width part and include it in the css when you get to that
            cardElement.innerHTML = `<img src="images/facedown_card.jpg" alt="Hidden Card" width=100px>`;
        } else {
            //TEMP: make sure you fix the width part and include it in the css when you get to that
            cardElement.innerHTML = `<img src="images/${card.suit}${card.rank}.png" alt="${card.suit}${card.rank}" width=100px>`;
        }
        handElement.appendChild(cardElement);
    });
}

// Initialize the game
createShoe();
document.getElementById('hit').addEventListener('click', player_hit);

function player_hit() {
    // Placeholder function to append a new card to the player's hand
    const playerHand = document.getElementById('player_hand_ul');
    const newCard = document.createElement('li');
    newCard.classList.add('card');
    newCard.innerHTML = '<img src="images/placeholder.png" alt="New Card">';
    playerHand.appendChild(newCard);
}
