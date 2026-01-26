// js/logic.js

function createStandardDeck({ includeJokers = false } = {}) {
    const suits = ["♠", "♣", "♥", "♦"]; // Spades, Clubs, Hearts, Diamonds
    const ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];

    const deck = [];

    for (const suit of suits) {
        for (const rank of ranks) {
            deck.push({
                rank,
                suit,
                id: `${rank}${suit}`,
                img: `images/cards/${suit}${rank}.png`
            });
        }
    }

    if (includeJokers) {
        deck.push({
            rank: "JOKER",
            suit: "RED",
            id: "JOKER_RED",
            img: "images/cards/joker_red.png"
        });

        deck.push({
            rank: "JOKER",
            suit: "BLACK",
            id: "JOKER_BLACK",
            img: "images/cards/joker_black.png"
        });
    }

    return deck;
}


function mulberry32(seed) {
    let t = seed >>> 0;
    return function () {
        t += 0x6D2B79F5;
        let x = Math.imul(t ^ (t >>> 15), 1 | t);
        x ^= x + Math.imul(x ^ (x >>> 7), 61 | x);
        return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
    };
}


function shuffleInPlace(arr, rng = Math.random) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}


export function createDeckManager({ includeJokers = false, seed = null } = {}) {
    let deck = [];
    let drawIndex = 0;
    const rng = seed === null ? Math.random : mulberry32(seed);

    function shuffleNewDeck() {
        deck = createStandardDeck({ includeJokers });
        shuffleInPlace(deck, rng);
        drawIndex = 0;
    }

    function drawCard() {
        if (drawIndex >= deck.length) return null;
        const card = deck[drawIndex];
        drawIndex += 1;
        return card;
    }

    function drawMany(count = 1) {
        const cards = [];
        for (let i = 0; i < count; i++) {
            const c = drawCard();
            if (!c) break;
            cards.push(c);
        }
        return cards;
    }

    function cardsLeft() {
        return deck.length - drawIndex;
    }

    function getDeckOrder() {
        // Remaining order (top-to-bottom from next draw onward)
        return deck.slice(drawIndex);
    }

    // initialize immediately
    shuffleNewDeck();

    return {
        shuffleNewDeck,
        drawCard,
        drawMany,
        cardsLeft,
        getDeckOrder
    };
}
