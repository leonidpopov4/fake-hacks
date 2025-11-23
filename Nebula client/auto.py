import time
import random

import numpy as np
import cv2
import pyautogui

import state
from capture import downscale_gray


def safe_click():
    """
    Send a very short left-click but aggressively make sure
    the button is not left 'held' down in the game.

    Every 5th auto click, also do a stronger reset pattern.
    """
    # normal safe click
    try:
        # just in case game thinks it's already down
        pyautogui.mouseUp(button="left")
    except Exception:
        pass

    pyautogui.mouseDown(button="left")
    time.sleep(0.01)
    pyautogui.mouseUp(button="left")

    # count this auto click
    state.total_auto_clicks += 1

    # every 5th click -> extra "reset" sequence
    if state.total_auto_clicks % 5 == 0:
        try:
            # small pause then a strong release+tap+release
            time.sleep(0.02)
            pyautogui.mouseUp(button="left")
            time.sleep(0.01)
            pyautogui.mouseDown(button="left")
            time.sleep(0.01)
            pyautogui.mouseUp(button="left")
            # we do NOT increment total_auto_clicks here
            # so this extra pattern doesn't recurse
        except Exception:
            pass


def auto_click_loop():
    """
    When AUTO is ON:
      - normal mode: full-screen template matching, move mouse / ghost.
      - game mode:
          * FAST / optimized: single pixel at crosshair.
          * NORMAL: center box + coverage / avg color.

    With adaptive_scan:
      - when no target recently -> slow scanning
      - when a target was just seen -> ultra-fast scanning
    """
    screen_w, screen_h = pyautogui.size()

    while state.running:
        try:
            if state.auto_enabled and state.templates:
                now = time.time()

                # ---- GLOBAL FIRE-RATE CAP ----
                if now - state.global_last_click < state.GLOBAL_MIN_CLICK_GAP:
                    time.sleep(0.001)
                    continue

                # per-template cooldown
                eff_cd = 0.0 if state.speed_mode == "fast" else state.CLICK_COOLDOWN

                if state.gamemode:
                    # ---------- GAME / CROSSHAIR MODE ----------
                    tpl = None
                    for t in state.templates:
                        if t.get("enabled", True):
                            tpl = t
                            break

                    if tpl is None:
                        time.sleep(0.001)
                        continue

                    if time.time() - tpl["last_click"] < eff_cd:
                        time.sleep(0.001)
                        continue

                    tpl_color = np.array(
                        tpl.get("avg_color", [0, 0, 0]), dtype=float
                    )

                    use_fast_pixel = (
                        state.speed_mode == "fast" or state.optimized_mode
                    )

                    if use_fast_pixel:
                        # FAST / OPTIMIZED: single pixel at crosshair
                        cx = screen_w // 2
                        cy = screen_h // 2
                        r, g, b = pyautogui.pixel(cx, cy)
                        pix = np.array([r, g, b], dtype=float)
                        dist = np.linalg.norm(pix - tpl_color)

                        if dist <= state.GAME_COLOR_DIST:
                            print(
                                f"[GAME-FAST] Shooting for {tpl['name']} "
                                f"(center_dist={dist:.1f} ≤ {state.GAME_COLOR_DIST})"
                            )
                            state.ignore_recording = True
                            state.global_last_click = time.time()
                            safe_click()
                            state.ignore_recording = False

                            t_now = time.time()
                            tpl["last_click"] = t_now
                            tpl["clicks"] = tpl.get("clicks", 0) + 1
                            state.last_target_seen = t_now

                    else:
                        # NORMAL game mode: FOV box around crosshair
                        cx = screen_w // 2
                        cy = screen_h // 2

                        left = cx - state.CENTER_BOX_HALF
                        top = cy - state.CENTER_BOX_HALF
                        width = state.CENTER_BOX_HALF * 2
                        height = state.CENTER_BOX_HALF * 2

                        patch_pil = pyautogui.screenshot(
                            region=(left, top, width, height)
                        )
                        patch_np = np.array(patch_pil, dtype=float)

                        if patch_np.size == 0:
                            time.sleep(0.001)
                            continue

                        if state.simplify_mode:
                            # Average color vs template average
                            patch_avg = patch_np.mean(axis=(0, 1))
                            dist = np.linalg.norm(patch_avg - tpl_color)

                            if dist <= state.GAME_COLOR_DIST:
                                print(
                                    f"[GAME-SIMPLE] Shooting for {tpl['name']} "
                                    f"(avg_dist={dist:.1f} ≤ {state.GAME_COLOR_DIST})"
                                )
                                state.ignore_recording = True
                                state.global_last_click = time.time()
                                safe_click()
                                state.ignore_recording = False

                                t_now = time.time()
                                tpl["last_click"] = t_now
                                tpl["clicks"] = tpl.get("clicks", 0) + 1
                                state.last_target_seen = t_now
                        else:
                            # Strict coverage check
                            flat = patch_np.reshape(-1, 3)
                            dists = np.linalg.norm(flat - tpl_color, axis=1)
                            close_mask = dists <= state.GAME_COLOR_DIST
                            coverage = close_mask.mean()

                            if coverage >= state.GAME_MIN_COVERAGE:
                                print(
                                    f"[GAME] Shooting for {tpl['name']} "
                                    f"(coverage={coverage:.2f}, dist≤{state.GAME_COLOR_DIST})"
                                )
                                state.ignore_recording = True
                                state.global_last_click = time.time()
                                safe_click()
                                state.ignore_recording = False

                                t_now = time.time()
                                tpl["last_click"] = t_now
                                tpl["clicks"] = tpl.get("clicks", 0) + 1
                                state.last_target_seen = t_now

                else:
                    # ---------- NORMAL / GHOST MODE ----------
                    screen_pil = pyautogui.screenshot()
                    screen_np = np.array(screen_pil)
                    screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)

                    screen_small = downscale_gray(screen_gray, state.DOWNSCALE)
                    Hs, Ws = screen_small.shape

                    for tpl in list(state.templates):
                        if not tpl.get("enabled", True):
                            continue

                        if time.time() - tpl["last_click"] < eff_cd:
                            continue

                        tpl_small = downscale_gray(tpl["img"], state.DOWNSCALE)
                        th_s, tw_s = tpl_small.shape

                        if th_s > Hs or tw_s > Ws:
                            continue

                        res = cv2.matchTemplate(
                            screen_small, tpl_small, cv2.TM_CCOEFF_NORMED
                        )
                        loc = np.where(res >= state.MATCH_THRESHOLD)

                        found = False
                        for pt_y, pt_x in zip(*loc):
                            cx_s = pt_x + tw_s // 2
                            cy_s = pt_y + th_s // 2

                            center_x = int(cx_s * state.DOWNSCALE)
                            center_y = int(cy_s * state.DOWNSCALE)

                            jx = jy = 0
                            if state.jitter_mode and not state.ghost_mode:
                                jx = random.randint(-2, 2)
                                jy = random.randint(-2, 2)

                            print(
                                f"[AUTO] Match for {tpl['name']} "
                                f"at ({center_x}, {center_y}), ghost={state.ghost_mode}"
                            )

                            state.ignore_recording = True

                            if state.ghost_mode:
                                old_x, old_y = pyautogui.position()
                                pyautogui.moveTo(center_x, center_y, duration=0.0)
                                state.global_last_click = time.time()
                                safe_click()
                                pyautogui.moveTo(old_x, old_y, duration=0.0)
                            else:
                                pyautogui.moveTo(
                                    center_x + jx,
                                    center_y + jy,
                                    duration=state.MOUSE_MOVE_DURATION,
                                )
                                state.global_last_click = time.time()
                                safe_click()

                            state.ignore_recording = False

                            t_now = time.time()
                            tpl["last_click"] = t_now
                            tpl["clicks"] = tpl.get("clicks", 0) + 1
                            state.last_target_seen = t_now
                            found = True
                            break

                        if found:
                            break

                # ---------- ADAPTIVE DELAY ----------
                base_delay = max(0.0, 0.02 - (state.scan_speed - 1) * 0.0025)

                if state.adaptive_scan:
                    # if we saw a target very recently -> scan super fast
                    if now - state.last_target_seen < 0.3:
                        base_delay = 0.0       # spam scan while enemy visible
                    else:
                        base_delay = 0.04      # slow/chill scan when no recent enemy

                eff_delay = 0.0 if state.speed_mode == "fast" else base_delay
                time.sleep(eff_delay)

            else:
                time.sleep(0.01)

        except pyautogui.FailSafeException:
            print("[WARN] PyAutoGUI FAILSAFE. Exiting auto loop.")
            state.running = False
            break
        except KeyboardInterrupt:
            print("[INFO] KeyboardInterrupt in auto loop, exiting.")
            state.running = False
            break
        except Exception as e:
            print(f"[ERROR] auto_click_loop exception: {e}")
            time.sleep(0.02)
