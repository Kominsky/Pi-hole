#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime
import re
import platform
import urllib.request
import urllib.error
import urllib.parse
import os

#AUTO-LOAD .ENV FILE
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Ignore empty lines and comment lines
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                # Direct assignment forces the .env file to override anything else
                os.environ[key.strip()] = val.strip('\'"')

# CONFIGURATION
PIHOLE_IP = os.getenv("PIHOLE_IP", "192.168.88.10")
PIHOLE_PASSWORD = os.getenv("PIHOLE_PASSWORD")

def get_pihole_auth_sid(pihole_ip, password):
    """Authenticates against Pi-hole v6 REST API and prints any error details."""
    if not password:
        print("DEBUG: Password is empty.")
        return None
        
    url = f"http://{pihole_ip}/api/auth"
    payload = json.dumps({"password": password}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                session = data.get("session", {})
                if session.get("valid"):
                    return session.get("sid")
    except urllib.error.HTTPError as e:
        # Print the exact error JSON returned by Pi-hole v6!
        error_body = e.read().decode('utf-8', errors='ignore')
        print(f"DEBUG API Auth Error ({e.code}): {error_body}")
    except Exception as e:
        print(f"DEBUG Connection Error: {e}")
        
    return None

def get_pihole_stats(pihole_ip):
    if not PIHOLE_PASSWORD:
        return {"status": "auth_failed", "error": "PIHOLE_PASSWORD environment variable not set"}
        
    sid = get_pihole_auth_sid(pihole_ip, PIHOLE_PASSWORD)
    if not sid:
        return {"status": "auth_failed"}

    url = f"http://{pihole_ip}/api/stats/summary"
    req = urllib.request.Request(url, headers={'sid': sid}, method='GET')
    
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                queries = data.get("queries", {})
                clients = data.get("clients", {})
                return {
                    "status": "connected",
                    "dns_queries_today": queries.get("total", 0),
                    "ads_blocked_today": queries.get("blocked", 0),
                    "ads_percentage_today": queries.get("percent_blocked", 0.0),
                    "unique_clients": clients.get("active", 0)
                }
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}

def get_arp_table():
    """Parses the local ARP table to find connected devices cross-platform."""
    try:
        system = platform.system().lower()
        devices = []
        
        if "windows" in system:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2 and re.match(r'^\d{1,3}(\.\d{1,3}){3}$', parts[0]):
                    devices.append({
                        "ip": parts[0],
                        "mac": parts[1].replace('-', ':'),
                        "mac_type": parts[2] if len(parts) > 2 else "unknown"
                    })
        else:
            result = subprocess.run(['ip', 'neigh'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    mac_match = re.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', line)
                    if mac_match:
                        devices.append({
                            "ip": parts[0],
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
    pihole_telemetry = get_pihole_stats(PIHOLE_IP)
    
    log_entry = {
        "timestamp": timestamp,
        "active_device_count": len(devices),
        "pihole_telemetry": pihole_telemetry,
        "devices": devices
    }
    
    filename = "network_activity_log.json"
    try:
        with open(filename, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        print(f"[{timestamp}] Logged {len(devices)} local devices. Pi-hole status: {pihole_telemetry.get('status')}")
    except Exception as e:
        print(f"Failed to write log: {e}")

if __name__ == "__main__":
    log_network_snapshot()

