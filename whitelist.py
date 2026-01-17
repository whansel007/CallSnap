# Reference: https://www.geeksforgeeks.org/python/python-get-list-of-running-processes/
import os, process_handling, win32gui, tkinter as tk
from pprint import pprint

_whitelist: list[str] = []

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
    def __init__(self, master: tk.Misc | None = None, pid: int = 0, name: str = "", command = lambda: print("Pressed")) -> None:
        hwnds = process_handling.getHwnds(pid)
        self.name = name
        for hwnd in hwnds:
            self.desc = win32gui.GetWindowText(hwnd)
        self.command = command
        super().__init__(master, text = self.desc, command = self.command)
        self._isWhitelisted = isWhitelisted(name, _whitelist)
    
    def toggleWhitelist(self):
        # print(self.name)
        self._isWhitelisted = not self._isWhitelisted

    def refresh(self, newMaster: tk.Misc):
        super().__init__(newMaster, text = self.desc, command = self.command)

    
    def isWhitelisted(self) -> bool:
        return self._isWhitelisted


class WhitelistUI(tk.Toplevel):
    _PADDING: int = 10
    _PACK_ARGS = {"padx": _PADDING, "pady": _PADDING, "fill": "x"}

    def __init__(self, master = None, title: str = "Whitelist", width: int = 600, height: int = 600) -> None:
        # Instance Variables
        self._programButtons: dict[int, ProgramButton] = {}
        self.processes = getAllProcesses()

        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")

        # display = "\n".join([f"{pid}\t: {name}" for pid, name in processes.items()])
        # tk.Label(self, text = display).pack()

        # Programs List
        self.programsFrame: tk.LabelFrame = tk.LabelFrame(self, text = "Programs")
        self.programsFrame.pack(**self._PACK_ARGS) # padx = self._PADDING, pady = self._PADDING, fill = "x"

        # Whitelist
        self.whitelistFrame: tk.LabelFrame = tk.LabelFrame(self, text = "Whitelisted Programs")
        self.whitelistFrame.pack(**self._PACK_ARGS)

        # Program Buttons
        self.insertButtons()

        # Closing protocol
        self.protocol("WM_DELETE_WINDOW", self.window_exit)

    def window_exit(self):
        _whitelist[:] = self.getProgramWhitelist()
        self.destroy()
        

    def insertButtons(self) -> None:
        # new_dict: dict[int, ProgramButton] = {}
        for pid, name in self.processes.items():
            programButton: None|ProgramButton = None
            if isWhitelisted(name, _whitelist) or programButton and programButton.isWhitelisted():
                programButton = ProgramButton(self.whitelistFrame, pid, name, lambda x = pid: self.refresh(x))
            else:
                programButton = ProgramButton(self.programsFrame, pid, name, lambda x = pid: self.refresh(x))
                
            programButton.pack()
            self._programButtons[pid] = programButton
        
        # Show LabelFrame
        self.blankProgramLabel = tk.Label(self.programsFrame, text = "No active program yet.")
        self.blankProgramLabel.pack()
        self.blankWhitelistLabel = tk.Label(self.whitelistFrame, text = "No ")
        self.blankWhitelistLabel.pack()
        # self._programButtons = new_list

    def refresh(self, pid: int) -> None:
        selfButton: ProgramButton = self._programButtons[pid]
        selfButton.toggleWhitelist()
        selfButton.pack_forget()
        if selfButton.isWhitelisted():
            selfButton.refresh(self.whitelistFrame)
        else:
            selfButton.refresh(self.programsFrame)

        # self.insertButtons()
        selfButton.pack()
        self._printProgramWhitelist()
    
    def getProgramWhitelist(self):
        return [button.name for button in self._programButtons.values() if button.isWhitelisted()]
    
    def _printProgramWhitelist(self):
        """
        Debug purposes only. Show the whitelist status of all program.
        """
        print("__Button_Whitelist_______")
        for button in self._programButtons.values():
            print(button.desc[:12], button.isWhitelisted())
        print()

# Minimize Process with PID
def openWhitelistUI(master: tk.Tk) -> None:
    wui = WhitelistUI(master)
    wui.grab_set()
    wui.mainloop()
    # wui.grab_release()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x300")
    tk.Button(root, text = "Whitelist UI", command = lambda: openWhitelistUI(root)).pack()
    tk.Button(root, text = "Print Whitelist", command = lambda: print(_whitelist)).pack()
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