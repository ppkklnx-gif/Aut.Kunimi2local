# Red Team Automation Framework v5.0

Plataforma de automatización Red Team con orquestación adaptativa, C2 (Metasploit + Sliver), generador de payloads, y análisis AI.

## Instalación rápida

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
cp .env.docker .env
nano .env              # Configura tus keys
docker compose up -d --build
```

Abrir: `http://localhost:3000`

## Documentación completa

**[DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)** — Guía paso a paso desde cero (Docker, .env, MSF RPC, Sliver, verificación, troubleshooting).

## Stack

| Componente | Tecnología |
|---|---|
| Frontend | React, Tailwind, Shadcn UI, Nginx |
| Backend | FastAPI, Python, nmap, nikto, gobuster |
| Database | MongoDB 7 |
| C2 | Metasploit RPC, Sliver C2 |
| AI | Moonshot/Kimi K2 |
| Deploy | Docker Compose |
