// js/game.js

import { createDeckManager } from "./deck.js";
import { createCard } from "./card.js";

const state = {
    hp: 20,
    deck: null,
    room: [],          // up to 4 cards
    discard: [],       // for now just for debugging
};

const els = {
    room: null,
    hpValue: null,
    cardsLeftValue: null,
    runBtn: null,
};

function setHp(value) {
    state.hp = Math.max(0, value);
    if (els.hpValue) els.hpValue.textContent = String(state.hp);
}

function updateCardsLeft() {
    if (els.cardsLeftValue && state.deck) {
        els.cardsLeftValue.textContent = String(state.deck.cardsLeft());
    }
}

function shouldShowRunButton() {
    // For now: show only when there are 4 cards in the room (i.e., a full room to "run" from)
    return state.room.length === 4;
}

function updateRunButtonVisibility() {
    if (!els.runBtn) return;

    const show = shouldShowRunButton();
    els.runBtn.classList.toggle("is-hidden", !show);
}

function renderRoom() {
    if (!els.room) return;

    els.room.innerHTML = "";

    state.room.forEach((cardObj, idx) => {
        const cardEl = createCard(cardObj.img, cardObj.id, false);
        cardEl.classList.add("room-card");
        cardEl.dataset.roomIndex = String(idx);

        cardEl.addEventListener("click", () => {
            pickRoomCard(idx);
        });

        els.room.appendChild(cardEl);
    });

    updateRunButtonVisibility();
}

function drawCard() {
    const card = state.deck.drawCard();
    updateCardsLeft();
    return card;
}

function fillRoom() {
    while (state.room.length < 4) {
        const card = drawCard();
        if (!card) break;
        state.room.push(card);
    }
    renderRoom();
}

function pickRoomCard(index) {
    const picked = state.room[index];
    if (!picked) return;

    // Remove from room, track discard for debugging
    state.room.splice(index, 1);
    state.discard.push(picked);

    console.log(`[PICK] ${picked.id} | hp=${state.hp} | cardsLeft=${state.deck.cardsLeft()}`);
    fillRoom();
}

function runFromRoom() {
    if (state.room.length === 0) return;

    // For debugging: "run" discards the whole room, then refills
    console.log("[RUN] running from room, discarding:", state.room.map(c => c.id).join(", "));

    state.discard.push(...state.room);
    state.room = [];

    fillRoom();
}

function newGame({ hp = 20, includeJokers = true, seed = null } = {}) {
    state.deck = createDeckManager({ includeJokers, seed });
    state.room = [];
    state.discard = [];

    setHp(hp);
    updateCardsLeft();
    fillRoom();

    console.log("[NEW GAME]", { hp: state.hp, cardsLeft: state.deck.cardsLeft() });
}

function initDomRefs() {
    els.room = document.getElementById("room");
    els.hpValue = document.getElementById("hpValue");
    els.cardsLeftValue = document.getElementById("cardsLeftValue");
    els.runBtn = document.getElementById("runBtn");

    if (els.runBtn) {
        els.runBtn.addEventListener("click", runFromRoom);
    }
}

function init() {
    initDomRefs();
    newGame({ hp: 20, includeJokers: false });

    // Quick dev helpers in console:
    window.scoundrel = {
        state,
        newGame,
        runFromRoom,
        pickRoomCard,
        setHp,
    };
}

document.addEventListener("DOMContentLoaded", init);
