let balance = parseFloat(localStorage.getItem('balance')) || 100;
let displayed_bet = parseFloat(localStorage.getItem('displayed_bet')) || 0;
let buyInCount = parseInt(localStorage.getItem('buyInCount')) || 0;
let shoe = [];
let game_state = {
    reshuffle: false,
    count: 0
};
let dealerHiddenCard = null; // Store the hidden card's value
let hiddenDealerCard = true; // Flag to manage the display state
let firstTurn = true; // Flag to manage first turn

function saveGameState() {
    localStorage.setItem('balance', balance);
    localStorage.setItem('displayed_bet', displayed_bet);
    localStorage.setItem('buyInCount', buyInCount);
}

function sleep(seconds) {
    return new Promise(resolve => setTimeout(resolve, seconds * 1000));
}
// Update balance display
function update_balance() {
    document.getElementById('balance').textContent = balance;
    saveGameState();
}

// Update current bet display
function update_bet() {
    document.getElementById('current_bet').textContent = displayed_bet;
    saveGameState();
}

update_balance();
update_bet();

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
    firstTurn = true;
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
betListener('bet_10', 10, 10);
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
    firstTurn = true; // Reset the first turn flag
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
        createShoe(); // Reshuffle the shoe when it's empty
    }
    let card = shoe.pop();
    if (card.suit === 'R' && card.rank === 'Marker') {
        game_state.reshuffle = true;
        console.log("Reshuffle marker hit!");
        createShoe(); // Reshuffle the shoe when reshuffle marker is hit
        card = shoe.pop(); // Draw a new card after reshuffling
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
    const dealerCards = document.querySelectorAll('#dealer_hand ul .card img');

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
    const dealerTotal = handEval(dealerHand.filter(card => card.rank !== 'i')); // Exclude placeholder card

    console.log(`Player Total: ${playerTotal}`);
    console.log(`Dealer Total: ${dealerTotal}`);
}

function revealDealerCard() {
    const dealerHandUl = document.getElementById('dealer_hand_ul');

    if (hiddenDealerCard && dealerHiddenCard) {
        hiddenDealerCard = false;
        const hiddenCardElement = dealerHandUl.querySelector('.card img[alt="Hidden Card"]');
        if (hiddenCardElement) {
            hiddenCardElement.src = `images/${dealerHiddenCard.suit}${dealerHiddenCard.rank}.png`;
            hiddenCardElement.alt = `${dealerHiddenCard.suit}${dealerHiddenCard.rank}`;
        } else {
            console.error("Hidden card element is not properly set.");
        }
    } else {
        console.error("Hidden card element or dealerHiddenCard is not properly set.");
    }
    logHandTotals(); // Log totals after revealing the hidden card
}

async function totals() {
    const playerHandUl = document.getElementById('player_hand_ul');
    const dealerHandUl = document.getElementById('dealer_hand_ul');

    const playerCards = Array.from(playerHandUl.querySelectorAll('.card img')).map(cardImg => {
        const suit = cardImg.alt.slice(0, 1);
        const rank = cardImg.alt.slice(1);
        return { suit, rank };
    });

    const dealerCards = Array.from(dealerHandUl.querySelectorAll('.card img')).map(cardImg => {
        const suit = cardImg.alt.slice(0, 1);
        const rank = cardImg.alt.slice(1);
        return { suit, rank };
    });

    const playerTotal = handEval(playerCards);
    const dealerTotal = handEval(dealerCards);

    console.log(`Final Player Total: ${playerTotal}`);
    console.log(`Final Dealer Total: ${dealerTotal}`);

    if (playerTotal > 21) {
        console.log("Player busts. Dealer wins.");
        displayed_bet = 0; // Player loses bet
    } else if (dealerTotal > 21) {
        console.log("Dealer busts. Player wins.");
        balance += Math.ceil(displayed_bet * 2); // Player wins twice the current bet
        displayed_bet = 0;
    } else if (playerTotal > dealerTotal) {
        console.log("Player wins.");
        balance += Math.ceil(displayed_bet * 2); // Player wins twice the current bet
        displayed_bet = 0;
    } else if (playerTotal < dealerTotal) {
        console.log("Dealer wins.");
        displayed_bet = 0; // Player loses bet
    } else {
        console.log("It's a push.");
        balance += displayed_bet; // Player gets back the bet
        displayed_bet = 0;
    }

    update_balance();
    update_bet();
    await sleep(2);

    await buyIn(); // Call the buyIn function here if the balance is 0

    // Reset the game for the next round
    resetGame();
}

