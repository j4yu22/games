function showElement(selector) {
    document.querySelector(selector).classList.remove('hidden');
}

function hideElement(selector) {
    document.querySelector(selector).classList.add('hidden');
}

// Function to start the game
function startGame() {
    hideElement('.bet-buttons');
    showElement('.dealer');
    showElement('.player');
    // Enable the appropriate action buttons
    document.querySelector('.hit').disabled = false;
    document.querySelector('.stand').disabled = false;
}

// Function to confirm bet and start the player's turn
function confirmBet() {
    // Your existing confirmBet logic here

    // After confirming bet, show the player's hand and options
    startGame();
}

// Example function call to initialize the game (can be called when user clicks "Confirm Bet")
document.querySelector('.confirm').addEventListener('click', confirmBet);
