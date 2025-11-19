import math

trader_mult = {
    "prapor": 0.5,
    "therapist": 0.63,
    "fence": 0.4,
    "skier": 0.49,
    "peacekeeper": 0.45,
    "mechanic": 0.56,
    "ragman": 0.62,
    "jaeger": 0.6,
    "ref": 0.5
}

player_mult = {
    "hideout_lvl": 1,
    "int_center_3": False
}

# ---------------------------
# PLAYER MULT
# ---------------------------
def get_player_mult():
    while True:
        try:
            player_mult["hideout_lvl"] = int(input("Enter your Hideout Management skill level: "))
            break
        except ValueError:
            print("Please enter a valid integer.")

    int_center = input("Do you have Intelligence Center level 3? (y/n): ")
    player_mult["int_center_3"] = (int_center.lower() == 'y')


# ---------------------------
# TRADER SELECTION
# ---------------------------
def select_trader():
    print("Available Traders: \nPrapor, Therapist, Fence, Skier, Peacekeeper, Mechanic, Ragman, Jaeger, Ref")
    while True:
        trader_select = input("Please type the name of the trader you are selling to: ").strip().lower()
        if trader_select in trader_mult:
            return trader_mult[trader_select]
        else:
            print("Invalid trader selection. Please try again.")


# ---------------------------
# BASE VALUE FROM WIKI LOGIC
# ---------------------------
def get_base_value():
    print("Place the item in any trader's sell menu and note its price.")
    tm = select_trader()

    while True:
        try:
            vendor_value = int(input("Enter the vendor value of the item: "))
            break
        except ValueError:
            print("Please enter a valid integer.")

    return vendor_value / tm


# ---------------------------
# BUILT-IN FLEA TAX FORMULA
# ---------------------------
def flea_tax(list_price, base_value, quantity=1):
    Ti = 0.03
    Tr = 0.03

    VO = base_value * quantity
    VR = list_price  # rubles

    # --- PO modifier ---
    PO = math.log10(VO / VR)
    if VR < VO:
        PO = PO ** 1.08

    # --- PR modifier ---
    PR = math.log10(VR / VO)
    if VR >= VO:
        PR = PR ** 1.08

    # Base tax before reductions
    tax = VO * Ti * (4 ** PO) * quantity + VR * Tr * (4 ** PR) * quantity

    # Reductions
    reduction = 0

    if player_mult["int_center_3"]:
        reduction += 0.30

    reduction += player_mult["hideout_lvl"] * 0.003
    reduction = min(reduction, 0.45)

    return tax * (1 - reduction)


# ---------------------------
# OPTIMAL PRICE (profit maximizing)
# ---------------------------
def optimize_price(base_value):
    max_profit = -999999
    best_price = base_value  # starting point

    # Search from base_value → base_value × 50 (safe range)
    for price in range(int(base_value), int(base_value * 50), 100):  # check every 100 rubles
        tax = flea_tax(price, base_value)
        profit = price - tax

        if profit > max_profit:
            max_profit = profit
            best_price = price

    return best_price, max_profit


# ---------------------------
# MAIN LOGIC
# ---------------------------
def main():
    print("=== Tarkov Flea Market Optimizer ===\n")

    get_player_mult()
    base_value = get_base_value()

    print(f"\nBase item value (correct Tarkov base price): {base_value:.2f}₽")

    print("\nCalculating optimal listing price (this may take a second)...")
    best_price, best_profit = optimize_price(base_value)

    fee = flea_tax(best_price, base_value)
    take_home = best_price - fee

    print("\n=== Optimal Listing Result ===")
    print(f"Optimal Listing Price: {best_price:,}₽")
    print(f"Fee at that price: {fee:,.0f}₽")
    print(f"Take-home profit: {take_home:,.0f}₽")


if __name__ == "__main__":
    main()
