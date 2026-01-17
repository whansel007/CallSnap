# Reference: https://www.geeksforgeeks.org/python/python-get-list-of-running-processes/
import os, process_handling, win32gui, tkinter as tk
from pprint import pprint
from okcancelapply import OkCancelApply as OCA

"""
Public method: 
- openWhitelistUI(master: tk.Tk) -> None
- getWhitelist() -> list[str]
- minmaxPrograms() -> None
"""

_whitelist: list[str] = []
_blacklist: list[str] = ["TextInputHost.exe"]

# Private Functions
def _splitCol(row: str) -> list[str]:
    info: list[str] = row.split()
    return [" ".join(info[:-1]), info[-1]] if len(info) != 0 else []

def _getAllProcesses() -> dict[int, str]:
    """
    Get all running processes.
    
    :return: A map with key "process_id" and value "program_name"
    :rtype: dict[int, str]
    """
    output = os.popen("wmic process get description, processid").read()
    processes: dict[int, str] = {}
    for row in output.split("\n\n")[1:]:
        info: list[str] = _splitCol(row)
        if len(info) != 0:
            desc, pid = info
            if len(process_handling.getHwnds(int(pid))) == 0: continue
            if desc in _blacklist: continue
            processes[int(pid)] = desc
    return processes

def _isWhitelisted(name: str, whitelist: list[str]) -> bool:
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
class _ProgramButton(tk.Button):
    _MAX_CHAR: int = 32

    def __init__(self, master: tk.Misc | None = None, pid: int = 0, name: str = "", command = lambda: print("Pressed")) -> None:
        # Instance Variable
        self.name = name
        self.desc = ""
        self.command = command

        # Get Window Name
        hwnds = process_handling.getHwnds(pid)
        for hwnd in hwnds:
            tempDesc = win32gui.GetWindowText(hwnd)
            # print(f"'{tempDesc}'")
            if tempDesc != "" and self.desc == "":
                # print(f"    '{tempDesc}'")
                self.desc = tempDesc

        # Add Program Name if it's not present
        program_name = self.name.split(".")[0].lower()
        if program_name not in self.desc.lower()[:self._MAX_CHAR - 3]:
            if len(self.desc) > self._MAX_CHAR - len(program_name) - 3:
                self.desc = self.desc[:self._MAX_CHAR - 3] + "..."
            self.desc += f" ({program_name.capitalize()})"
        elif len(self.desc) > self._MAX_CHAR:
            self.desc = self.desc[:self._MAX_CHAR - 3] + "..."

        # Create Program Button
        super().__init__(master, text = self.desc, command = self.command, width = self._MAX_CHAR + 4)
        self._isWhitelisted = _isWhitelisted(name, _whitelist)
    
    def toggleWhitelist(self):
        self._isWhitelisted = not self._isWhitelisted

    def refresh(self, newMaster: tk.Misc):
        super().__init__(newMaster, text = self.desc, command = self.command, width = self._MAX_CHAR + 4)
    
    def isWhitelisted(self) -> bool:
        return self._isWhitelisted

