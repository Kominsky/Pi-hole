#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime
import re
import platform

def get_arp_table():
    """Parses the local ARP table to find connected devices cross-platform."""
    try:
        system = platform.system().lower()
        devices = []
        
        if "windows" in system:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                parts = line.strip().split()
                # Match IP address format
                if len(parts) >= 2 and re.match(r'^\d{1,3}(\.\d{1,3}){3}$', parts[0]):
                    ip = parts[0]
                    mac = parts[1].replace('-', ':')
                    if re.match(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', mac):
                        devices.append({
                            "ip": ip,
                            "mac": mac,
                            "mac_type": parts[2] if len(parts) > 2 else "unknown"
                        })
        else:
            result = subprocess.run(['ip', 'neigh'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    ip = parts[0]
                    mac_match = re.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', line)
                    if mac_match:
                        devices.append({
                            "ip": ip,
                            "mac": mac_match.group(0),
                            "mac_type": parts[-1] if "REACHABLE" in line or "STALE" in line else "unknown"
                        })
        return devices
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
    
    filename = "network_activity_log.json"
    try:
        with open(filename, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"[{timestamp}] Logged {len(devices)} active devices.")
    except Exception as e:
        print(f"Failed to write log: {e}")

if __name__ == "__main__":
    log_network_snapshot()