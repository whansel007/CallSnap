# Reference: https://www.geeksforgeeks.org/python/python-get-list-of-running-processes/
import os, process_handling, win32gui, tkinter as tk
from pprint import pprint

_WHITELIST: list[str] = ["discord"]

# Functions
def splitCol(row: str) -> list[str]:
    info: list[str] = row.split()
    return [" ".join(info[:-1]), info[-1]] if len(info) != 0 else []

def getAllProcesses() -> dict[int, str]:
    """
    Get all running processes.
    
    :return: A map with key "process_id" and value "program_name"
    :rtype: dict[int, str]
    """
    output = os.popen("wmic process get description, processid").read()
    processes: dict[int, str] = {}
    for row in output.split("\n\n")[1:]:
        info: list[str] = splitCol(row)
        if len(info) != 0:
            desc, pid = info
            if len(process_handling.getHwnds(int(pid))) == 0: continue
            processes[int(pid)] = desc
    return processes

def isWhitelisted(name: str, whitelist: list[str]) -> bool:
    """
    Check if name is in the whitelist (case-insensitive, match)
    
    :param name: Program name
    :type name: str
    :param whitelist: A list of allowed program names
    :type whitelist: list[str]
    :return: The name of the program is in the whitelist.
    :rtype: bool
    """
    for wl_name in whitelist:
        if wl_name.lower() in name.lower():
            return True
    return False

# Class
class ProgramButton(tk.Button):

    def __init__(self, master: tk.Misc | None = None, pid: int = 0, name: str = "") -> None:
        hwnds = process_handling.getHwnds(pid)
        for hwnd in hwnds:
            name = name + " " + win32gui.GetWindowText(hwnd)
        
        super().__init__(master, text = name)

class WhitelistUI(tk.Tk):
    
    def __init__(self, title: str = "Whitelist", width: int = 600, height: int = 600) -> None:
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")

        processes = getAllProcesses()
        # display = "\n".join([f"{pid}\t: {name}" for pid, name in processes.items()])
        # tk.Label(self, text = display).pack()

        # Programs List
        programsFrame: tk.LabelFrame = tk.LabelFrame(self, text = "Programs")
        programsFrame.pack()


        # Whitelist
        whitelistFrame: tk.LabelFrame = tk.LabelFrame(self, text = "Whitelisted Programs")
        whitelistFrame.pack()

        # Program Buttons
        for pid, name in processes.items():
            programButton: ProgramButton
            if isWhitelisted(name, _WHITELIST):
                programButton = ProgramButton(whitelistFrame, pid, name)
            else:
                programButton = ProgramButton(programsFrame, pid, name)
                
            programButton.pack()

    

# Minimize Process with PID
if __name__ == "__main__":
    WhitelistUI("Whitelist").mainloop()
    # processes = getAllProcesses()
    # pprint(processes)
    # for pid, name in processes.items():
    #     if isWhitelisted(name, _WHITELIST):
    #         process_handling.restore_by_pid(pid)
    #     else:
    #         process_handling.minimize_by_pid(pid)
            # print(pid, "\t", name)
    # print(isWhitelisted("Discord.exe", _WHITELIST))