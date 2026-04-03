# Red Team Automation Framework v3.2 - PRD

## Problem Statement
Framework Red Team profesional con MITRE ATT&CK, Tactical Decision Engine adaptativo, Moonshot AI (Kimi K2) para analisis inteligente, y Attack Chains automatizadas con motor de ejecucion paso a paso.

## What's Implemented

### Core Features (Complete)
- [x] 14 tacticas MITRE ATT&CK seleccionables (Kill Chain)
- [x] 34 herramientas Red Team categorizadas
- [x] 35+ modulos Metasploit con MITRE mapping
- [x] Tema Matrix/Cyberpunk (#FF003C, #00FF41, negro)
- [x] Moonshot AI (Kimi K2) Red Team Advisor
- [x] Scan system con background tasks y polling

### Tactical Decision Engine (Complete)
- [x] WAF bypass strategies (Cloudflare, Akamai, AWS WAF, Imperva, ModSecurity)
- [x] Service-to-attack mapping (10+ servicios)
- [x] Vulnerability-to-exploit mapping (SQL, XSS, LFI, RFI, SSRF, etc)
- [x] Adaptive planning en tiempo real

### Attack Chains (Complete - P0 + P1)
- [x] 6 cadenas predefinidas: Web to Shell, SMB to Domain, Kerberos, Linux PrivEsc, Windows PrivEsc, Phishing to Shell
- [x] Motor de ejecucion automatica (auto_execute) con tracking paso a paso
- [x] Ejecucion manual paso a paso con botones [RUN] individuales
- [x] Pipeline visual de progreso (S1 > S2 > S3 > S4) con colores de estado
- [x] Polling en tiempo real (1.5s) durante ejecucion
- [x] Context variables (LHOST, Domain, User, Pass) para personalizar comandos
- [x] Deteccion automatica de chains aplicables segun hallazgos
- [x] Resultados por paso en el terminal

### Attack Tree (Complete)
- [x] Arbol de ataque interactivo con nodos priorizados
- [x] Nodos de WAF, prioridad, herramienta, exploit
- [x] Status tracking por nodo (pending/testing/success/failed)

## Architecture
- Frontend: React + TailwindCSS + Shadcn UI (Matrix theme)
- Backend: FastAPI + Motor (MongoDB async)
- Database: MongoDB
- AI: Moonshot AI (Kimi K2) via API
- Execution: Background tasks con asyncio

## API Endpoints
- GET /api/ - Health check
- GET /api/mitre/tactics - Tacticas MITRE
- GET /api/tools - Herramientas Red Team
- POST /api/scan/start - Iniciar escaneo
- GET /api/scan/{id}/status - Status del escaneo
- GET /api/scan/{id}/tree - Attack tree
- PUT /api/scan/{id}/tree/node/{id} - Actualizar nodo
- GET /api/scan/history - Historial
- GET /api/chains - Listar cadenas
- GET /api/chains/{id} - Detalles de cadena
- POST /api/chains/execute - Ejecutar cadena (manual/auto)
- GET /api/chains/execution/{id} - Status de ejecucion
- POST /api/chains/execution/{id}/step/{id} - Ejecutar paso manual
- POST /api/chains/detect - Detectar chains aplicables
- POST /api/chains/{id}/generate - Generar comandos
- GET /api/metasploit/modules - Modulos MSF
- POST /api/metasploit/execute - Ejecutar MSF
- GET /api/tactical/waf-bypass/{waf} - Bypass strategies
- GET /api/tactical/service-attacks - Service attack map
- GET /api/tactical/vuln-exploits - Vuln exploit map

## Prioritized Backlog

### P0 - Completado
- Attack Chains display y ejecucion
- Tactical Decision Engine
- MITRE ATT&CK Kill Chain

### P1 - Completado
- Attack Chain Execution Engine con tracking en tiempo real

### P2 (Proximo)
- C2 Framework integration (Sliver/Havoc)
- BloodHound AD attack paths
- WebSocket real-time updates (reemplazar polling)
- Report generation PDF
- Real Metasploit integration (msfrpcd)

### P3 (Futuro)
- Cobalt Strike Beacon simulation
- Multi-target campaign management
- Deploy en Kali Linux real
