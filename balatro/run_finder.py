import pyautogui
import time

skip_images = {
    "Free Shop" : "images/free_shop_skip.png",
    "Polychrome" : "images/polychrome_skip.png",
    "Uncommon" : "images/uncommon_skip.png"
}

def check_image(image_path, confidence=0.8):
    """
    Safely check if an image is visible on screen.

    Parameters:
        image_path (str): file path to the image to search for
        confidence (float): match confidence (0.0–1.0)

    Returns:
        bool: True if found, False otherwise
    """
    start = time.time()
    try:
        result = pyautogui.locateOnScreen(image_path, confidence=confidence)
        found = result is not None
        elapsed = time.time() - start
        print(f"[CHECK] {image_path} conf={confidence} -> {found} ({elapsed:.2f}s)")
        return found
    except pyautogui.ImageNotFoundException:
        elapsed = time.time() - start
        print(f"[CHECK] {image_path} conf={confidence} -> False (ImageNotFoundException) ({elapsed:.2f}s)")
        return False
    except Exception as e:
        elapsed = time.time() - start
        print(f"[WARN] error checking image '{image_path}': {e} ({elapsed:.2f}s)")
        return False

def click_image(image_path, confidence=0.8):
    """
    Safely find and click an image on screen.

    Parameters:
        image_path (str): file path to the image to search for
        confidence (float): match confidence (0.0–1.0)

    Returns:
        bool: True if clicked, False otherwise
    """
    start = time.time()
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        elapsed = time.time() - start

        if location:
            print(f"[CLICK] {image_path} conf={confidence} -> at {location} ({elapsed:.2f}s)")
            pyautogui.click(location)
            return True

        print(f"[CLICK] {image_path} conf={confidence} -> not found ({elapsed:.2f}s)")
        return False
    except pyautogui.ImageNotFoundException:
        elapsed = time.time() - start
        print(f"[CLICK] {image_path} conf={confidence} -> False (ImageNotFoundException) ({elapsed:.2f}s)")
        return False
    except Exception as e:
        elapsed = time.time() - start
        print(f"[WARN] error clicking image '{image_path}': {e} ({elapsed:.2f}s)")
        return False

def new_run():
    """
    Attempt to start a new run, with debug output.

    Parameters:
        None

    Returns:
        None
    """
    print("[RUN] attempting new run sequence")

    clicked_options = click_image(image_path="images/options.png", confidence=0.8)
    time.sleep(0.5)

    clicked_new_run = click_image(image_path="images/new_run.png", confidence=0.8)
    time.sleep(0.5)

    clicked_play = click_image(image_path="images/play.png", confidence=0.8)

    if clicked_options or clicked_new_run or clicked_play:
        print("[RUN] at least one click succeeded; waiting for UI")
        time.sleep(3)
    else:
        print("[RUN] no clicks succeeded; skipping long wait")
        time.sleep(0.3)

def check_skip():
    for name, path in skip_images.items():
        hit1 = check_image(path, confidence=0.9)
        if hit1:
            time.sleep(0.2)  # let a frame change; helps reject one-off matches
            hit2 = check_image(path, confidence=0.9)

            if hit2:
                print(f"Found {name}")
                return True

            print(f"[DEBUG] rejected one-off match for {name}")

    return False


def main():
    """
    Run new runs until a skip image is found, with debug output.

    Parameters:
        None

    Returns:
        None
    """
    print("[MAIN] starting")
    new_run()

    i = 0
    while True:
        i += 1
        print(f"[LOOP] iteration {i}")

        if check_skip():
            print("[MAIN] skip condition found, breaking")
            break

        print("[MAIN] skip not found, starting new run")
        new_run()

    print("[MAIN] main loop done")


if __name__ == "__main__":
    main()