async function buyIn() {
    if (balance === 0) {
        buyInCount += 1;
        alert("Your balance is 0. You are buying back in for 100.");
        balance = 100;
        update_balance();
        console.log(`Player bought in. Total buy-ins: ${buyInCount}`);
    }
}


function confirm_bet() {
    if (displayed_bet === 0) {
        console.log("Cannot confirm bet. Bet amount is zero.");
        return; // Exit the function if the bet amount is zero
    }
    update_bet();
    update_balance();

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
    firstTurn = true; // Reset the first turn flag
}

async function dealInitialCards() {
    const playerCards = [drawCard(), drawCard()];
    const dealerCards = [drawCard(), drawCard()];

    dealerHiddenCard = dealerCards[0]; // Store the actual value of the hidden card

    updateHand('player_hand_ul', playerCards);
    updateHand('dealer_hand_ul', dealerCards, hiddenDealerCard);

    firstTurn = true; // Set firstTurn to true at the start of a new round
    updateOptions(); // Update options to reflect the reset state

    // Check for 21 immediately after dealing cards
    const playerTotal = handEval(playerCards);
    const dealerTotal = handEval([dealerCards[0], dealerCards[1]]); // Including hidden card for calculation

    if (playerTotal === 21 || dealerTotal === 21) {
        document.getElementById('options').classList.add('hidden');
        if (dealerTotal === 21 && playerTotal === 21) {
            console.log("Both player and dealer have 21. It's a push.");
            balance += displayed_bet; // Player gets back the bet
            displayed_bet = 0;
        } else if (dealerTotal === 21) {
            console.log("Dealer has 21. Player loses.");
            displayed_bet = 0; // Player loses bet
            revealDealerCard();
        } else if (playerTotal === 21) {
            console.log("Player has 21. Player wins.");
            await sleep(2);
            balance += Math.ceil(displayed_bet * 2.5);  // Player wins 2.5 times the current bet
            displayed_bet = 0;
        }
        update_balance();
        update_bet();
        await sleep(2);
        resetGame();
    }
}


