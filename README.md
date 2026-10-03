# HomeLab Network Observer & DNS Router

## Architecture & Network Routing
An automated monitoring utility and architectural documentation for a self-hosted home network utilizing **Pi-hole** for sinkholing/DNS telemetry, custom ARP polling scripts, and local routing configurations.
* **Local Subnet Management:** Configured static DHCP reservations on the local router to ensure consistent IP allocation for critical infrastructure (NAS, Pi-hole, servers).
* **DNS Flow:** Client devices query the Pi-hole container/device as their primary upstream DNS resolver. Pi-hole filters ad-domains via gravity lists and forwards legitimate queries upstream (e.g., Cloudflare 1.1.1.1 over TLS).
* **Network Logging:** A lightweight Python background daemon periodically parses kernel neighbor tables (`ip neigh`) to snapshot active local hardware endpoints.
