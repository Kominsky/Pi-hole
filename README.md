# HomeLab Network Observer & Pi-Hole Telemetry Pipeline

An automated, cross-platform network monitoring daemon and telemetry ingestion utility. Built to track active local hardware endpoints and pull real-time application-layer DNS metrics from a self-hosted **Pi-hole v6** instance using REST API authentication and 12-Factor configuration principles.

## Architecture & Data Flow

[Local Client Devices] ---> (DNS Queries) ---> [Pi-hole v6 (192.168.88.10)]
^
[Python Background Daemon] --- (ARP Polling) -----------> | (REST API / SID Auth)
|
+---> Appends Time-Series Logs (network_activity_log.json) via NDJSON

* **Layer 2/3 Discovery:** Dynamically executes OS-native neighbor table inspections (`arp -a` on Windows, `ip neigh` on Linux) to map active MAC-to-IP bindings.
* **Layer 7 Telemetry & Auth:** Authenticates programmatically against the Pi-hole v6 REST API (`POST /api/auth`) using secure JSON payloads, acquiring session identifiers (`sid`) to ingest daily block metrics.
* **Secret Management:** Decouples credentials from source code using environment variables and a local `.env` loader, adhering to 12-Factor app security guidelines.
* **Structured Logging:** Appends snapshots using Newline-Delimited JSON (NDJSON) for clean time-series storage and downstream observability ingestion.

An automated monitoring utility and architectural documentation for a self-hosted home network utilizing **Pi-hole** for sinkholing/DNS telemetry, custom ARP polling scripts, and local routing configurations.
* **Local Subnet Management:** Configured static DHCP reservations on the local router to ensure consistent IP allocation for critical infrastructure (NAS, Pi-hole, servers).
* **DNS Flow:** Client devices query the Pi-hole container/device as their primary upstream DNS resolver. Pi-hole filters ad-domains via gravity lists and forwards legitimate queries upstream (e.g., Cloudflare 1.1.1.1 over TLS).
* **Network Logging:** A lightweight Python background daemon periodically parses kernel neighbor tables (`ip neigh`) to snapshot active local hardware endpoints.\

## Engineering Challenges & Troubleshooting
1. **Cross-Platform OS Routing:**
   * *Challenge:* Linux kernel networking commands (`ip neigh`) threw `[WinError 2]` exceptions on Windows host environments.
   * *Resolution:* Integrated Python's built-in `platform` module to conditionally evaluate the host kernel and dispatch native command-line utilities.
2. **Pi-hole v6 API Breaking Changes & Security Challenge:**
   * *Challenge:* Legacy endpoints (`/admin/api.php`) were deprecated in favor of a native REST API that enforces strict session authentication, returning `401 Unauthorized` responses to unauthenticated polling.
   * *Resolution:* Engineered a pre-flight token exchange function that securely passes hashed credentials, captures the dynamic session identifier, and injects it into subsequent telemetry header requests.
3. **Environment Variable & Shell Escaping:**
   * *Challenge:* Terminal command-line parsing stripped trailing special characters (such as passwords ending in `$`) during interactive session setups.
   * *Resolution:* Implemented a robust, zero-dependency `.env` file loader that directly overrides `os.environ` while preserving literal string boundaries.

## Setup & Quickstart

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/your-username/homelab-network-observer.git](https://github.com/your-username/homelab-network-observer.git)
   cd homelab-network-observer
