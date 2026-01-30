// js/game.js

import { createDeckManager } from "./deck.js";
import { createCard } from "./card.js";

const state = {
    maxHp: 20,
    hp: 20,
    potionUsedThisRoom: false,
    weapon: null,
    monstersOnWeapon: [],
    deck: null,
    room: [],          // up to 4 cards
    discard: [],       // for now just for debugging
    weapon: null,
    roomInteracted: false,
    ranLastRoom: false,
};

const els = {
    room: null,
    hpValue: null,
    cardsLeft: null,
    runBtn: null,
    combatArea: null,
    discardPile: null,
    discardLabel: null,
    deckLabel: null,
    deck: null,
};

let endHandled = false;

function checkEndConditions() {
    if (endHandled) return false;

    if (state.hp <= 0) {
        endHandled = true;
        alert("You died.");
        newGame({ hp: state.maxHp, includeJokers: false });
        endHandled = false;
        return true;
    }

    const deckEmpty = state.deck && state.deck.cardsLeft() === 0;
    const roomEmpty = state.room.length === 0;

    if (deckEmpty && roomEmpty) {
        endHandled = true;
        alert("You win!");
        newGame({ hp: state.maxHp, includeJokers: false });
        endHandled = false;
        return true;
    }

    return false;
}

function getCardValue(cardObj) {
    const r = cardObj.rank;

    if (r === "A") return 14;
    if (r === "J") return 11;
    if (r === "Q") return 12;
    if (r === "K") return 13;

    const n = Number(r);
    return Number.isFinite(n) ? n : 0;
}

function markRoomInteracted() {
    state.roomInteracted = true;
    state.ranLastRoom = false; // any normal action breaks the "ran last room" streak
}

function isHeart(cardObj) {
    return cardObj.suit === "♥";
}

function isDiamond(cardObj) {
    return cardObj.suit === "♦";
}

function isMonster(cardObj) {
    return cardObj.suit === "♣" || cardObj.suit === "♠";
}

function setHp(value) {
    state.hp = Math.max(0, Math.min(state.maxHp, value));
    if (els.hpValue) els.hpValue.textContent = String(state.hp);
    return checkEndConditions();
}

function updateCardsLeft() {
    const remaining = state.deck.cardsLeft();

    if (els.cardsLeft) {
        els.cardsLeft.textContent = String(remaining);
    }

    if (!els.deck) return;

    if (remaining === 0) {
        // Hide deck visuals completely (like discard)
        els.deck.classList.add("is-hidden");
        els.deck.classList.remove("stacked");
        els.deck.innerHTML = "";

        if (els.deckLabel) els.deckLabel.classList.remove("is-hidden");
    } else {
        els.deck.classList.remove("is-hidden");
        els.deck.classList.add("stacked");

        if (els.deck.children.length === 0) {
            const card = document.createElement("div");
            card.className = "card facedown-card";
            card.innerHTML = `<img src="images/cards/facedown_card.jpg" alt="Deck" />`;
            els.deck.appendChild(card);
        }
    }
}

function shouldShowRunButton() {
    return state.room.length === 4 && !state.roomInteracted && !state.ranLastRoom;
}

function updateRunButtonVisibility() {
    if (!els.runBtn) return;

    const show = shouldShowRunButton();
    els.runBtn.classList.toggle("is-hidden", !show);
}

function shuffleInPlace(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function renderRoom() {
    if (!els.room) return;

    els.room.innerHTML = "";

    state.room.forEach((cardObj, idx) => {
        const cardEl = createCard(cardObj.img, cardObj.id, false);
        cardEl.classList.add("room-card");
        cardEl.dataset.roomIndex = String(idx);

        cardEl.addEventListener("click", () => {
            handleRoomCardAction(idx, "left");
        });

        cardEl.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            handleRoomCardAction(idx, "right");
        });
        els.room.appendChild(cardEl);
    });

    updateRunButtonVisibility();
    checkEndConditions();
}

