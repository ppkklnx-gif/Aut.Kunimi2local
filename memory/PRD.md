# Red Team Automation Framework v5.0 - PRD

## Problem Statement
Framework Red Team con orquestacion adaptativa, boveda de credenciales, cadenas condicionales, msfrpcd, Sliver C2, WebSocket, timeline de ataque, y catalogo dinamico de herramientas.

## What's Implemented (Feb 2026)

### Core (8 nuevos puntos del usuario)
- [x] 1. Orquestacion Dinamica Adaptativa - loop que decide la siguiente herramienta segun resultados
- [x] 2. Cadenas integradas al Motor Tactico - auto-trigger de chains cuando hallazgos lo justifican
- [x] 3. Boveda de Credenciales - parseo automatico, almacenamiento, inyeccion en comandos
- [x] 4. Ejecucion Condicional en Cadenas - evalua condiciones (sqli, shell, linux, windows, creds)
- [x] 5. Session Manager - tracking de shells activas, acciones post-explotacion recomendadas
- [x] 6. Catalogo Dinamico de Herramientas - POST /api/tools/add, DELETE /api/tools/{id}
- [x] 7. Reportes con Timeline - cronologia completa del ataque con timestamps
- [x] 8. Abort Scan - boton ABORT que mata escaneo en curso

### Safeguards
- [x] Max 20 herramientas por escaneo
- [x] Timeout 600s global
- [x] Timeout 120s por herramienta
- [x] Max 3 errores consecutivos
- [x] Auto-skip de herramientas agresivas si WAF detectado
- [x] Pausa entre herramientas

### Previas
- [x] msfrpcd real, Sliver C2, WebSocket, PDF reports, modulos recomendados
- [x] MITRE ATT&CK, 6 cadenas de ataque, tema Matrix

## Backlog P2
- [ ] OpSec/Evasion (ofuscacion, limpieza, tunneling) - punto 7 del usuario
- [ ] BloodHound AD paths
- [ ] Multi-target campaigns
