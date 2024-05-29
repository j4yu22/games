let balance = 100;
let displayed_bet = 0;
let shoe = [];
let game_state = {
    reshuffle: false,
    count: 0
};
let dealerHiddenCard = null; // Store the hidden card's value
let hiddenDealerCard = true; // Flag to manage the display state
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
    // Hide chip buttons and confirm bet button
    document.getElementById('chip_buttons').classList.add('hidden');

    // Show dealer hand, player hand, and options
    document.getElementById('dealer_hand').classList.remove('hidden');
    document.getElementById('player_hand').classList.remove('hidden');
    document.getElementById('options').classList.remove('hidden');

    // Play animation of chips going to the current bet area
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

// Evaluate the total value of a hand
function handEval(hand) {
    let total = 0;
    let aces = 0;

    hand.forEach(card => {
        const value = cardEval(card);
        total += value;
        if (card.rank === 'A') {
            aces += 1;
        }
    });

    while (total > 21 && aces > 0) {
        total -= 10;
        aces -= 1;
    }

    return total;
}

function logHandTotals() {
    const playerCards = document.querySelectorAll('#player_hand_ul .card img');
    const dealerCards = document.querySelectorAll('#dealer_hand .card img');

    const playerHand = Array.from(playerCards).map(cardImg => {
        const altText = cardImg.alt;
        const suit = altText.slice(0, 1);
        const rank = altText.slice(1);
        return { suit, rank };
    });

    const dealerHand = Array.from(dealerCards).map(cardImg => {
        const altText = cardImg.alt;
        if (altText === "Hidden Card") {
            return { suit: 'H', rank: 'i' }; // Placeholder to prevent splitting error
        }
        const suit = altText.slice(0, 1);
        const rank = altText.slice(1);
        return { suit, rank };
    });

    const playerTotal = handEval(playerHand);
    const dealerTotal = handEval(dealerHand);

    console.log(`Player Total: ${playerTotal}`);
    console.log(`Dealer Total: ${dealerTotal}`);
}

function dealInitialCards() {
    const playerCards = [drawCard(), drawCard()];
    const dealerCards = [drawCard(), drawCard()];

    dealerHiddenCard = dealerCards[0]; // Store the actual value of the hidden card

    updateHand('player_hand_ul', playerCards);
    updateHand('dealer_hand', dealerCards, hiddenDealerCard);
}

function updateHand(handId, cards, hideFirstCard = false) {
    const handElement = document.getElementById(handId);
    handElement.innerHTML = '';
    cards.forEach((card, index) => {
        const cardElement = document.createElement('li');
        cardElement.className = 'card';
        if (hideFirstCard && index === 0) {
            cardElement.innerHTML = `<img src="images/facedown_card.jpg" alt="Hidden Card" width=100px>`;
        } else {
            cardElement.innerHTML = `<img src="images/${card.suit}${card.rank}.png" alt="${card.suit}${card.rank}" width=100px>`;
        }
        handElement.appendChild(cardElement);
    });
    logHandTotals();
}


// Initialize the game
createShoe();

function hit() {
    const playerHandUl = document.getElementById('player_hand_ul');
    const newCard = drawCard();
    const newCardElement = document.createElement('li');
    newCardElement.className = 'card';
    newCardElement.innerHTML = `<img src="images/${newCard.suit}${newCard.rank}.png" alt="${newCard.suit}${newCard.rank}" width=100px>`;
    playerHandUl.appendChild(newCardElement);
    console.log("Player hit.");
    logHandTotals();

    const playerCards = Array.from(playerHandUl.querySelectorAll('.card img')).map(cardImg => {
        const suit = cardImg.alt.slice(0, 1);
        const rank = cardImg.alt.slice(1);
        return { suit, rank };
    });

    if (handEval(playerCards) > 21) {
        console.log("Player busted.");
        document.getElementById('options').classList.add('hidden');
        revealDealerCard();
        // Add any additional logic for handling player bust (e.g., updating balance)
    }
}

function stand() {
    document.getElementById('options').classList.add('hidden');
    revealDealerCard();
    logHandTotals();
    console.log("Player stood.");
}

function double_down() {
    if (balance >= displayed_bet && !document.getElementById('options').classList.contains('hidden')) {
        balance -= displayed_bet;
        displayed_bet *= 2;
        update_balance();
        update_bet();
        hit();
        document.getElementById('options').classList.add('hidden');
        dealerTurn();
        logHandTotals();
        console.log("Player doubled down.");
    } else {
        console.log("Not enough balance to double down or already acted.");
    }
}

function dealerTurn() {
    const dealerHandUl = document.getElementById('dealer_hand');

    // Reveal hidden dealer card
    if (hiddenDealerCard) {
        hiddenDealerCard = false;
        const hiddenCardElement = dealerHandUl.querySelector('.card img[alt="Hidden Card"]');
        if (hiddenCardElement && dealerHiddenCard) {
            hiddenCardElement.src = `images/${dealerHiddenCard.suit}${dealerHiddenCard.rank}.png`;
            hiddenCardElement.alt = `${dealerHiddenCard.suit}${dealerHiddenCard.rank}`;
        } else {
            console.error("Hidden card element or dealerHiddenCard is not properly set.");
        }
    }

    let dealerCards = Array.from(dealerHandUl.querySelectorAll('.card img')).map(cardImg => {
        const [suit, rank] = cardImg.alt.split('');
        return { suit, rank };
    });

    logHandTotals();

    while (handEval(dealerCards) < 17) {
        const newCard = drawCard();
        const newCardElement = document.createElement('li');
        newCardElement.className = 'card';
        newCardElement.innerHTML = `<img src="images/${newCard.suit}${newCard.rank}.png" alt="${newCard.suit}${newCard.rank}" width=100px>`;
        dealerHandUl.appendChild(newCardElement);
        dealerCards.push(newCard);
        logHandTotals();
    }
}

function revealDealerCard() {
    const dealerHandUl = document.getElementById('dealer_hand');

    if (hiddenDealerCard) {
        hiddenDealerCard = false;
        const hiddenCardElement = dealerHandUl.querySelector('.card img[alt="Hidden Card"]');
        if (hiddenCardElement && dealerHiddenCard) {
            hiddenCardElement.src = `images/${dealerHiddenCard.suit}${dealerHiddenCard.rank}.png`;
            hiddenCardElement.alt = `${dealerHiddenCard.suit}${dealerHiddenCard.rank}`;
        } else {
            console.error("Hidden card element or dealerHiddenCard is not properly set.");
        }
    }
}



// Add event listener for the option buttons
document.getElementById('hit').addEventListener('click', hit);
document.getElementById('stand').addEventListener('click', stand);
document.getElementById('double_down').addEventListener('click', double_down);