function renderCombat() {
    if (!els.combatArea) return;

    // Remove old rendered cards (keep the "Combat" label)
    els.combatArea.querySelectorAll(".combat-card").forEach(el => el.remove());

    // No weapon/monsters yet
    if (!state.weapon && state.monstersOnWeapon.length === 0) return;

    const baseLeft = 18;   // matches your panel padding
    const baseBottom = 18;
    const shift = 70;      // ~2/3 of a 100px card to overlap by ~1/3

    // Weapon (if present)
    if (state.weapon) {
        const weaponEl = createCard(state.weapon.img, state.weapon.id, false);
        weaponEl.classList.add("combat-card", "combat-weapon");
        weaponEl.style.position = "absolute";
        weaponEl.style.left = `${baseLeft}px`;
        weaponEl.style.bottom = `${baseBottom}px`;
        els.combatArea.appendChild(weaponEl);
    }

    // Monsters stacked on top of weapon, each new one shifted right
    state.monstersOnWeapon.forEach((m, i) => {
        const mEl = createCard(m.img, m.id, false);
        mEl.classList.add("combat-card", "combat-monster");
        mEl.style.position = "absolute";
        mEl.style.left = `${baseLeft + shift * (i + 1)}px`;
        mEl.style.bottom = `${baseBottom}px`;
        els.combatArea.appendChild(mEl);
    });
}

function renderDiscard() {
    if (!els.discardPile) return;

    // Clear current top discard card
    els.discardPile.innerHTML = "";

    const count = state.discard.length;

    // If no discarded cards, show label and no pile
    if (count === 0) {
        if (els.discardLabel) els.discardLabel.classList.remove("is-hidden");
        els.discardPile.classList.remove("stacked");
        return;
    }

    // If 2+ cards, show stacked layers like the deck
    els.discardPile.classList.toggle("stacked", count >= 2);

    // Show top discarded card face-up
    const top = state.discard[count - 1];
    const topEl = createCard(top.img, top.id, false);
    topEl.classList.add("facedown-card"); // keeps it above pseudo layers via z-index rule
    els.discardPile.appendChild(topEl);
}

function drawCard() {
    const card = state.deck.drawCard();
    updateCardsLeft();
    return card;
}

function dealNewRoom() {
    state.room = [];
    state.roomInteracted = false;
    state.potionUsedThisRoom = false;

    for (let i = 0; i < 4; i++) {
        const c = drawCard();
        if (!c) break;
        state.room.push(c);
    }

    renderRoom();
    updateRunButtonVisibility();
    checkEndConditions();
}

function advanceRoomIfNeeded() {
    // Case 1: room is empty — try to deal a fresh room
    if (state.room.length === 0) {
        state.potionUsedThisRoom = false;
        state.roomInteracted = false;
        state.ranLastRoom = false;

        // Attempt to draw up to 4 new cards
        const newRoom = [];
        for (let i = 0; i < 4; i++) {
            const c = drawCard();
            if (!c) break;
            newRoom.push(c);
        }

        state.room = newRoom;

        renderRoom();
        updateRunButtonVisibility();
        checkEndConditions();
        return;
    }

    // Case 2: exactly 1 card left — carry it to next room
    if (state.room.length !== 1) return;

    const carried = state.room[0];

    state.potionUsedThisRoom = false;
    state.roomInteracted = false;
    state.ranLastRoom = false;

    const newRoom = [carried];

    while (newRoom.length < 4) {
        const c = drawCard();
        if (!c) break;
        newRoom.push(c);
    }

    state.room = newRoom;

    console.log(`[ROOM] advancing; carried ${carried.id}`);

    renderRoom();
    updateRunButtonVisibility();
    checkEndConditions();
}

