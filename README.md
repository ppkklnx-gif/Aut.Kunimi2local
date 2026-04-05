# Red Team Automation Framework v5.0

Plataforma de automatización Red Team con orquestación adaptativa, C2 (Metasploit + Sliver), generador de payloads, y análisis AI.

## Instalación

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
cp .env.docker backend/.env
nano backend/.env       # Configura tus keys
./start.sh
```

Abrir: `http://localhost:3000`

Documentación completa: **[DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)**

## Arquitectura

| Componente | Dónde corre | Tecnología |
|---|---|---|
| Frontend | Docker | React, Nginx |
| MongoDB | Docker | Mongo 7 |
| Backend | Kali host | FastAPI, Python |
| MSF RPC | Kali host | msfrpcd |
| Sliver C2 | Kali host | sliver-server |
| Herramientas | Kali host | nmap, nikto, gobuster |
| AI | API externa | Moonshot/Kimi K2 |
