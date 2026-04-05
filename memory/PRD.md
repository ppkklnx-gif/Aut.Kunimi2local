# Red Team Framework v5.0 - PRD

## What's Implemented
- Docker deployment (mongo, backend, frontend)
- 9-section APT-style Cyberpunk UI
- Payload generator (11 templates) with global LHOST injection
- C2 resilience (MSF RPC + Sliver) with diagnostics and auto-reconnect
- Adaptive scan orchestration, attack chains, credential vault
- Health check endpoint with full connectivity diagnostics

## Architecture
Docker Compose: mongo:7, backend (Python+nmap+nikto), frontend (React+Nginx)
Kali host: msfrpcd, sliver-server

## Backlog
### P1
- Refactorizar App.js en componentes modulares

### P2
- OpSec/Evasion, BloodHound AD, multi-target campaigns, payload obfuscation