function updateHand(handId, cards, hideFirstCard = false) {
    const handElement = document.getElementById(handId);
    handElement.innerHTML = '';
    cards.forEach((card, index) => {
        if (!card) {
            console.error("Invalid card detected:", card);
            return; // Skip invalid cards
        }
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

async function hit() {
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

    firstTurn = false; // It's no longer the first turn after the player hits
    updateOptions(); // Update options based on the first turn flag

    const playerTotal = handEval(playerCards);

    if (playerTotal > 21) {
        console.log("Player busted.");
        document.getElementById('options').classList.add('hidden');
        await sleep(2);
        revealDealerCard();
        totals();   
    } else if (playerTotal === 21) {
        console.log("Player has 21.");
        document.getElementById('options').classList.add('hidden');
        await sleep(2);
        dealerTurn();
    }
}

async function stand() {
    firstTurn = false; // It's no longer the first turn after the player stands
    updateOptions(); // Update options based on the first turn flag
    document.getElementById('options').classList.add('hidden');
    await sleep(2);
    revealDealerCard();
    logHandTotals();
    console.log("Player stood.");
    dealerTurn(); // Call dealerTurn after the player stands
}

async function double_down() {
    if (balance >= displayed_bet && !document.getElementById('options').classList.contains('hidden') && firstTurn) {
        balance -= displayed_bet;
        displayed_bet *= 2;
        update_balance();
        update_bet();
        firstTurn = false; // It's no longer the first turn after the player doubles down
        updateOptions(); // Update options based on the first turn flag
        await hit();
        document.getElementById('options').classList.add('hidden');
        await sleep(2);
        dealerTurn(); // Call dealer turn after the player doubles down and hits
    } else {
        console.log("Not enough balance to double down or already acted.");
    }
}

async function dealerTurn() {
    const dealerHandUl = document.getElementById('dealer_hand_ul');

    // Reveal hidden dealer card
    revealDealerCard();

    let dealerCards = Array.from(dealerHandUl.querySelectorAll('.card img')).map(cardImg => {
        const suit = cardImg.alt.slice(0, 1);
        const rank = cardImg.alt.slice(1);
        return { suit, rank };
    });

    // Exclude placeholder card
    dealerCards = dealerCards.filter(card => card.rank !== 'i');
    let dealerTotal = handEval(dealerCards);

    console.log(`Dealer initial total: ${dealerTotal}`);

    while (dealerTotal < 17) {
        const newCard = drawCard();
        const newCardElement = document.createElement('li');
        newCardElement.className = 'card';
        newCardElement.innerHTML = `<img src="images/${newCard.suit}${newCard.rank}.png" alt="${newCard.suit}${newCard.rank}" width=100px>`;
        dealerHandUl.appendChild(newCardElement);
        dealerCards.push(newCard);

        dealerTotal = handEval(dealerCards);
        console.log(`Dealer drew ${newCard.suit}${newCard.rank}, new total: ${dealerTotal}`);
        logHandTotals();
        await sleep(2);
    }

    if (dealerTotal >= 17) {
        console.log('Dealer stands.');
        await sleep(2);
    }

    totals(); // Call the totals function to determine the outcome
}


// Add event listener for the option buttons
document.getElementById('hit').addEventListener('click', hit);
document.getElementById('stand').addEventListener('click', stand);
document.getElementById('double_down').addEventListener('click', double_down);

function updateOptions() {
    const doubleDownButton = document.getElementById('double_down');
    if (firstTurn) {
        doubleDownButton.classList.remove('hidden');
    } else {
        doubleDownButton.classList.add('hidden');
    }
}

updateOptions(); // Initial call to set the options correctly

function resetGame() {
    // Clear player and dealer hands
    const playerHandUl = document.getElementById('player_hand_ul');
    const dealerHandUl = document.getElementById('dealer_hand_ul');
    playerHandUl.innerHTML = '';
    dealerHandUl.innerHTML = '';

    // Hide hands
    document.getElementById('dealer_hand').classList.add('hidden');
    document.getElementById('player_hand').classList.add('hidden');
    
    // Show betting buttons and confirm bet button
    document.getElementById('chip_buttons').classList.remove('hidden');
    document.getElementById('confirm_bet').classList.remove('hidden');

    // Reset other necessary game state variables
    displayed_bet = 0;
    update_bet();
    update_balance();

    // Reset first turn flag
    firstTurn = true;
    hiddenDealerCard = true;

    console.log("Game reset. Ready for next round.");
}


//keyboard shortcuts
document.addEventListener('keydown', (event) => {
    switch (event.key) {
        case '1':
            document.getElementById('bet_1').click();
            break;
        case '2':
            document.getElementById('bet_5').click();
            break;
        case '3':
            document.getElementById('bet_10').click();
            break;
        case '4':
            document.getElementById('bet_25').click();
            break;
        case '5':
            document.getElementById('bet_50').click();
            break;
        case '6':
            document.getElementById('bet_100').click();
            break;
        case 'Enter':
            if (!document.getElementById('chip_buttons').classList.contains('hidden')) {
                document.getElementById('confirm_bet').click();
            }
            break;
        case 'h':
            if (!document.getElementById('options').classList.contains('hidden')) {
                document.getElementById('hit').click();
            }
            break;
        case 's':
            if (!document.getElementById('options').classList.contains('hidden')) {
                document.getElementById('stand').click();
            }
            break;
        case 'd':
            if (!document.getElementById('options').classList.contains('hidden')) {
                document.getElementById('double_down').click();
            }
            break;
    }
});

document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('tips-button').addEventListener('click', () => {
        document.getElementById('tips_menu').classList.toggle('hidden');
    });

    document.getElementById('close_tips').addEventListener('click', () => {
        document.getElementById('tips_menu').classList.add('hidden');
    });
});
