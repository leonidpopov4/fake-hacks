import pyautogui
import ui


def setup_pyautogui():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.0
    if hasattr(pyautogui, "MINIMUM_DURATION"):
        pyautogui.MINIMUM_DURATION = 0
    if hasattr(pyautogui, "MINIMUM_SLEEP"):
        pyautogui.MINIMUM_SLEEP = 0


if __name__ == "__main__":
    # make sure dependencies are installed:
    # pip install pyautogui keyboard pillow pynput opencv-python numpy
    setup_pyautogui()
    ui.main()
