#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime
import re

def get_arp_table():
    """Parse the local ARP table to find connected devices"""
    try:
        result = subprocess.run(['arp -a'], capture_output=True, text=True, check=True)
        devices = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 5:
                ip = parts[0]
                #look for MAC address feild
                mac_match = re.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', line)
                if mac_match:
                    devices.append({
                        "ip": ip,
                        "mac": mac_match.group(0),
                        "status": parts[-1] if "REACHABLE" in line or "STALE" in line else "UNKNOWN"
                    })
    except Exception as e:
        print(f"Error fetching ARP table: {e}")
        return []


def log_network_snapshot():
    timestamp = datetime.now().isoformat()
    devices = get_arp_table()

    log_entry = {
        "timestamp": timestamp,
        "active_device_count": len(devices),
        "devices": devices
    }

    #append to a local JSON log file
    filename = "network_activity_log.json"
    try:
        with open(filename, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"[{timestamp}] Logged {len(devices)} active devices.")

    except Exception as e:
        print(f"Failed to write log")


if __name__ == "__main__":
    log_network_snapshot()