class _WhitelistUI(tk.Toplevel):
    _PADDING: int = 10
    _PACK_KWARGS = {"padx": _PADDING, "pady": _PADDING, "fill": "x"}

    def __init__(self, master = None, title: str = "Whitelist", width: int = 500, height: int = 600) -> None:
        # Instance Variables
        self._programButtons: dict[int, _ProgramButton] = {}
        self.processes = _getAllProcesses()
        self.localWhitelist = _whitelist[:]

        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Programs List
        self.programsFrame: tk.LabelFrame = tk.LabelFrame(self, text = "Programs")
        self.programsFrame.pack(**self._PACK_KWARGS) # padx = self._PADDING, pady = self._PADDING, fill = "x"

        # Whitelist
        self.whitelistFrame: tk.LabelFrame = tk.LabelFrame(self, text = "Whitelisted Programs")
        self.whitelistFrame.pack(**self._PACK_KWARGS)

        # Program Buttons
        self.insertButtons()

        # Ok Cancel Apply Button
        self.oca: OCA = OCA(self, self._apply, None, self._stateFunc)
        self.oca.pack(side="bottom", **self._PACK_KWARGS)

        # Closing protocol
        self.protocol("WM_DELETE_WINDOW", self.window_exit)

    def _apply(self):
        _whitelist[:] = self.localWhitelist

    
    def _stateFunc(self):
        if len(_whitelist) != len(self.localWhitelist):
            return True

        for prog in self.localWhitelist:
            if prog not in _whitelist:
                return True
        return False

    def window_exit(self):
        _whitelist[:] = self.getProgramWhitelist()
        self.destroy()

    def insertButtons(self) -> None:
        # new_dict: dict[int, ProgramButton] = {}
        for pid, name in self.processes.items():
            programButton: None|_ProgramButton = None
            if len(name) == 0:
                continue
            elif _isWhitelisted(name, _whitelist) or programButton and programButton.isWhitelisted():
                programButton = _ProgramButton(self.whitelistFrame, pid, name, lambda x = pid: self.refresh(x))
            else:
                programButton = _ProgramButton(self.programsFrame, pid, name, lambda x = pid: self.refresh(x))
                
            programButton.pack()
            self._programButtons[pid] = programButton
        
        # Show LabelFrame
        self.blankWhitelistLabel = tk.Label(self.whitelistFrame, text = "No whitelisted program yet.")
        self.blankProgramLabel = tk.Label(self.programsFrame, text = "All programs are whitelisted!")

        whitelist_length = len(self.getProgramWhitelist())
        if whitelist_length == 0:
            self.blankWhitelistLabel.pack()
        
        if len(self.processes) - whitelist_length == 0:
            self.blankProgramLabel.pack()
        
        # Frame Padding
        self.programPad = tk.Frame(self.programsFrame, height = self._PADDING)
        self.whitelistPad = tk.Frame(self.whitelistFrame, height = self._PADDING)

        self.programPad.pack()
        self.whitelistPad.pack()

    def refresh(self, pid: int) -> None:
        # Change the referred program button's whitelist status
        selfButton: _ProgramButton = self._programButtons[pid]
        selfButton.toggleWhitelist()

        # Update the position of the button
        selfButton.pack_forget()
        if selfButton.isWhitelisted():
            selfButton.refresh(self.whitelistFrame)
        else:
            selfButton.refresh(self.programsFrame)
        selfButton.pack()

        # Update local settings
        self.localWhitelist[:] = self.getProgramWhitelist()

        # Show empty frame status
        whitelist_length = len(self.localWhitelist)
        self.blankWhitelistLabel.pack_forget()
        self.blankProgramLabel.pack_forget()

        if whitelist_length == 0: # No whitelist
            self.blankWhitelistLabel.pack()

        if len(self.processes) - whitelist_length == 0: # No blacklist
            self.blankProgramLabel.pack()

        # update frame padding
        self.programPad.pack_forget()
        self.programPad.pack()
        self.whitelistPad.pack_forget()
        self.whitelistPad.pack()
        
        # Refresh Apply Button
        self.oca.refreshApplyButton()
    
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

# Public Functions
def openWhitelistUI(master: tk.Tk) -> None:
    wui = _WhitelistUI(master)
    wui.grab_set()
    wui.mainloop()
    # wui.grab_release()

def getWhitelist() -> list[str]:
    return _whitelist

def minmaxPrograms() -> None:
    processes = _getAllProcesses()
    for pid, name in processes.items():
        if _isWhitelisted(name, _whitelist):
            process_handling.restore_by_pid(pid)
        else:
            process_handling.minimize_by_pid(pid)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x150")
    tk.Button(root, text = "Whitelist UI", command = lambda: openWhitelistUI(root)).pack()
    tk.Button(root, text = "Print Whitelist", command = lambda: print(_whitelist)).pack()
    tk.Button(root, text = "Minimize!", command = minmaxPrograms).pack()

    root.mainloop()