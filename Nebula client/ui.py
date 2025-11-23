import threading
import os

import keyboard
import tkinter as tk
from PIL import Image, ImageTk

import state
import capture
import auto
import mouse_listener


# UI colors
BG = "#020308"
CARD = "#050711"
TEXT = "#f5f7ff"
ACCENT = "#5be6b6"
ACCENT2 = "#6ca8ff"
DANGER = "#ff4f6b"
MUTED = "#8087a0"
OUTLINE = "#1a2033"


def main():
    print("=== NEBULA CLIENT | Visual Multi-Target Clicker ===")
    print("F8  = start/stop recording (left-click targets to add them)")
    print("TAB = snapshot center of screen (for gamemode)")
    print("9   = AUTO-CLICK ON")
    print("0   = AUTO-CLICK OFF (pause)")
    print("ESC = quit script")
    print("---------------------------------------------")
    print("[INFO] Game mode: center-only shooting.")
    print("[INFO] FAST game mode: single pixel color at crosshair.")
    print("[INFO] Simplify: uses average color (game mode).")
    print("[INFO] Speed mode NORMAL = legit, FAST = rage.")
    print("[INFO] Optimized Mode: pops up when you enable Crosshair Mode.\n")

    capture.load_existing_templates()

    # Threads: mouse listener + auto loop
    t_mouse = threading.Thread(
        target=mouse_listener.mouse_listener_thread, daemon=True
    )
    t_mouse.start()

    t_auto = threading.Thread(target=auto.auto_click_loop, daemon=True)
    t_auto.start()

    # ---------- TK UI ----------
    root = tk.Tk()
    root.title("NEBULA CLIENT | Visual Assist")
    root.configure(bg=BG)
    root.attributes("-topmost", True)
    root.resizable(False, False)
    root.geometry("+40+40")

    outer = tk.Frame(root, bg=BG, bd=0)
    outer.pack(padx=6, pady=6)

    card = tk.Frame(
        outer, bg=CARD, bd=0,
        highlightthickness=1, highlightbackground=OUTLINE
    )
    card.pack(fill="both", expand=True)

    # Header
    header = tk.Frame(card, bg="#040612")
    header.pack(fill="x")

    title_left = tk.Label(
        header,
        text="NEBULA CLIENT",
        bg="#040612",
        fg=ACCENT,
        font=("Consolas", 12, "bold"),
    )
    title_left.pack(side="left", padx=8, pady=4)

    title_mid = tk.Label(
        header,
        text="VISUAL ASSIST · LEGIT / RAGE / OPT",
        bg="#040612",
        fg=MUTED,
        font=("Consolas", 8),
    )
    title_mid.pack(side="left", padx=6, pady=4)

    title_right = tk.Label(
        header,
        text="INJECTED",
        bg="#040612",
        fg=ACCENT2,
        font=("Consolas", 8, "bold"),
    )
    title_right.pack(side="right", padx=8, pady=4)

    # Status bar
    status_bar = tk.Frame(card, bg=CARD)
    status_bar.pack(fill="x", pady=(2, 4))

    record_var = tk.StringVar()
    auto_var = tk.StringVar()

    lbl_record = tk.Label(
        status_bar, textvariable=record_var,
        bg=CARD, fg=ACCENT, font=("Consolas", 8)
    )
    lbl_record.pack(side="left", padx=(8, 4))

    lbl_auto = tk.Label(
        status_bar, textvariable=auto_var,
        bg=CARD, fg=ACCENT2, font=("Consolas", 8)
    )
    lbl_auto.pack(side="left", padx=4)

    # Layout: left (modules) / right (targets)
    body = tk.Frame(card, bg=CARD)
    body.pack(fill="both", expand=True, padx=6, pady=4)

    left_panel = tk.Frame(body, bg=CARD)
    left_panel.pack(side="left", fill="y", padx=(0, 4))

    right_panel = tk.Frame(body, bg=CARD)
    right_panel.pack(side="right", fill="both", expand=True, padx=(4, 0))

    def section_label(parent, text):
        return tk.Label(
            parent,
            text=text,
            bg=CARD,
            fg=MUTED,
            font=("Consolas", 8, "bold"),
            anchor="w",
        )

    def style_btn(btn, danger=False):
        btn.configure(
            bg="#090c19" if not danger else "#1b0b11",
            fg=TEXT,
            activebackground=ACCENT2 if not danger else DANGER,
            activeforeground=TEXT,
            bd=0,
            relief="flat",
            font=("Consolas", 8),
            padx=10,
            pady=4,
            cursor="hand2",
        )

    # ---------- LEFT: COMBAT / AIM ----------
    section_label(left_panel, "COMBAT / AIM").pack(
        anchor="w", pady=(0, 2), padx=2
    )

    btn_row1 = tk.Frame(left_panel, bg=CARD)
    btn_row1.pack(anchor="w")

    def ui_toggle_recording():
        state.recording = not state.recording
        print(f"[MODE] RECORDING {'ON' if state.recording else 'OFF'}")

    def ui_auto_on():
        if not state.auto_enabled:
            state.auto_enabled = True
            print("[MODE] AUTO-CLICK ON")

    def ui_auto_off():
        if state.auto_enabled:
            state.auto_enabled = False
            print("[MODE] AUTO-CLICK OFF")

    def ui_center_snapshot():
        print("[MODE] Snapshot center (TAB equivalent)")
        capture.record_center_template()

    btn_record = tk.Button(
        btn_row1, text="RECORDER [F8]", command=ui_toggle_recording
    )
    style_btn(btn_record)
    btn_record.grid(row=0, column=0, padx=(0, 4), pady=(0, 2))

    btn_center = tk.Button(
        btn_row1, text="SET CROSSHAIR [TAB]", command=ui_center_snapshot
    )
    style_btn(btn_center)
    btn_center.grid(row=0, column=1, padx=(0, 0), pady=(0, 2))

    btn_row2 = tk.Frame(left_panel, bg=CARD)
    btn_row2.pack(anchor="w")

    btn_auto_on = tk.Button(btn_row2, text="LEGIT ON [9]", command=ui_auto_on)
    style_btn(btn_auto_on)
    btn_auto_on.grid(row=0, column=0, padx=(0, 4), pady=(0, 2))

    btn_auto_off = tk.Button(btn_row2, text="PANIC OFF [0]", command=ui_auto_off)
    style_btn(btn_auto_off, danger=True)
    btn_auto_off.grid(row=0, column=1, padx=(0, 0), pady=(0, 2))

    # ---------- LEFT: MOVEMENT / GAMEPLAY (compact) ----------
    section_label(left_panel, "AIM / GAMEPLAY").pack(
        anchor="w", pady=(6, 2), padx=2
    )

    settings_frame = tk.Frame(left_panel, bg=CARD)
    settings_frame.pack(anchor="w")

    # core sliders (kept in main window)
    sensitivity_var = tk.DoubleVar(value=state.MATCH_THRESHOLD)
    speed_var = tk.DoubleVar(value=state.scan_speed)

    # toggles
    ghost_var = tk.BooleanVar(value=state.ghost_mode)
    game_var = tk.BooleanVar(value=state.gamemode)
    simplify_var = tk.BooleanVar(value=state.simplify_mode)
    speed_mode_var = tk.StringVar(value=state.speed_mode)
    jitter_var = tk.BooleanVar(value=state.jitter_mode)
    adaptive_var = tk.BooleanVar(value=state.adaptive_scan)  # NEW

    # advanced values (config window)
    move_var = tk.DoubleVar(value=state.MOUSE_MOVE_DURATION)
    fov_var = tk.IntVar(value=state.CENTER_BOX_HALF)
    color_dist_var = tk.DoubleVar(value=state.GAME_COLOR_DIST)
    coverage_var = tk.DoubleVar(value=state.GAME_MIN_COVERAGE * 100.0)
    cps_var = tk.DoubleVar(value=round(1.0 / state.GLOBAL_MIN_CLICK_GAP))

    def on_sensitivity_change(value):
        state.MATCH_THRESHOLD = float(value)
        print(f"[SET] Sensitivity = {state.MATCH_THRESHOLD:.2f}")

    def on_speed_change(value):
        state.scan_speed = float(value)
        print(f"[SET] Scan speed = {state.scan_speed:.1f}")

    def on_move_change(value):
        state.MOUSE_MOVE_DURATION = float(value)
        print(f"[SET] Move duration = {state.MOUSE_MOVE_DURATION:.3f}s")

    def on_ghost_toggle():
        state.ghost_mode = ghost_var.get()
        print(f"[SET] Ghost mode = {state.ghost_mode}")

    def on_simplify_toggle():
        state.simplify_mode = simplify_var.get()
        print(f"[SET] Simplify color = {state.simplify_mode}")

    def on_speed_mode_change():
        state.speed_mode = speed_mode_var.get()
        print(f"[SET] Speed mode = {state.speed_mode}")

    def on_jitter_toggle():
        state.jitter_mode = jitter_var.get()
        print(f"[SET] Jitter Aim = {state.jitter_mode}")

    def on_adaptive_toggle():
        state.adaptive_scan = adaptive_var.get()
        print(f"[SET] Adaptive scan mode = {state.adaptive_scan}")

    def on_fov_change(value):
        state.CENTER_BOX_HALF = int(float(value))
        print(f"[SET] Game FOV half = {state.CENTER_BOX_HALF}")

    def on_color_dist_change(value):
        state.GAME_COLOR_DIST = float(value)
        print(f"[SET] Color strictness = {state.GAME_COLOR_DIST:.1f}")

    def on_coverage_change(value):
        state.GAME_MIN_COVERAGE = float(value) / 100.0
        print(f"[SET] Coverage = {state.GAME_MIN_COVERAGE:.2f}")

    def on_cps_change(value):
        cps = max(1.0, float(value))
        state.GLOBAL_MIN_CLICK_GAP = 1.0 / cps
        print(
            f"[SET] Global CPS limit = {cps:.1f} "
            f"(gap={state.GLOBAL_MIN_CLICK_GAP:.3f}s)"
        )

    def show_optimized_popup():
        popup = tk.Toplevel(root)
        popup.title("Optimized Mode")
        popup.configure(bg=CARD)
        popup.attributes("-topmost", True)
        popup.resizable(False, False)

        msg = tk.Label(
            popup,
            text=(
                "Enable OPTIMIZED Crosshair Mode?\n\n"
                "- Mouse never moves (click-only)\n"
                "- Single pixel checks at crosshair\n"
                "- Forces RAGE + Ghost + Simplify\n"
                "- Higher CPS & scan speed\n"
                "- Adaptive scan = fast only on enemies"
            ),
            bg=CARD,
            fg=TEXT,
            font=("Consolas", 8),
            justify="left",
            padx=10,
            pady=10,
        )
        msg.pack()

        btn_frame = tk.Frame(popup, bg=CARD)
        btn_frame.pack(pady=(0, 10))

        def enable_opt():
            state.optimized_mode = True
            speed_mode_var.set("fast")
            state.speed_mode = "fast"
            ghost_var.set(True)
            state.ghost_mode = True
            simplify_var.set(True)
            state.simplify_mode = True
            cps_var.set(25)
            on_cps_change(25)
            speed_var.set(9)
            on_speed_change(9)

            # NEW: also enable adaptive scan
            adaptive_var.set(True)
            state.adaptive_scan = True

            print("[OPT] Optimized Mode ENABLED (with adaptive scan)")
            popup.destroy()

        def skip_opt():
            state.optimized_mode = False
            print("[OPT] Optimized Mode skipped")
            popup.destroy()

        btn_yes = tk.Button(btn_frame, text="ENABLE", command=enable_opt)
        style_btn(btn_yes)
        btn_yes.grid(row=0, column=0, padx=4)

        btn_no = tk.Button(btn_frame, text="SKIP", command=skip_opt)
        style_btn(btn_no, danger=True)
        btn_no.grid(row=0, column=1, padx=4)

    def on_game_toggle():
        before = state.gamemode
        state.gamemode = game_var.get()
        print(f"[SET] Game mode (crosshair) = {state.gamemode}")
        if state.gamemode and not before:
            show_optimized_popup()

    # core sliders in main window
    lbl_sens = tk.Label(
        settings_frame,
        text="Aim Assist:",
        bg=CARD,
        fg=MUTED,
        font=("Consolas", 8),
    )
    lbl_sens.grid(row=0, column=0, sticky="w")

    sens_scale = tk.Scale(
        settings_frame,
        from_=0.65,
        to=0.95,
        resolution=0.01,
        orient="horizontal",
        variable=sensitivity_var,
        command=on_sensitivity_change,
        showvalue=True,
        length=130,
        bg=CARD,
        fg=TEXT,
        highlightthickness=0,
        troughcolor="#090c19",
        sliderrelief="flat",
    )
    sens_scale.grid(row=0, column=1, padx=(4, 0))

    lbl_speed = tk.Label(
        settings_frame,
        text="Scan CPS:",
        bg=CARD,
        fg=MUTED,
        font=("Consolas", 8),
    )
    lbl_speed.grid(row=1, column=0, sticky="w")

    speed_scale = tk.Scale(
        settings_frame,
        from_=1,
        to=10,
        resolution=1,
        orient="horizontal",
        variable=speed_var,
        command=on_speed_change,
        showvalue=True,
        length=130,
        bg=CARD,
        fg=TEXT,
        highlightthickness=0,
        troughcolor="#090c19",
        sliderrelief="flat",
    )
    speed_scale.grid(row=1, column=1, padx=(4, 0), pady=(2, 0))

    # toggles row (compact)
    toggles_frame = tk.Frame(left_panel, bg=CARD)
    toggles_frame.pack(anchor="w", pady=(4, 0))

    ghost_check = tk.Checkbutton(
        toggles_frame,
        text="Ghost Click",
        variable=ghost_var,
        command=on_ghost_toggle,
        bg=CARD,
        fg=TEXT,
        activebackground=CARD,
        activeforeground=TEXT,
        selectcolor="#090c19",
        font=("Consolas", 8),
        padx=0,
    )
    ghost_check.grid(row=0, column=0, sticky="w")

    game_check = tk.Checkbutton(
        toggles_frame,
        text="Crosshair Mode",
        variable=game_var,
        command=on_game_toggle,
        bg=CARD,
        fg=TEXT,
        activebackground=CARD,
        activeforeground=TEXT,
        selectcolor="#090c19",
        font=("Consolas", 8),
        padx=0,
    )
    game_check.grid(row=1, column=0, sticky="w")

    simplify_check = tk.Checkbutton(
        toggles_frame,
        text="Simplify Color",
        variable=simplify_var,
        command=on_simplify_toggle,
        bg=CARD,
        fg=TEXT,
        activebackground=CARD,
        activeforeground=TEXT,
        selectcolor="#090c19",
        font=("Consolas", 8),
        padx=0,
    )
    simplify_check.grid(row=2, column=0, sticky="w")

    jitter_check = tk.Checkbutton(
        toggles_frame,
        text="Jitter Aim",
        variable=jitter_var,
        command=on_jitter_toggle,
        bg=CARD,
        fg=TEXT,
        activebackground=CARD,
        activeforeground=TEXT,
        selectcolor="#090c19",
        font=("Consolas", 8),
        padx=0,
    )
    jitter_check.grid(row=3, column=0, sticky="w")

    adaptive_check = tk.Checkbutton(
        toggles_frame,
        text="OPT Scan Mode",
        variable=adaptive_var,
        command=on_adaptive_toggle,
        bg=CARD,
        fg=TEXT,
        activebackground=CARD,
        activeforeground=TEXT,
        selectcolor="#090c19",
        font=("Consolas", 8),
        padx=0,
    )
    adaptive_check.grid(row=4, column=0, sticky="w")

    # Speed mode: LEGIT / RAGE
    speedmode_frame = tk.Frame(left_panel, bg=CARD)
    speedmode_frame.pack(anchor="w", pady=(6, 0))

    speedmode_label = tk.Label(
        speedmode_frame,
        text="MODE:",
        bg=CARD,
        fg=MUTED,
        font=("Consolas", 8, "bold"),
    )
    speedmode_label.grid(row=0, column=0, sticky="w")

    def on_speed_mode_change_wrapper():
        on_speed_mode_change()

    rb_normal = tk.Radiobutton(
        speedmode_frame,
        text="LEGIT",
        variable=speed_mode_var,
        value="normal",
        command=on_speed_mode_change_wrapper,
        bg=CARD,
        fg=ACCENT,
        activebackground=CARD,
        activeforeground=ACCENT,
        selectcolor="#090c19",
        font=("Consolas", 8),
        padx=2,
    )
    rb_normal.grid(row=0, column=1, sticky="w")

    rb_fast = tk.Radiobutton(
        speedmode_frame,
        text="RAGE",
        variable=speed_mode_var,
        value="fast",
        command=on_speed_mode_change_wrapper,
        bg=CARD,
        fg=DANGER,
        activebackground=CARD,
        activeforeground=DANGER,
        selectcolor="#090c19",
        font=("Consolas", 8),
        padx=2,
    )
    rb_fast.grid(row=0, column=2, sticky="w")

    # ---------- CONFIG WINDOW BUTTON ----------
    config_window_holder = {"win": None}

    def open_config_window():
        # prevent multiple config windows
        if config_window_holder["win"] is not None:
            try:
                config_window_holder["win"].lift()
                return
            except tk.TclError:
                config_window_holder["win"] = None

        win = tk.Toplevel(root)
        config_window_holder["win"] = win
        win.title("NEBULA CONFIG")
        win.configure(bg=CARD)
        win.resizable(False, False)
        win.attributes("-topmost", True)

        cfg_frame = tk.Frame(win, bg=CARD)
        cfg_frame.pack(padx=8, pady=8)

        # Mouse move
        tk.Label(
            cfg_frame,
            text="Mouse Move duration:",
            bg=CARD,
            fg=MUTED,
            font=("Consolas", 8),
        ).grid(row=0, column=0, sticky="w")

        move_scale = tk.Scale(
            cfg_frame,
            from_=0.0,
            to=0.10,
            resolution=0.005,
            orient="horizontal",
            variable=move_var,
            command=on_move_change,
            showvalue=True,
            length=160,
            bg=CARD,
            fg=TEXT,
            highlightthickness=0,
            troughcolor="#090c19",
            sliderrelief="flat",
        )
        move_scale.grid(row=0, column=1, padx=(6, 0), pady=(2, 4))

        # FOV
        tk.Label(
            cfg_frame,
            text="Game FOV (half box):",
            bg=CARD,
            fg=MUTED,
            font=("Consolas", 8),
        ).grid(row=1, column=0, sticky="w")

        fov_scale = tk.Scale(
            cfg_frame,
            from_=20,
            to=120,
            resolution=5,
            orient="horizontal",
            variable=fov_var,
            command=on_fov_change,
            showvalue=True,
            length=160,
            bg=CARD,
            fg=TEXT,
            highlightthickness=0,
            troughcolor="#090c19",
            sliderrelief="flat",
        )
        fov_scale.grid(row=1, column=1, padx=(6, 0), pady=(2, 4))

        # Color strictness
        tk.Label(
            cfg_frame,
            text="Color strictness:",
            bg=CARD,
            fg=MUTED,
            font=("Consolas", 8),
        ).grid(row=2, column=0, sticky="w")

        color_scale = tk.Scale(
            cfg_frame,
            from_=10,
            to=80,
            resolution=1,
            orient="horizontal",
            variable=color_dist_var,
            command=on_color_dist_change,
            showvalue=True,
            length=160,
            bg=CARD,
            fg=TEXT,
            highlightthickness=0,
            troughcolor="#090c19",
            sliderrelief="flat",
        )
        color_scale.grid(row=2, column=1, padx=(6, 0), pady=(2, 4))

        # Coverage
        tk.Label(
            cfg_frame,
            text="Coverage % (strict):",
            bg=CARD,
            fg=MUTED,
            font=("Consolas", 8),
        ).grid(row=3, column=0, sticky="w")

        coverage_scale = tk.Scale(
            cfg_frame,
            from_=10,
            to=90,
            resolution=5,
            orient="horizontal",
            variable=coverage_var,
            command=on_coverage_change,
            showvalue=True,
            length=160,
            bg=CARD,
            fg=TEXT,
            highlightthickness=0,
            troughcolor="#090c19",
            sliderrelief="flat",
        )
        coverage_scale.grid(row=3, column=1, padx=(6, 0), pady=(2, 4))

        # CPS
        tk.Label(
            cfg_frame,
            text="Global CPS limit:",
            bg=CARD,
            fg=MUTED,
            font=("Consolas", 8),
        ).grid(row=4, column=0, sticky="w")

        cps_scale = tk.Scale(
            cfg_frame,
            from_=5,
            to=35,
            resolution=1,
            orient="horizontal",
            variable=cps_var,
            command=on_cps_change,
            showvalue=True,
            length=160,
            bg=CARD,
            fg=TEXT,
            highlightthickness=0,
            troughcolor="#090c19",
            sliderrelief="flat",
        )
        cps_scale.grid(row=4, column=1, padx=(6, 0), pady=(2, 6))

        def on_cfg_close():
            config_window_holder["win"] = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_cfg_close)

    # CONFIG button
    cfg_btn = tk.Button(left_panel, text="[ CONFIG ]", command=open_config_window)
    style_btn(cfg_btn)
    cfg_btn.pack(anchor="w", pady=(6, 0), padx=2)

    # ---------- RIGHT: TARGETS + PREVIEW ----------
    targets_header = tk.Frame(right_panel, bg=CARD)
    targets_header.pack(fill="x")

    lbl_targets = tk.Label(
        targets_header,
        text="TARGETS",
        bg=CARD,
        fg=MUTED,
        font=("Consolas", 8, "bold"),
        anchor="w",
    )
    lbl_targets.pack(side="left", padx=(0, 2))

    mid_frame = tk.Frame(right_panel, bg=CARD)
    mid_frame.pack(fill="both", expand=True)

    list_frame = tk.Frame(mid_frame, bg=CARD)
    list_frame.pack(side="left", fill="both", expand=True, padx=(0, 4))

    lst_targets = tk.Listbox(
        list_frame,
        bg="#050611",
        fg=TEXT,
        selectbackground=ACCENT2,
        selectforeground=TEXT,
        font=("Consolas", 8),
        height=10,
        activestyle="dotbox",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=OUTLINE,
    )
    lst_targets.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=lst_targets.yview)
    scrollbar.pack(side="right", fill="y")
    lst_targets.config(yscrollcommand=scrollbar.set)

    preview_frame = tk.Frame(mid_frame, bg=CARD)
    preview_frame.pack(side="right", fill="y")

    preview_label = tk.Label(
        preview_frame,
        text="Preview",
        bg=CARD,
        fg=MUTED,
        font=("Consolas", 8),
    )
    preview_label.pack(anchor="n", pady=(0, 2))

    preview_canvas = tk.Label(preview_frame, bg="#050611")
    preview_canvas.pack(padx=2, pady=2)

    preview_image_ref = {"img": None}

    bottom_targets = tk.Frame(right_panel, bg=CARD)
    bottom_targets.pack(anchor="w", pady=(4, 0))

    def refresh_targets_list(preserve_selection=True):
        sel = lst_targets.curselection()
        selected_index = sel[0] if sel else None

        lst_targets.delete(0, tk.END)
        for tpl in state.templates:
            status = "ON" if tpl.get("enabled", True) else "OFF"
            clicks = tpl.get("clicks", 0)
            lst_targets.insert(
                tk.END,
                f"{tpl['name']} [{status}] {tpl['w']}x{tpl['h']} • {clicks} hits",
            )

        if (
            preserve_selection
            and selected_index is not None
            and selected_index < len(state.templates)
        ):
            lst_targets.select_set(selected_index)
            lst_targets.event_generate("<<ListboxSelect>>")

    def update_preview(*args):
        sel = lst_targets.curselection()
        if not sel:
            preview_canvas.config(image="", text="")
            preview_image_ref["img"] = None
            return
        idx = sel[0]
        if idx < 0 or idx >= len(state.templates):
            return
        tpl = state.templates[idx]
        try:
            img = Image.open(tpl["path"]).convert("RGB")
            img = img.resize((96, 96), Image.NEAREST)
            tk_img = ImageTk.PhotoImage(img)
            preview_canvas.config(image=tk_img)
            preview_canvas.image = tk_img
            preview_image_ref["img"] = tk_img
        except Exception:
            preview_canvas.config(image="", text="(no image)")
            preview_image_ref["img"] = None

    lst_targets.bind("<<ListboxSelect>>", update_preview)

    def ui_delete_selected():
        sel = lst_targets.curselection()
        if not sel:
            return
        for idx in reversed(sel):
            tpl = state.templates[idx]
            print(f"[DELETE] Removing {tpl['name']}")
            try:
                if os.path.exists(tpl["path"]):
                    os.remove(tpl["path"])
            except Exception:
                pass
            state.templates.pop(idx)
        refresh_targets_list(preserve_selection=False)
        update_preview()

    def ui_clear_all():
        print("[CLEAR] Removing all targets")
        state.templates = []
        try:
            for fname in os.listdir(state.TEMPLATE_DIR):
                if fname.lower().endswith(".png"):
                    os.remove(os.path.join(state.TEMPLATE_DIR, fname))
        except Exception:
            pass
        refresh_targets_list(preserve_selection=False)
        update_preview()

    def ui_toggle_selected():
        sel = lst_targets.curselection()
        if not sel:
            return
        for idx in sel:
            tpl = state.templates[idx]
            tpl["enabled"] = not tpl.get("enabled", True)
            state_txt = "ON" if tpl["enabled"] else "OFF"
            print(f"[TOGGLE] {tpl['name']} -> {state_txt}")
        refresh_targets_list()

    btn_delete = tk.Button(bottom_targets, text="DEL", command=ui_delete_selected)
    style_btn(btn_delete, danger=True)
    btn_delete.grid(row=0, column=0, padx=(0, 4), pady=(0, 2))

    btn_clear = tk.Button(bottom_targets, text="WIPE", command=ui_clear_all)
    style_btn(btn_clear, danger=True)
    btn_clear.grid(row=0, column=1, padx=(0, 4), pady=(0, 2))

    btn_toggle = tk.Button(bottom_targets, text="TOGGLE", command=ui_toggle_selected)
    style_btn(btn_toggle)
    btn_toggle.grid(row=0, column=2, padx=(0, 0), pady=(0, 2))

    # footer
    hint = tk.Label(
        card,
        text="F8=REC  TAB=CROSSHAIR  9=LEGIT ON  0=PANIC  DEL=Delete Target  ESC=UNINJECT",
        bg=CARD,
        fg=MUTED,
        font=("Consolas", 7),
    )
    hint.pack(anchor="w", padx=6, pady=(2, 4))

    watermark = tk.Label(
        card, text="nebula.client", bg=CARD, fg="#3e4660", font=("Consolas", 7)
    )
    watermark.place(relx=1.0, rely=1.0, x=-8, y=-4, anchor="se")

    # keyboard polling
    key_state = {"f8": False, "9": False, "0": False, "tab": False}

    def update_status_labels():
        record_var.set("[RECORDER] ON" if state.recording else "[RECORDER] OFF")
        auto_var.set("[AIMBOT] ACTIVE" if state.auto_enabled else "[AIMBOT] IDLE")

    def poll_hotkeys():
        if not state.running:
            try:
                root.destroy()
            except tk.TclError:
                pass
            return

        if keyboard.is_pressed("esc"):
            print("[INFO] ESC pressed. Exiting.")
            state.running = False
            try:
                root.destroy()
            except tk.TclError:
                pass
            return

        cur_f8 = keyboard.is_pressed("f8")
        if cur_f8 and not key_state["f8"]:
            state.recording = not state.recording
            print(f"[MODE] RECORDING {'ON' if state.recording else 'OFF'}")
        key_state["f8"] = cur_f8

        cur_tab = keyboard.is_pressed("tab")
        if cur_tab and not key_state["tab"]:
            print("[HOTKEY] TAB -> snapshot center")
            capture.record_center_template()
        key_state["tab"] = cur_tab

        cur_9 = keyboard.is_pressed("9")
        if cur_9 and not key_state["9"]:
            if not state.auto_enabled:
                state.auto_enabled = True
                print("[MODE] AUTO-CLICK ON")
        key_state["9"] = cur_9

        cur_0 = keyboard.is_pressed("0")
        if cur_0 and not key_state["0"]:
            if state.auto_enabled:
                state.auto_enabled = False
                print("[MODE] AUTO-CLICK OFF")
        key_state["0"] = cur_0

        if keyboard.is_pressed("delete"):
            ui_delete_selected()

        update_status_labels()
        refresh_targets_list()
        root.after(80, poll_hotkeys)

    def on_close():
        state.running = False
        try:
            root.destroy()
        except tk.TclError:
            pass

    root.protocol("WM_DELETE_WINDOW", on_close)

    update_status_labels()
    refresh_targets_list(preserve_selection=False)
    root.after(80, poll_hotkeys)
    root.mainloop()

    print("[INFO] Shutting down...")
