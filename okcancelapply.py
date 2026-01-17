import tkinter as tk
from typing import Callable, Any

class okcancelapply(tk.Frame):
    _PACK_KWARGS: dict[str, Any] = {"padx":2, "pady":10, "side":"left"}
    _STYLE: dict[str, Any] = {
        "width": 12
    }

    def __init__(self, master: tk.Tk| tk.Toplevel, applyCommand: None|Callable[[], None] = None, exitCommand: None|Callable[[], None] = None, stateFunc: None|Callable[[], bool] = None) -> None:
        """
        Construct the "Ok Cancel Apply" Buttons frame.
        
        :param master: The parent of the frame. By default: does nothing.
        :type master: tk.Misc | None
        :param applyCommand: The function that is triggered when pressing "Ok" or "Apply". By default: does nothing.
        :type applyCommand: None | Callable[[], None]
        :param exitCommand: The function that is triggered when pressing "Ok" or "Cancel". By default: close master.
        :type exitCommand: None | Callable[[], None]
        :param stateFunc: The function that looks for any changes between local settings and global settings. When false, disable the apply button.
        :type stateFunc: None | Callable[[], bool]
        """
        super().__init__(master)
        self.applyCommand = applyCommand if applyCommand else lambda: None
        self.exitCommand = exitCommand if exitCommand else lambda: master.destroy()
        self.stateFunc = stateFunc if stateFunc else lambda: True

        self.okButton = tk.Button(self, text = "Ok", command = self._handleOk, **self._STYLE)
        self.cancelButton = tk.Button(self, text = "Cancel", command = self._handleCancel, **self._STYLE)
        self.applyButton = tk.Button(self, text = "Apply", command = self._handleApply, **self._STYLE)

        self.okButton.pack(**self._PACK_KWARGS)
        self.cancelButton.pack(**self._PACK_KWARGS)
        self.applyButton.pack(**self._PACK_KWARGS)

        self.applyButton.configure(state = tk.DISABLED)
    
    def _handleOk(self):
        self.applyCommand()
        self.exitCommand()

    def _handleCancel(self):
        self.exitCommand()
    
    def _handleApply(self):
        self.applyCommand()
        self.refreshApplyButton()

    def refreshApplyButton(self):
        if self.stateFunc():
            self.applyButton.configure(state = tk.NORMAL)
        else:
            self.applyButton.configure(state = tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x150")

    globalValue = tk.IntVar(root, 0)
    localValue = tk.IntVar(root, 0)

    applyCommand = lambda: globalValue.set(localValue.get())
    exitCommand = lambda: root.destroy()
    def changed(): return globalValue.get() != localValue.get()

    oca = okcancelapply(root, applyCommand, exitCommand, changed)

    def buttonClick():
        localValue.set(localValue.get() + 1)
        oca.refreshApplyButton()

    tk.Label(root, text = "Local:").pack()
    tk.Label(root, textvariable = localValue).pack()
    tk.Label(root, text = "Global:").pack()
    tk.Label(root, textvariable = globalValue).pack()
    tk.Button(root, text = "+1", command = buttonClick).pack()

    oca.pack()
    root.mainloop()
    print("Final global value:", globalValue.get())