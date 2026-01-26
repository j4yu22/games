/**
 * Create a card DOM element using the shared card CSS.
 *
 * Parameters:
 *      imgSrc (string): path to the card image
 *      alt (string): alt text for accessibility
 *      facedown (boolean): whether this card is face-down
 *
 * Returns:
 *      HTMLElement: <div class="card"> element
 */
export function createCard(imgSrc, alt = "", facedown = false) {
    const card = document.createElement("div");
    card.classList.add("card");
    card.classList.add("selectable");

    if (facedown) {
        card.classList.add("facedown-card");
    }

    const img = document.createElement("img");
    img.src = imgSrc;
    img.alt = facedown ? "Face-down card" : alt;

    card.appendChild(img);
    return card;
}