function handleRoomCardAction(index, action) {
    const cardObj = state.room[index];
    if (!cardObj) return;

    // HEARTS: potion (left = heal once per room, right = discard)
    if (isHeart(cardObj)) {
        if (action === "left") {
            markRoomInteracted();
            if (state.potionUsedThisRoom) {
                console.log("[HEART] potion already used this room");
                return;
            }

            const heal = getCardValue(cardObj);
            const before = state.hp;
            setHp(state.hp + heal);

            state.potionUsedThisRoom = true;
            console.log(`[HEART] healed ${state.hp - before} (card=${cardObj.id})`);
        } else if (action === "right") {
            markRoomInteracted();
            console.log(`[HEART] discarded (card=${cardObj.id})`);
        }

        state.room.splice(index, 1);
        state.discard.push(cardObj);
        renderDiscard();
        renderRoom();
        updateRunButtonVisibility();
        advanceRoomIfNeeded();
        return;
    }

    // DIAMONDS: weapons (left = equip, right = discard)
    if (isDiamond(cardObj)) {
        if (action === "left") {
            markRoomInteracted();
            // Discard current combat contents (weapon + monsters)
            if (state.weapon) state.discard.push(state.weapon);
            if (state.monstersOnWeapon.length) state.discard.push(...state.monstersOnWeapon);

            state.weapon = cardObj;
            state.monstersOnWeapon = [];

            console.log(`[WEAPON] equipped ${cardObj.id}`);

            state.room.splice(index, 1);
            renderCombat();
            renderRoom();
            updateRunButtonVisibility();
            advanceRoomIfNeeded();
            return;
        }

        // right click: discard weapon card
        console.log(`[WEAPON] discarded ${cardObj.id}`);
        markRoomInteracted();
        state.room.splice(index, 1);
        state.discard.push(cardObj);
        renderDiscard();
        renderRoom();
        updateRunButtonVisibility();
        advanceRoomIfNeeded();
        return;
    }

    // CLUBS/SPADES: monsters
    if (isMonster(cardObj)) {
        const monsterValue = getCardValue(cardObj);

        // Left click requires a weapon equipped
        if (action === "left" && !state.weapon) {
            console.log(`[MONSTER] cannot be left clicked ${cardObj.id} without a weapon`);
            return;
        }

        // Right click: fight by hand (full damage), goes to discard
        if (action === "right") {
            markRoomInteracted();
            const ended = setHp(state.hp - monsterValue);
            if (ended) return;

            console.log(`[MONSTER] fought by hand ${cardObj.id}, damage=${monsterValue}, hp=${state.hp}`);

            state.room.splice(index, 1);
            state.discard.push(cardObj);
            renderDiscard();
            renderRoom();
            updateRunButtonVisibility();
            advanceRoomIfNeeded();
            return;
        }

        // Left click: fight with weapon, subject to stacking rule
        // Rule: if a monster is already on the weapon, the last fought monster must be > clicked monster
        const last = state.monstersOnWeapon[state.monstersOnWeapon.length - 1];
        if (last) {
            const lastValue = getCardValue(last);
            if (!(lastValue > monsterValue)) {
                console.log(`[MONSTER] cannot fight ${cardObj.id} with weapon; last=${last.id} (${lastValue})`);
                return;
            }
        }

        const weaponValue = state.weapon ? getCardValue(state.weapon) : 0;
        const damage = Math.max(0, monsterValue - weaponValue);
        const ended = setHp(state.hp - damage);
        if (ended) return;

        console.log(`[MONSTER] fought with weapon ${cardObj.id}, weapon=${weaponValue}, damage=${damage}, hp=${state.hp}`);

        // Move monster to combat stack
        state.monstersOnWeapon.push(cardObj);

        state.room.splice(index, 1);
        renderCombat();
        renderRoom();
        updateRunButtonVisibility();
        advanceRoomIfNeeded();
        return;
    }

    // Fallback: discard
    console.log(`[CARD] ${action}-clicked ${cardObj.id} (no rule)`);
    state.room.splice(index, 1);
    state.discard.push(cardObj);
    renderDiscard();
    renderRoom();
    updateRunButtonVisibility();
    advanceRoomIfNeeded();
}

function runFromRoom() {
    if (state.room.length === 0) return;

    // Disallow: after any interaction, or two runs in a row
    if (state.roomInteracted || state.ranLastRoom) return;

    console.log("[RUN] running from room; returning cards to bottom of deck:", state.room.map(c => c.id).join(", "));

    // Mark that we ran this room (prevents running twice in a row)
    state.ranLastRoom = true;

    // Return room cards to bottom of deck in random order
    const toReturn = [...state.room];
    shuffleInPlace(toReturn);
    state.deck.putOnBottom(toReturn);

    // Clear the room and reset per-room limits
    state.room = [];
    state.potionUsedThisRoom = false;

    // Deck size changed, update counter and deal next room
    updateCardsLeft();
    dealNewRoom();
}

function newGame({ hp = state.maxHp, includeJokers = true, seed = null } = {}) {
    state.deck = createDeckManager({ includeJokers, seed });
    state.room = [];
    state.discard = [];
    state.weapon = null;
    state.monstersOnWeapon = [];
    renderCombat();
    renderDiscard();

    setHp(hp);
    updateCardsLeft();
    dealNewRoom();
    state.potionUsedThisRoom = false;

    console.log("[NEW GAME]", { hp: state.hp, cardsLeft: state.deck.cardsLeft() });
}

function initDomRefs() {
    els.room = document.getElementById("room");
    els.combatArea = document.getElementById("combatArea");
    els.hpValue = document.getElementById("hpValue");
    els.cardsLeft = document.getElementById("cardsLeftValue");
    els.runBtn = document.getElementById("runBtn");
    els.discardPile = document.getElementById("discard");
    els.discardLabel = document.getElementById("discardLabel");
    els.deckLabel = document.getElementById("deckLabel");
    els.deck = document.getElementById("deck");

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
        handleRoomCardAction,
        setHp,
    };
}

document.addEventListener("DOMContentLoaded", init);
