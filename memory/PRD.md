# Red Team Automation Framework v5.0 - PRD

## Problem Statement
Framework Red Team con orquestacion adaptativa, boveda de credenciales, cadenas condicionales, msfrpcd, Sliver C2, WebSocket, timeline de ataque, y catalogo dinamico de herramientas. UI estilo APT/Cyberpunk con 8 secciones y configuracion global de listener.

## What's Implemented (Feb-Apr 2026)

### UI Overhaul - APT Style (Apr 2026)
- [x] Dashboard: 4 metricas, MITRE Kill Chain fases, Recent Operations
- [x] Targets: Add/Remove/Scan targets
- [x] Attack Graph: Visual tree of scan results
- [x] Chains: 6 cadenas de ataque con context inputs y ejecucion manual/auto
- [x] C2: MSF + Sliver status panels, session shell interactivo
- [x] AI: Kimi K2 analysis, recommended exploits, suggested chains, PDF download
- [x] Config: Global listener IP/Port, C2 protocol, auto-inject LHOST, stealth mode, quick payload commands
- [x] Logs: Terminal output con 6 filtros
- [x] Autonomous Mode toggle
- [x] Cyberpunk dark theme (JetBrains Mono, green/red/cyan accents)

### Global Listener Config (Apr 2026)
- [x] Backend: GET/PUT /api/config - persistent in MongoDB
- [x] Auto-inject LHOST into all payloads: MSF, chains, Sliver implants
- [x] Quick Payload Commands: MSFvenom, Bash, Python reverse shells, NC listener, MSF handler
- [x] Sidebar LHOST indicator (green when configured, red when not)

### Core Backend (Feb 2026)
- [x] 1. Orquestacion Dinamica Adaptativa - loop que decide herramienta segun resultados
- [x] 2. Cadenas integradas al Motor Tactico - auto-trigger chains cuando hallazgos justifican
- [x] 3. Boveda de Credenciales - parseo automatico, almacenamiento, inyeccion
- [x] 4. Ejecucion Condicional en Cadenas - evalua condiciones (sqli, shell, linux, windows, creds)
- [x] 5. Session Manager - tracking de shells activas, post-explotacion recomendada
- [x] 6. Catalogo Dinamico de Herramientas - POST /api/tools/add, DELETE /api/tools/{id}
- [x] 7. Reportes con Timeline - cronologia completa con timestamps
- [x] 8. Abort Scan - boton ABORT que mata escaneo

### Safeguards
- [x] Max 20 herramientas por escaneo
- [x] Timeout 600s global / 120s por herramienta
- [x] Max 3 errores consecutivos
- [x] Auto-skip de herramientas agresivas si WAF detectado
- [x] Pausa entre herramientas

### Integrations
- [x] Moonshot AI (Kimi K2) - analisis tactico
- [x] msfrpcd - Metasploit RPC
- [x] Sliver C2 - gRPC
- [x] WebSocket - real-time scan updates

## Architecture
```
/app/backend/server.py - FastAPI (adaptive orchestration, 50+ endpoints)
/app/backend/modules/credential_vault.py
/app/backend/modules/session_manager.py
/app/backend/modules/sliver_c2.py
/app/frontend/src/App.js - React (8 sections)
/app/frontend/src/App.css - Cyberpunk theme
```

## Backlog

### P1
- [ ] Refactorizar App.js en componentes separados (archivo de ~850 lineas)

### P2
- [ ] OpSec/Evasion (ofuscacion, limpieza, tunneling)
- [ ] BloodHound AD paths
- [ ] Multi-target campaigns
- [ ] Expandir credential_vault para inyeccion automatica en MSF/Sliver modules
