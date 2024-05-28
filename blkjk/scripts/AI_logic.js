// gameState object
const gameState = {
    balance: 100,
    reshuffle: false,
    handCount: 0,
    splitCount: 0,
    quit: false,
    count: 0
};

let playerHand = {};
let dealerHand = [];
let shoe = createShoe();
let currentPlayerAction = null;
const chipCounters = { 1: 0, 5: 0, 10: 0, 50: 0, 100: 0 };

// Utility function to log messages to the log area
function logMessage(message) {
    const logMessages = document.getElementById('log-messages');
    logMessages.innerHTML += `${message}\n`;
    logMessages.scrollTop = logMessages.scrollHeight;
}

function updateBalance() {
    document.getElementById('balance').textContent = `Balance: $${gameState.balance}`;
}

function updateCurrentBet() {
    const bet = playerHand['Player'] ? playerHand['Player'].bet : '-';
    document.getElementById('current-bet').textContent = `Current Bet: ${bet}`;
}

function updateHands() {
    const dealerCards = document.getElementById('dealer-cards');
    dealerCards.innerHTML = '';
    dealerHand.forEach(card => {
        dealerCards.innerHTML += `<div class="card">${formatCard(card)}</div>`;
    });

    const playerCards = document.getElementById('player-cards');
    playerCards.innerHTML = '';
    playerHand['Player'].cards.forEach(card => {
        playerCards.innerHTML += `<div class="card">${formatCard(card)}</div>`;
    });
}

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

function createShoe(numDecks = 3) {
    let shoe = [];
    for (let i = 0; i < numDecks; i++) {
        shoe = shoe.concat(createDeck());
    }
    shoe = shuffle(shoe);
    const reshuffleMarkerPosition = shoe.length - Math.floor(Math.random() * (135 - 125 + 1)) - 125;
    shoe.splice(reshuffleMarkerPosition, 0, { suit: 'R', rank: 'Marker' });
    gameState.reshuffle = false;
    logMessage("New Shoe!");
    return shoe;
}

function shuffle(deck) {
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
}

function drawCard(shoe) {
    if (shoe.length === 0) {
        logMessage("The deck is empty...");
        return null;
    }
    let card = shoe.pop();
    if (card.suit === 'R' && card.rank === 'Marker') {
        gameState.reshuffle = true;
        if (shoe.length > 0) {
            card = shoe.pop();
        }
    }
    const value = cardEval(card);
    if (value < 7) {
        gameState.count += 1;
    } else if (value > 9) {
        gameState.count -= 1;
    }
    return card;
}

function formatCard(card) {
    if (card) {
        return `${card.suit}${card.rank}`;
    }
    return "No card";
}

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

function handEval(hand) {
    try {
        let points = 0;
        let aces = 0;
        for (const card of hand) {
            const value = cardEval(card);
            points += value;
            if (card.rank === 'A') {
                aces += 1;
            }
        }
        while (points > 21 && aces > 0) {
            points -= 10;
            aces -= 1;
        }
        return points;
    } catch (error) {
        return '?';
    }
}

function incrementChip(value) {
    if (gameState.balance >= value) {
        gameState.balance -= value;
        chipCounters[value] += 1;
        document.getElementById(`chip-${value}`).textContent = chipCounters[value];
        updateBalance();
    } else {
        logMessage("Not enough balance.");
    }
}

function confirmBet() {
    let bet = 0;
    for (const value in chipCounters) {
        bet += value * chipCounters[value];
    }

    if (bet > 0) {
        playerHand['Player'] = { cards: [], bet };
        chipCounters[1] = 0;
        chipCounters[5] = 0;
        chipCounters[10] = 0;
        chipCounters[50] = 0;
        chipCounters[100] = 0;
        updateCurrentBet();
        startRound();
    } else {
        logMessage("Please place a bet.");
    }
}

function displayHand(hand) {
    const formattedHand = hand.map(card => `|${card.suit}${card.rank}|`).join(' ');
    const points = handEval(hand);
    const output = `${formattedHand} TOTAL: ${points}`;
    return output;
}

function checkBlkjk(playerHand, dealerHand) {
    let playerB = false;
    let dealerB = false;
    if (handEval(playerHand['Player']['cards']) === 21) {
        playerB = true;
    }
    if (handEval(dealerHand) === 21) {
        dealerB = true;
    }
    if (playerB && !dealerB) {
        return 1;
    } else if (playerB && dealerB) {
        return 2;
    } else if (dealerB && !playerB) {
        return 3;
    } else {
        return null;
    }
}

