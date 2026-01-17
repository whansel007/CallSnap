# Reference: https://www.geeksforgeeks.org/python/python-get-list-of-running-processes/
import os, process_handling, win32gui, tkinter as tk
from pprint import pprint

_WHITELIST: list[str] = ["discord", "spotify"]

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
    _isWhitelisted: bool = False

    def __init__(self, master: tk.Misc | None = None, pid: int = 0, name: str = "") -> None:
        hwnds = process_handling.getHwnds(pid)
        self.name = name
        for hwnd in hwnds:
            self.name = self.name + " " + win32gui.GetWindowText(hwnd)
        
        super().__init__(master, text = self.name, command = self.toggleWhitelist)
    
    def toggleWhitelist(self):
        print(self.name)
        self._isWhitelisted = not self._isWhitelisted

class WhitelistUI(tk.Toplevel):
    _PADDING: int = 10

    def __init__(self, master = None, title: str = "Whitelist", width: int = 600, height: int = 600) -> None:
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")

        processes = getAllProcesses()
        # display = "\n".join([f"{pid}\t: {name}" for pid, name in processes.items()])
        # tk.Label(self, text = display).pack()

        # Programs List
        self.programsFrame: tk.LabelFrame = tk.LabelFrame(self, text = "Programs")
        self.programsFrame.pack(padx = self._PADDING, pady = self._PADDING, fill = "x")


        # Whitelist
        self.whitelistFrame: tk.LabelFrame = tk.LabelFrame(self, text = "Whitelisted Programs")
        self.whitelistFrame.pack(padx = self._PADDING, pady = self._PADDING, fill = "x")

        # Program Buttons
        for pid, name in processes.items():
            programButton: ProgramButton
            if isWhitelisted(name, _WHITELIST):
                programButton = ProgramButton(self.whitelistFrame, pid, name)
            else:
                programButton = ProgramButton(self.programsFrame, pid, name)
                
            programButton.pack()

    

# Minimize Process with PID
def openWhitelistUI(master: tk.Tk):
    wui = WhitelistUI(master)
    wui.grab_set()
    wui.mainloop()
    wui.grab_release()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x300")
    tk.Button(root, text = "Whitelist UI", command = lambda: openWhitelistUI(root)).pack()
    root.mainloop()
    # processes = getAllProcesses()
    # pprint(processes)
    # for pid, name in processes.items():
    #     if isWhitelisted(name, _WHITELIST):
    #         process_handling.restore_by_pid(pid)
    #     else:
    #         process_handling.minimize_by_pid(pid)
            # print(pid, "\t", name)
    # print(isWhitelisted("Discord.exe", _WHITELIST))