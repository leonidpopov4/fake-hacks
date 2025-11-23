import numpy as np
from PIL import Image
import cv2
import pyautogui

import state


def pil_to_cv_gray(pil_img: Image.Image) -> np.ndarray:
    """Convert a PIL image to an OpenCV grayscale image."""
    rgb = np.array(pil_img)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return gray


def downscale_gray(gray: np.ndarray, factor: float) -> np.ndarray:
    """Downscale a grayscale image by given factor using area interpolation."""
    if factor == 1.0:
        return gray
    h, w = gray.shape
    new_w = int(w / factor)
    new_h = int(h / factor)
    if new_w <= 0 or new_h <= 0:
        return gray
    return cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)


def add_template_from_patch(patch: Image.Image, where_text: str):
    """Create template entry from a PIL patch image."""
    patch_np = np.array(patch)              # RGB
    avg_color = patch_np.mean(axis=(0, 1))  # [R,G,B]

    gray_patch = pil_to_cv_gray(patch)
    h, w = gray_patch.shape

    state.template_counter += 1
    filename = f"{state.TEMPLATE_DIR}/template_{state.template_counter}.png"
    patch.save(filename)

    name = f"Target {state.template_counter}"
    state.templates.append({
        "id": state.template_counter,
        "name": name,
        "path": filename,
        "img": gray_patch,
        "w": w,
        "h": h,
        "last_click": 0.0,
        "enabled": True,
        "clicks": 0,
        "avg_color": avg_color,  # RGB
    })

    print(f"[LEARN] Saved {name} {where_text} -> {filename} (avg_color={avg_color})")


def record_click_template(x, y):
    """Capture a small patch around (x, y) and store it as a NEW target."""
    left = int(x - state.REGION_WIDTH // 2)
    top = int(y - state.REGION_HEIGHT // 2)
    patch = pyautogui.screenshot(
        region=(left, top, state.REGION_WIDTH, state.REGION_HEIGHT)
    )
    add_template_from_patch(patch, f"at ({x}, {y})")


def record_center_template():
    """Capture a patch from the CENTER of the screen (for gamemode)."""
    screen_w, screen_h = pyautogui.size()
    cx = screen_w // 2
    cy = screen_h // 2
    left = int(cx - state.REGION_WIDTH // 2)
    top = int(cy - state.REGION_HEIGHT // 2)
    patch = pyautogui.screenshot(
        region=(left, top, state.REGION_WIDTH, state.REGION_HEIGHT)
    )
    add_template_from_patch(patch, "from screen center (TAB)")


def load_existing_templates():
    """Load any PNG targets from TEMPLATE_DIR at startup (from previous runs)."""
    import os

    files = [f for f in os.listdir(state.TEMPLATE_DIR)
             if f.lower().endswith(".png")]
    files.sort()
    for fname in files:
        path = f"{state.TEMPLATE_DIR}/{fname}"
        try:
            patch = Image.open(path).convert("RGB")
            patch_np = np.array(patch)
            avg_color = patch_np.mean(axis=(0, 1))  # RGB

            gray_patch = pil_to_cv_gray(patch)
            h, w = gray_patch.shape

            state.template_counter += 1
            name = f"Target {state.template_counter}"
            state.templates.append({
                "id": state.template_counter,
                "name": name,
                "path": path,
                "img": gray_patch,
                "w": w,
                "h": h,
                "last_click": 0.0,
                "enabled": True,
                "clicks": 0,
                "avg_color": avg_color,
            })
            print(f"[LOAD] Found existing {name} from {path} (avg_color={avg_color})")
        except Exception as e:
            print(f"[WARN] Could not load {path}: {e}")
