# Reference: https://www.geeksforgeeks.org/python/python-get-list-of-running-processes/
import os
from pprint import pprint
import win32con # Dependency



output = os.popen("wmic process get description, processid").read()
BLACKLIST: list[str] = ['svchost.exe']


def splitCol(row: str) -> list[str]:
    info: list[str] = row.split()
    return [" ".join(info[:-1]), info[-1]] if len(info) != 0 else []

processes: dict[int, str] = {}
for row in output.split("\n\n")[1:]:
    info: list[str] = splitCol(row)
    if len(info) != 0:
        desc, pid = info
        if desc in BLACKLIST: continue
        processes[int(pid)] = desc
    
pprint(processes)

# Minimize Process with PID