function playerTurn(shoe, playerHand, dealerHand, firstTurn = true) {
    if (gameState.splitCount < 1) {
        logMessage('---Player Turn---');
    }
    try {
        for (const key in playerHand) {
            if (playerHand.hasOwnProperty(key)) {
                const hand = playerHand[key];
                firstTurn = true;
                if (firstTurn) {
                    logMessage(`Dealer's Hand: ${displayHand([dealerHand[0], { suit: '', rank: '?' }])}`);
                    logMessage(`${key} Hand: ${displayHand(hand.cards)}\n`);
                }
                if (handEval(hand.cards) === 21) {
                    disableActionButtons();
                    setTimeout(() => {
                        dealerTurn(shoe, dealerHand, playerHand);
                        total(playerHand, dealerHand);
                        resetGame();
                    }, 1000);
                    break;
                }
                currentPlayerAction = key;
                enableActionButtons();
            }
        }
    } catch (error) {
        console.error(error);
    }
}

function hit() {
    const hand = playerHand[currentPlayerAction];
    hand.cards.push(drawCard(shoe));
    logMessage(`${displayHand(hand.cards)}`);
    if (handEval(hand.cards) > 21) {
        logMessage('Busted');
        disableActionButtons();
        setTimeout(() => {
            dealerTurn(shoe, dealerHand, playerHand);
            total(playerHand, dealerHand);
            resetGame();
        }, 1000);
    } else {
        updateHands();
        currentPlayerAction = null;
    }
}

function stand() {
    disableActionButtons();
    setTimeout(() => {
        dealerTurn(shoe, dealerHand, playerHand);
        total(playerHand, dealerHand);
        resetGame();
    }, 1000);
    currentPlayerAction = null;
}

function doubleDown() {
    const hand = playerHand[currentPlayerAction];
    if (gameState.balance >= hand.bet) {
        gameState.balance -= hand.bet;
        hand.bet += hand.bet;
        hand.cards.push(drawCard(shoe));
        logMessage(`${displayHand(hand.cards)}`);
        if (handEval(hand.cards) > 21) {
            logMessage('Busted');
        }
        updateBalance();
        updateHands();
        disableActionButtons();
        setTimeout(() => {
            dealerTurn(shoe, dealerHand, playerHand);
            total(playerHand, dealerHand);
            resetGame();
        }, 1000);
        currentPlayerAction = null;
    } else {
        logMessage("Not enough balance to double down.");
    }
}

function split() {
    const hand = playerHand[currentPlayerAction];
    if (gameState.balance >= hand.bet && hand.cards[0].rank === hand.cards[1].rank) {
        gameState.balance -= hand.bet;
        const hand1 = `Number ${gameState.splitCount + 1}`;
        const hand2 = `Number ${gameState.splitCount + 2}`;
        gameState.splitCount += 2;
        playerHand[hand1] = { cards: [hand.cards[0], drawCard(shoe)], bet: hand.bet };
        playerHand[hand2] = { cards: [hand.cards[1], drawCard(shoe)], bet: hand.bet };
        delete playerHand[currentPlayerAction];
        logMessage(`Split hands: ${hand1} and ${hand2}`);
        updateBalance();
        updateHands();
        disableActionButtons();
        playerTurn(shoe, playerHand, dealerHand);
    } else {
        logMessage("Invalid split attempt.");
    }
}

function enableActionButtons() {
    document.querySelector('#actions button[onclick="hit()"]').disabled = false;
    document.querySelector('#actions button[onclick="stand()"]').disabled = false;
    document.querySelector('#actions button[onclick="doubleDown()"]').disabled = false;
    document.querySelector('#actions button[onclick="split()"]').disabled = false;
}

function disableActionButtons() {
    document.querySelector('#actions button[onclick="hit()"]').disabled = true;
    document.querySelector('#actions button[onclick="stand()"]').disabled = true;
    document.querySelector('#actions button[onclick="doubleDown()"]').disabled = true;
    document.querySelector('#actions button[onclick="split()"]').disabled = true;
}

