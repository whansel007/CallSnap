# Main program that cointains the settings
import ctypes
import tkinter as tk
from tkinter import messagebox, ttk
import keyboard
import whitelist as wl
from name_detector import NameDetectorGUI


# Get a refference to user32.dll file
user32 = ctypes.windll.user32
    # dll is Dynamic Link Library containing window functions that other processes can call 
    # user32.dll is responsible for user-interface and window-management API: creating windows, keyboard and mouse input, dialog, menus, and other core UI

WM_COMMAND = 0x0111 # Code to indicate that the message sent is a COMMAND!
MINIMIZE_ALL = 419 # Command code to MINIMIZE_ALL

def minimize_all():
    # Return the Shell_TrayWnd window that handles global shell commands, otherwise return None
    shell = user32.FindWindowW("Shell_TrayWnd", None)

    if shell:
        user32.SendMessageW(shell, WM_COMMAND, MINIMIZE_ALL, 0)

# UI ===
root = tk.Tk()
root.title("CallSnap")
root.geometry("750x600")
root.configure(bg="#f3f1ed")

main_frame = tk.Frame(root, bg="#f3f1ed")
main_frame.pack(fill="both", expand=True, padx=24, pady=(24, 16))

header_frame = tk.Frame(main_frame, bg="#f3f1ed")
header_frame.pack(fill="x", pady=(0, 12))

title_label = tk.Label(
    header_frame,
    text="CallSnap",
    font=("Georgia", 22, "bold"),
    bg="#f3f1ed",
    fg="#2d2a26",
)
title_label.pack(anchor="w")

subtitle_label = tk.Label(
    header_frame,
    text="Minimize distractions and alert you when your name is mentioned on calls.",
    font=("Georgia", 11),
    bg="#f3f1ed",
    fg="#5f5a54",
    wraplength=460,
    justify="left",
)
subtitle_label.pack(anchor="w", pady=(6, 0))

actions_frame = tk.Frame(main_frame, bg="#f3f1ed")
actions_frame.pack(fill="x", pady=(0, 16))

detector_app = None
keybind_window = None
keybind_vars = {}
keybind_actions = {}
keybind_labels = {}
keybind_hotkeys = {}

def open_detector_settings():
    if detector_app:
        detector_app.open_settings_window()

def apply_keybinds():
    for action_name, action in keybind_actions.items():
        entry = keybind_vars[action_name]
        sequence = entry.get().strip()
        previous = keybind_labels[action_name].get("current", "")
        try:
            if previous:
                hotkey_id = keybind_hotkeys.pop(action_name, None)
                if hotkey_id:
                    keyboard.remove_hotkey(hotkey_id)
            if sequence:
                hotkey_id = keyboard.add_hotkey(
                    sequence,
                    lambda fn=action: root.after(0, fn),
                )
                keybind_hotkeys[action_name] = hotkey_id
            keybind_labels[action_name]["current"] = sequence
        except Exception as exc:
            messagebox.showerror("Invalid key binding", str(exc))
            return

    messagebox.showinfo("Key bindings", "Key bindings updated.")

def open_keybind_settings():
    global keybind_window
    if keybind_window and keybind_window.winfo_exists():
        keybind_window.lift()
        keybind_window.focus_force()
        return

    keybind_window = tk.Toplevel(root)
    keybind_window.title("Key Bindings")
    keybind_window.geometry("520x260")
    keybind_window.configure(bg="#f3f1ed")

    frame = tk.Frame(keybind_window, bg="#f3f1ed")
    frame.pack(fill="both", expand=True, padx=20, pady=16)

    header = tk.Label(
        frame,
        text="Configure Key Bindings",
        font=("Georgia", 14, "bold"),
        bg="#f3f1ed",
        fg="#2d2a26",
    )
    header.pack(anchor="w")

    hint = tk.Label(
        frame,
        text="Use sequences like ctrl+shift+m or alt+m.",
        font=("Georgia", 9),
        bg="#f3f1ed",
        fg="#5f5a54",
    )
    hint.pack(anchor="w", pady=(4, 12))

    form = tk.Frame(frame, bg="#f3f1ed")
    form.pack(fill="x")

    for row, action_name in enumerate(keybind_actions):
        label = tk.Label(
            form,
            text=action_name,
            font=("Segoe UI", 10),
            bg="#f3f1ed",
            fg="#2d2a26",
        )
        label.grid(row=row, column=0, sticky="w", pady=6)

        entry = tk.Entry(form, textvariable=keybind_vars[action_name], width=36)
        entry.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=6)

    form.columnconfigure(1, weight=1)

    button_row = tk.Frame(frame, bg="#f3f1ed")
    button_row.pack(fill="x", pady=(16, 0))

    apply_btn = tk.Button(
        button_row,
        text="Apply",
        command=apply_keybinds,
        font=("Segoe UI", 10, "bold"),
        bg="#f7d070",
        fg="#2d2a26",
        activebackground="#e7c15f",
        relief="flat",
    )
    apply_btn.pack(side="right")

utility_label = tk.Label(
    actions_frame,
    text="Utilities",
    font=("Georgia", 12, "bold"),
    bg="#f3f1ed",
    fg="#2d2a26",
)
utility_label.pack(anchor="w", pady=(0, 6))

grid_frame = tk.Frame(actions_frame, bg="#f3f1ed")
grid_frame.pack(fill="x")
grid_frame.columnconfigure(0, weight=1, uniform="utility")
grid_frame.columnconfigure(1, weight=1, uniform="utility")

minimize_btn = tk.Button(
    grid_frame,
    text="Minimize All Apps",
    command=minimize_all,
    font=("Segoe UI", 11, "bold"),
    bg="#f7d070",
    fg="#2d2a26",
    activebackground="#e7c15f",
    relief="flat",
)
minimize_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))

detector_settings_btn = tk.Button(
    grid_frame,
    text="Open Detector Settings",
    command=open_detector_settings,
    font=("Segoe UI", 10),
    bg="#e6e2dc",
    fg="#2d2a26",
    activebackground="#d7d1ca",
    relief="flat",
)
detector_settings_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 8))

minimize_whitelist_btn = tk.Button(
    grid_frame,
    text="Minimize Excluding Whitelist",
    command=wl.minmaxPrograms,
    font=("Segoe UI", 10),
    bg="#e6e2dc",
    fg="#2d2a26",
    activebackground="#d7d1ca",
    relief="flat",
)
minimize_whitelist_btn.grid(row=1, column=0, sticky="ew", padx=(0, 8))

whitelist_btn = tk.Button(
    grid_frame,
    text="Whitelist Programs Setting",
    command=lambda: wl.openWhitelistUI(root),
    font=("Segoe UI", 10),
    bg="#e6e2dc",
    fg="#2d2a26",
    activebackground="#d7d1ca",
    relief="flat",
)
whitelist_btn.grid(row=1, column=1, sticky="ew", padx=(8, 0))

detector_container = tk.Frame(main_frame, bg="#f3f1ed")
detector_app = NameDetectorGUI(detector_container, configure_window=False, show_settings=False)
detector_container.pack(fill="both", expand=True)

keybind_actions = {
    "Minimize All Apps": minimize_all,
    "Minimize Excluding Whitelist": wl.minmaxPrograms,
}
keybind_vars = {name: tk.StringVar(value="") for name in keybind_actions}
keybind_labels = {name: {"current": ""} for name in keybind_actions}

keybind_button = ttk.Button(
    detector_app.button_frame,
    text="Configure Key Bindings",
    command=open_keybind_settings,
    style="Utility.TButton",
)
keybind_button.pack(side="left", padx=(8, 0))

root.mainloop()
