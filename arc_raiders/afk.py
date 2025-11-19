"""
start up: if game is not running, launch it, wait 2 minutes, ensure squad fill is set
to off, ensure custom loadout is cleared by readying up with free loadout, then
cancelling immediately

get into raid: play > night raid > confirm > check inventory clear > ready up >
ready up anyways 

raid: check if dead

process after raid: id death screen > wait 15s > continue > unload backpack > continue x3 >
possible survey > wait > workshop > scrappy > claim > esc x2
"""
import psutil
import os
import time
import pyautogui
import random

# PyAutoGUI Functions
def check_image(image_path, confidence=0.8):
    """
    safely check if an image is visible on screen.
    """
    time.sleep(1 + random.uniform(0.2, 0.6))
    try:
        result = pyautogui.locateOnScreen(image_path, confidence=confidence)
        return result is not None
    except pyautogui.ImageNotFoundException:
        return False
    except Exception as e:
        print(f"[WARN] error checking image '{image_path}': {e}")
        return False

def click_image(image_path, confidence=0.8):
    """
    safely find and click an image on screen.
    """
    time.sleep(1 + random.uniform(0.2, 0.6))
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.click(location)
            return True
        return False
    except pyautogui.ImageNotFoundException:
        return False
    except Exception as e:
        print(f"[WARN] error clicking image '{image_path}': {e}")
        return False
    
def press_key(key, duration=0.1):
    """
    press a key.
    """
    pyautogui.keyDown(key)
    time.sleep(duration)
    pyautogui.keyUp(key)

# Game Launching Functions
def check_game_status(game_exe):
    """check if a process with the given name is currently running"""
    for proc in psutil.process_iter(['name']):
        if game_exe.lower() in proc.info['name'].lower():
            return True
    return False

def launch_game():
    """launch arc raiders via steam if it is not running"""
    game_exe = "PioneerGame.exe"  # check task manager for exact name when open
    game_appid = 1808500          # arc raiders steam app id

    if not check_game_status(game_exe):
        print("Launching ARC Raiders...")
        os.startfile(f"steam://run/{game_appid}")
        time.sleep(100)  # give it time to load
    
    launched = False
    launched_counter = 0
    while not launched:
        if check_image("images/header.png", confidence=0.8):
            launched = True

        elif launched_counter > 500:
            print("Failed to find header.png within reasonable time.")
            break

        else:
            time.sleep(5)
            launched_counter += 1

# Pre-Game Checks
def check_squad_fill():
    """ensure squad fill is turned off"""
    if check_image("images/fill_squad_on.png", confidence=0.9):
        click_image("images/fill_squad_on.png", confidence=0.9)
        print("Turned off squad fill.")

def clear_inventory():
    """clear inventory by readying up with free loadout and cancelling"""
    cancel_matchmaking = [1975, 1360]
    click_image("images/play.png", confidence=0.8)
    pyautogui.click()
    click_image("images/free_loadout.png", confidence=0.8)
    pyautogui.click()
    click_image("images/ready_up.png", confidence=0.8)
    time.sleep(1.5)
    if check_image("images/confirm.png", confidence=0.8):
        click_image("images/cancel.png", confidence=0.8)
    else:
        pyautogui.click(cancel_matchmaking)
    print("Inventory cleared.")

def find_night_raid():
    """navigate to night raid selection"""
    buried_city = [375, 805]
    spaceport = [635, 450]
    dam_battlegrounds = [1180, 890]
    blue_gate = [1620, 725]

    time.sleep(1)
    pyautogui.click(buried_city)
    pyautogui.click()
    if check_image("images/confirm.png", confidence=0.9):
        click_image("images/confirm.png", confidence=0.9)
        return
    pyautogui.click(spaceport)
    pyautogui.click()
    if check_image("images/confirm.png", confidence=0.9):
        click_image("images/confirm.png", confidence=0.9)
        return
    pyautogui.click(dam_battlegrounds)
    pyautogui.click()
    if check_image("images/confirm.png", confidence=0.9):
        click_image("images/confirm.png", confidence=0.9)
        return
    pyautogui.click(blue_gate)
    pyautogui.click()
    if check_image("images/confirm.png", confidence=0.9):
        click_image("images/confirm.png", confidence=0.9)
        return
    print("Failed to find night raid location.")

def death_check():
    """check if player is dead in raid"""
    dead = False
    while not dead:
        if check_image("images/death_screen.png", confidence=0.8):
            dead = True
        time.sleep(3)

# Main functions
def startup():
    """handle pre loop startup tasks"""
    launch_game()
    check_squad_fill()
    # clear_inventory()

def loop():
    """enter, afk, exit, offload loop"""
    loop_counter = 0
    while True:
        #pre raid
        check_squad_fill()
        click_image("images/play.png", confidence=0.8)
        time.sleep(1)
        pyautogui.click()

        # find_night_raid()
        
        # click_image("images/confirm.png", confidence=0.8)
        
        # if not check_image("images/empty_inventory.png", confidence=0.8):
        #     click_image("images/back.png", confidence=0.8)
        #     time.sleep(1)
        #     pyautogui.click()
        #     clear_inventory()
        #     continue
        click_image("images/ready_up.png", confidence=0.8)
        click_image("images/ready_up_anyways.png", confidence=0.8)
        #in raid
        death_check()
        #post raid
        time.sleep(5)
        click_image("images/continue.png", confidence=0.8)
        click_image("images/unload_backpack.png", confidence=0.8)
        click_image("images/continue.png", confidence=0.8)
        pyautogui.click()
        pyautogui.click()
        pyautogui.click()
        if check_image("images/skip.png", confidence=0.8):
            click_image("images/skip.png", confidence=0.8)
        time.sleep(10)
        if check_image("images/workshop.png", confidence=0.8):
            click_image("images/workshop.png", confidence=0.8)
        else:
            workshop_coords = [325, 40]
            pyautogui.click(workshop_coords)
        click_image("images/scrappy.png", confidence=0.8)
        if check_image("images/claim.png", confidence=0.8):
            click_image("images/claim.png", confidence=0.8)
        click_image("images/back.png", confidence=0.8)
        time.sleep(1)
        pyautogui.click()
        loop_counter += 1
        print(f"Completed AFK runs: {loop_counter}")

def main():
    startup()
    loop()

if __name__ == "__main__":
    main()