function dealerTurn(shoe, dealerHand, playerHand) {
    logMessage("\n---Dealer's Turn---");
    for (const key in playerHand) {
        if (playerHand.hasOwnProperty(key)) {
            logMessage(`${key} Hand: ${displayHand(playerHand[key].cards)}`);
        }
    }
    logMessage(`\nDealer Hand: ${displayHand(dealerHand)}`);
    while (true) {
        const points = handEval(dealerHand);
        if (points < 17) {
            dealerHand.push(drawCard(shoe));
            logMessage(`Dealer hits: ${displayHand(dealerHand)}`);
            if (handEval(dealerHand) > 21) {
                logMessage('Dealer busted.');
                break;
            }
        } else {
            logMessage('Dealer stands.');
            break;
        }
    }
    return dealerHand;
}

function total(playerHand, dealerHand) {
    const dealerPoints = handEval(dealerHand);
    logMessage(`\n---Final---`);
    for (const key in playerHand) {
        if (playerHand.hasOwnProperty(key)) {
            const hand = playerHand[key];
            const playerPoints = handEval(hand.cards);
            logMessage(`${key} Hand: ${displayHand(hand.cards)}`);
            if (playerPoints > 21) {
                logMessage("You lose.");
            } else if (dealerPoints > 21 || playerPoints > dealerPoints) {
                logMessage("You win.");
                gameState.balance += hand.bet * 2;
            } else if (playerPoints === dealerPoints) {
                logMessage("It's a push.");
                gameState.balance += hand.bet;
            } else {
                logMessage("You lose.");
            }
            hand.bet = 0;
        }
    }
    updateBalance();
}

function startRound() {
    if (gameState.balance < 1) {
        const loss = 100 + rebuyCounter * 100;
        while (true) {
            const rebuy = prompt("You have no money. Take out a loan? (Y/N) ").toLowerCase();
            if (rebuy === 'y') {
                gameState.balance = 100;
                rebuyCounter += 1;
                logMessage("Good decision. Now you can make gazillions.");
                break;
            } else if (rebuy === 'n') {
                logMessage(`You bought back in ${rebuyCounter} times and lost a total of $${loss}. See you next week!`);
                return;
            } else {
                logMessage("Invalid input. Enter Y or N.");
            }
        }
    }

    playerHand = {
        'Player': {
            cards: [],
            bet: 0
        }
    };
    logMessage(`\nYou have $${gameState.balance.toFixed(2)}`);
    logMessage('\n');
    if (gameState.quit) {
        const net = gameState.balance - (100 + rebuyCounter * 100);
        logMessage(`Quitter :(  Here's your net: $${net.toFixed(2)}, see you next week.`);
        return;
    }

    playerHand['Player'].cards = [drawCard(shoe), drawCard(shoe)];
    dealerHand = [drawCard(shoe), drawCard(shoe)];

    const checks = checkBlkjk(playerHand, dealerHand);
    if (checks === 1) {
        logMessage(`${displayHand(playerHand['Player'].cards)}`);
        logMessage(`Dealer Hand: ${displayHand(dealerHand)}`);
        logMessage('You got Blackjack!!!');
        gameState.balance += playerHand['Player'].bet * 1.5 + playerHand['Player'].bet;
        resetGame();
    } else if (checks === 2) {
        logMessage(`${displayHand(playerHand['Player'].cards)}`);
        logMessage(`\nDealer Hand: ${displayHand(dealerHand)}`);
        logMessage('Yikes...');
        gameState.balance += playerHand['Player'].bet;
        resetGame();
    } else {
        playerTurn(shoe, playerHand, dealerHand);
    }
}

function resetGame() {
    chipCounters[1] = 0;
    chipCounters[5] = 0;
    chipCounters[10] = 0;
    chipCounters[50] = 0;
    chipCounters[100] = 0;
    document.getElementById('chip-1').textContent = 0;
    document.getElementById('chip-5').textContent = 0;
    document.getElementById('chip-10').textContent = 0;
    document.getElementById('chip-50').textContent = 0;
    document.getElementById('chip-100').textContent = 0;
    updateCurrentBet();
}

// Add an event listener to the Start Game button to trigger startGame function
document.addEventListener("DOMContentLoaded", () => {
    document.querySelector('#start-game').addEventListener('click', () => {
        gameState.quit = false;
        startRound();
    });
});
