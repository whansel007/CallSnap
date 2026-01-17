# Main program that cointains the settings
import ctypes
import tkinter as tk
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

def open_name_detector():
    detector_window = tk.Toplevel(root)
    NameDetectorGUI(detector_window)

# UI ===
root = tk.Tk()
root.title("CallSnap")
root.geometry("520x440")
root.minsize(520, 440)
root.configure(bg="#f3f1ed")

header_frame = tk.Frame(root, bg="#f3f1ed")
header_frame.pack(fill="x", padx=24, pady=(24, 12))

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

content_frame = tk.Frame(root, bg="#f3f1ed")
content_frame.pack(fill="both", expand=True, padx=24, pady=(8, 20))

minimize_btn = tk.Button(
    content_frame,
    text="Minimize All Apps",
    command=minimize_all,
    font=("Segoe UI", 11, "bold"),
    bg="#f7d070",
    fg="#2d2a26",
    activebackground="#e7c15f",
    relief="flat",
)
minimize_btn.pack(fill="x", pady=(0, 10))

open_detector_btn = tk.Button(
    content_frame,
    text="Open Name Detector",
    command=open_name_detector,
    font=("Segoe UI", 11, "bold"),
    bg="#9cc5a1",
    fg="#1f2a22",
    activebackground="#86b28c",
    relief="flat",
)
open_detector_btn.pack(fill="x", pady=(0, 18))

utility_label = tk.Label(
    content_frame,
    text="Utilities",
    font=("Georgia", 12, "bold"),
    bg="#f3f1ed",
    fg="#2d2a26",
)
utility_label.pack(anchor="w", pady=(0, 6))

whitelist_btn = tk.Button(
    content_frame,
    text="Whitelist UI",
    command=lambda: wl.openWhitelistUI(root),
    font=("Segoe UI", 10),
    bg="#e6e2dc",
    fg="#2d2a26",
    activebackground="#d7d1ca",
    relief="flat",
)
whitelist_btn.pack(fill="x", pady=(0, 6))

print_whitelist_btn = tk.Button(
    content_frame,
    text="Print Whitelist",
    command=lambda: print(wl._whitelist),
    font=("Segoe UI", 10),
    bg="#e6e2dc",
    fg="#2d2a26",
    activebackground="#d7d1ca",
    relief="flat",
)
print_whitelist_btn.pack(fill="x", pady=(0, 6))

minimize_whitelist_btn = tk.Button(
    content_frame,
    text="Minimize Whitelist Programs",
    command=wl.minmaxPrograms,
    font=("Segoe UI", 10),
    bg="#e6e2dc",
    fg="#2d2a26",
    activebackground="#d7d1ca",
    relief="flat",
)
minimize_whitelist_btn.pack(fill="x")

root.mainloop()
