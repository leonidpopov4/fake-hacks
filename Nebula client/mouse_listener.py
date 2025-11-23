from pynput import mouse
from pynput.mouse import Button

import state
import capture


def on_click(x, y, button, pressed):
    """Mouse listener: records your left-clicks while recording mode is ON."""
    if not pressed:
        return

    if button != Button.left:
        return

    if state.ignore_recording:
        return

    if state.recording:
        capture.record_click_template(x, y)


def mouse_listener_thread():
    """Background thread for mouse events."""
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
