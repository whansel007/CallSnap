# Reference: https://www.geeksforgeeks.org/python/python-get-list-of-running-processes/
import os
from pprint import pprint
import process_handling

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
            processes[int(pid)] = desc
    return processes

# Minimize Process with PID
if __name__ == "__main__":
    processes = getAllProcesses()
    for pid, name in processes.items():
        if "discord" in name.lower():
            print(pid, name)