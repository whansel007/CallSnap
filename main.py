# Main program that cointains the settings
import ctypes
import tkinter as tk

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
root.title("Minimize All")

btn = tk.Button(root, text="Minimize All Apps", command=minimize_all)
btn.pack(padx=20, pady=20)

open_detector_btn = tk.Button(root, text="Open Name Detector", command=open_name_detector)
open_detector_btn.pack(padx=20, pady=10)

root.mainloop()
