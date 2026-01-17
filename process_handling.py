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

def restore_by_pid(pid):
    for hwnd in getHwnds(pid):
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

if __name__ == "__main__":
    target_pids = [25064, 9032, 9260, 20100, 18736, 16132]  # Replace with your PID
    for target_pid in target_pids:
        restore_by_pid(target_pid)