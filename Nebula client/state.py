import os

# ========== TUNABLE SETTINGS (current values) ==========

# Patch size around clicks/center
REGION_WIDTH = 32
REGION_HEIGHT = 32

# Template match threshold (normal/ghost mode)
MATCH_THRESHOLD = 0.80

# Per-template cooldown (seconds)
CLICK_COOLDOWN = 0.05

# Downscale factor for template matching
DOWNSCALE = 1.5

# Scan speed (1..10) – mapped to delay
scan_speed = 7.0

# Mouse move duration for NORMAL mode (seconds)
MOUSE_MOVE_DURATION = 0.03

# Modes
ghost_mode = False          # normal mode: teleport back after click
gamemode = False            # center/crosshair mode
simplify_mode = False       # game mode: average color check
speed_mode = "normal"       # "normal" or "fast"

# Game mode FOV (half of box size in pixels)
CENTER_BOX_HALF = 40        # 40 -> 80x80 box

# Game mode color settings
GAME_COLOR_DIST = 30.0      # RGB distance
GAME_MIN_COVERAGE = 0.45    # 0..1, fraction of pixels that must match

# Global CPS limit
GLOBAL_MIN_CLICK_GAP = 0.05  # seconds between any two clicks

# ========== RUNTIME STATE ==========

templates = []              # list of target dicts
recording = False
auto_enabled = False
ignore_recording = False
running = True
template_counter = 0
global_last_click = 0.0

optimized_mode = False      # optimized crosshair mode (popup)
jitter_mode = False         # tiny random wobble in normal mode

# NEW: adaptive scan behavior
adaptive_scan = False       # when True: slow idle scan, fast when target seen
last_target_seen = 0.0      # timestamp of last valid target shot

total_auto_clicks = 0       # counts every auto safe_click()

# Template directory
TEMPLATE_DIR = "click_templates"
os.makedirs(TEMPLATE_DIR, exist_ok=True)
