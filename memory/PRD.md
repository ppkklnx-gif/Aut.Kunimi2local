# Red Team Automation Framework v3.0 - PRD

## Original Problem Statement
Herramienta web profesional para Red Team con MITRE ATT&CK completo, pensando como un operador ofensivo. Incluye todas las fases del Kill Chain, herramientas de pentesting avanzadas, y análisis de IA para identificar vectores de ataque.

## Architecture
- **Frontend**: React + TailwindCSS (Matrix/Cyberpunk theme con rojo)
- **Backend**: FastAPI + MongoDB
- **AI**: Kimi K2 como Red Team Advisor
- **Framework**: MITRE ATT&CK v18 (Oct 2025)

## MITRE ATT&CK Integration

### 14 Tácticas Implementadas
1. TA0043 - Reconnaissance (RECON)
2. TA0042 - Resource Development (RESOURCE)
3. TA0001 - Initial Access (INITIAL ACCESS)
4. TA0002 - Execution (EXECUTION)
5. TA0003 - Persistence (PERSISTENCE)
6. TA0004 - Privilege Escalation (PRIV ESC)
7. TA0005 - Defense Evasion (EVASION)
8. TA0006 - Credential Access (CREDS)
9. TA0007 - Discovery (DISCOVERY)
10. TA0008 - Lateral Movement (LATERAL)
11. TA0009 - Collection (COLLECT)
12. TA0011 - Command and Control (C2)
13. TA0010 - Exfiltration (EXFIL)
14. TA0040 - Impact (IMPACT)

### 34 Herramientas de Red Team
- **Reconnaissance**: nmap, masscan, subfinder, amass, theharvester, whatweb, wafw00f, gobuster, feroxbuster, shodan, nuclei
- **Initial Access**: nikto, sqlmap, hydra, crackmapexec, kerbrute
- **Execution**: msfvenom, metasploit
- **Privilege Escalation**: linpeas, winpeas, linux_exploit_suggester
- **Credential Access**: mimikatz, secretsdump, hashcat, john, rubeus
- **Lateral Movement**: psexec, wmiexec, evil-winrm, smbexec
- **Discovery**: bloodhound, sharphound
- **C2**: chisel, ligolo

### 35+ Módulos Metasploit
- **Exploits**: Shellshock, Log4Shell, Spring4Shell, EternalBlue, PwnKit, Dirty Pipe, etc.
- **Auxiliary**: Scanners (SMB, SSH, MySQL, RDP, VNC)
- **Post**: Hashdump, Credential Collector, Exploit Suggester, Process Migration

## What's Been Implemented (Jan 2026)

### Core Features
- [x] Kill Chain visual con 14 tácticas MITRE
- [x] 34 herramientas de Red Team categorizadas
- [x] 35+ módulos Metasploit con mapeo MITRE
- [x] Árbol de ataque dinámico con nodos por fase
- [x] Análisis IA como Red Team Advisor
- [x] Consola Metasploit con LHOST/LPORT
- [x] Filtros por categoría (exploit/auxiliary/post)
- [x] Historial de operaciones

### API Endpoints
- GET /api/mitre/tactics - 14 tácticas ATT&CK
- GET /api/tools - 34 herramientas por fase
- GET /api/metasploit/modules - 35+ módulos MSF
- POST /api/scan/start - Iniciar con phases
- GET /api/scan/{id}/tree - Árbol MITRE
- POST /api/metasploit/execute - Exploit con LHOST

## Prioritized Backlog

### P0 - Completado
- ✅ MITRE ATT&CK Kill Chain completo
- ✅ Base de datos de herramientas Red Team
- ✅ Módulos Metasploit con mapeo MITRE
- ✅ IA Red Team Advisor

### P1 (High)
- [ ] Instalar herramientas reales en Kali
- [ ] Conexión msfrpcd real
- [ ] Cobalt Strike integration
- [ ] C2 Framework (ligolo-ng real)

### P2 (Medium)
- [ ] BloodHound integration
- [ ] Active Directory attack paths
- [ ] Kerberos attacks (Rubeus real)
- [ ] Exportar PDF con MITRE mapping

## Next Tasks
1. Desplegar en Kali Linux con herramientas reales
2. Configurar msfrpcd para Metasploit real
3. Integrar BloodHound para AD recon
4. Agregar más técnicas de evasión
