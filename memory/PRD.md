# Red Team Automation Framework v5.0 - PRD

## Problem Statement
Framework Red Team local para Kali Linux con orquestacion adaptativa, C2 (MSF RPC + Sliver), generador de payloads con LHOST global, UI estilo APT/Cyberpunk con 9 secciones.

## What's Implemented

### C2 Resilience Layer (Apr 2026 - Incident Report Fixes)
- [x] MSF RPC: SSL/non-SSL auto-fallback, auth diagnostics, port reachability check
- [x] MSF RPC: Exponential backoff reconnect (5s-120s, 15 retries max, background thread)
- [x] MSF RPC: Connection validation on each call (detects dead connections)
- [x] MSF RPC: Detailed diagnostics endpoint GET /api/msf/diagnostics
- [x] Sliver: Config path validation (detects directory vs file, searches for .cfg inside)
- [x] Sliver: Connection validation with auto-reconnect (_ensure_connected)
- [x] Sliver: Async reconnect loop with exponential backoff
- [x] Unified RECONNECT button POST /api/c2/reconnect (both MSF + Sliver)
- [x] Frontend C2 panel: Shows diagnostics (token_set, port_reachable, config_path, auto-reconnecting status)

### Frontend Crash Fixes (Apr 2026)
- [x] attackTree.nodes: Object.values() for dict-type nodes (was .map crash)
- [x] All .map() calls protected with (|| []) for null/undefined data
- [x] mitreTactics: dict-to-array transform on API response
- [x] waf_analysis: safe null access pattern

### DevOps Fixes (Apr 2026)
- [x] start_redteam.sh: Correct log ownership (chown to SUDO_USER)
- [x] start_redteam.sh: Auto-detect current user, fix permissions
- [x] All paths via .env (no hardcoded paths in code)
- [x] Backend .env template with all required variables

### UI - APT Style (Apr 2026)
- [x] 9 sections: Dashboard, Targets, Attack Graph, Chains, C2, Payloads, AI, Config, Logs
- [x] Cyberpunk dark theme (JetBrains Mono, green/red/cyan accents)
- [x] Autonomous Mode toggle

### Payload Generator (Apr 2026)
- [x] 11 templates with LHOST auto-injection
- [x] Oneliners (bash, python, powershell), binaries (msfvenom), implants (Sliver)
- [x] GET /api/payloads/templates, POST /api/payloads/generate

### Global Config (Apr 2026)
- [x] GET/PUT /api/config persistent in MongoDB
- [x] Auto-inject LHOST into all: payloads, MSF, chains, Sliver

### Core Backend
- [x] Adaptive orchestration loop with safeguards
- [x] Attack chains (6 built-in), credential vault, session manager
- [x] PDF report generation, attack timeline
- [x] WebSocket real-time updates

## Architecture
```
backend/server.py - FastAPI (adaptive orchestration, 50+ endpoints)
backend/modules/__init__.py - MSF RPC with reconnect/diagnostics
backend/modules/sliver_c2.py - Sliver with path validation/reconnect
backend/modules/credential_vault.py
backend/modules/session_manager.py
frontend/src/App.js - React (9 sections)
frontend/src/App.css - Cyberpunk theme
start_redteam.sh - Start script with permission handling
install.sh - Full installer for Kali
```

## Key API Endpoints
- POST /api/scan/start, GET /api/scan/{id}/status
- GET/PUT /api/config
- GET /api/payloads/templates, POST /api/payloads/generate
- GET /api/c2/dashboard, POST /api/c2/reconnect
- GET /api/msf/status, GET /api/msf/diagnostics, POST /api/msf/connect
- GET /api/sliver/status, POST /api/sliver/reconnect
- POST /api/chains/execute, POST /api/chains/{id}/generate
- WS /api/ws/scan/{id}

## Backlog
### P1
- [ ] Refactorizar App.js en componentes separados (~1000 lineas)

### P2
- [ ] OpSec/Evasion (ofuscacion, limpieza, tunneling)
- [ ] BloodHound AD paths
- [ ] Multi-target campaigns
- [ ] Payload obfuscation (shikata_ga_nai, XOR, base64)
