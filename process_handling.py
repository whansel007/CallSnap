import win32gui
import win32con
import win32process

def getHwnds(pid: int) -> list[int]:
    def callback(hwnd, hwnds):
        # Get PID for this window handle
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid and win32gui.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def minimize_by_pid(pid):
    for hwnd in getHwnds(pid):
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def maximize_by_pid(pid):
    for hwnd in getHwnds(pid):
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def restore_by_pid(pid):
    for hwnd in getHwnds(pid):
        # Reference: https://stackoverflow.com/questions/60471477/using-python-how-can-i-detect-whether-a-program-is-minimized-or-maximized
        _, viewStatus, *_ = win32gui.GetWindowPlacement(hwnd)
        if viewStatus == win32con.SW_SHOWMAXIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        

if __name__ == "__main__":
    target_pids = [25064, 9032, 9260, 20100, 18736, 16132]  # Replace with your PID
    for target_pid in target_pids:
        restore_by_pid(target_pid)