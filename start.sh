#!/bin/bash
# ═══════════════════════════════════════════════════════════
# Red Team Framework v5.0 - Start
# Levanta: Docker (frontend + mongo) + Backend (local)
# ═══════════════════════════════════════════════════════════
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

RED='\033[0;91m'
GREEN='\033[0;92m'
CYAN='\033[0;96m'
DIM='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${RED}╔═══════════════════════════════════════════╗${NC}"
echo -e "${RED}║${GREEN}  RED TEAM FRAMEWORK v5.0                  ${RED}║${NC}"
echo -e "${RED}╚═══════════════════════════════════════════╝${NC}"
echo ""

# ─── 1. Verificar .env ───────────────────────────────────
if [ ! -f "$DIR/backend/.env" ]; then
    echo -e "${CYAN}[*]${NC} Creando backend/.env desde plantilla..."
    cp "$DIR/.env.docker" "$DIR/backend/.env"
    echo -e "${RED}[!]${NC} Edita backend/.env con tus API keys: nano backend/.env"
    echo -e "${RED}[!]${NC} Luego ejecuta este script de nuevo."
    exit 1
fi

# ─── 2. Docker: MongoDB + Frontend ──────────────────────
echo -e "${CYAN}[1/4]${NC} Levantando Docker (MongoDB + Frontend)..."
docker compose up -d --build 2>&1 | tail -5

# Esperar a que Mongo esté healthy
echo -e "${DIM}      Esperando MongoDB...${NC}"
for i in $(seq 1 30); do
    if docker compose exec -T mongo mongosh --eval "db.runCommand({ping:1})" --quiet 2>/dev/null | grep -q "ok"; then
        echo -e "${GREEN}[+]${NC} MongoDB: LISTO (puerto 27017)"
        break
    fi
    sleep 1
    [ $i -eq 30 ] && echo -e "${RED}[-]${NC} MongoDB no respondió en 30s. Verifica con: docker compose logs mongo"
done

# ─── 3. Dependencias Python ─────────────────────────────
echo -e "${CYAN}[2/4]${NC} Verificando dependencias Python..."
if ! python3 -c "import fastapi, motor, httpx" 2>/dev/null; then
    echo -e "${DIM}      Instalando dependencias...${NC}"
    pip3 install -r "$DIR/backend/requirements.docker.txt" -q 2>/dev/null
fi
echo -e "${GREEN}[+]${NC} Dependencias Python: OK"

# ─── 4. Backend ─────────────────────────────────────────
echo -e "${CYAN}[3/4]${NC} Iniciando Backend..."
pkill -f "uvicorn server:app" 2>/dev/null || true
sleep 1

cd "$DIR/backend"
nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /tmp/redteam-backend.log 2>&1 &
BACKEND_PID=$!
cd "$DIR"

# Esperar a que responda
for i in $(seq 1 15); do
    if curl -sf http://localhost:8001/api/ > /dev/null 2>&1; then
        echo -e "${GREEN}[+]${NC} Backend: LISTO (puerto 8001, PID $BACKEND_PID)"
        break
    fi
    sleep 1
    [ $i -eq 15 ] && echo -e "${RED}[-]${NC} Backend no respondió. Log: tail -f /tmp/redteam-backend.log"
done

# ─── 5. Verificación ────────────────────────────────────
echo -e "${CYAN}[4/4]${NC} Verificación..."

HEALTH=$(curl -s http://localhost:8001/api/health 2>/dev/null)
if [ -n "$HEALTH" ]; then
    MONGO_OK=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['checks']['mongodb']['status'])" 2>/dev/null)
    LISTENER=$(echo "$HEALTH" | python3 -c "import sys,json; c=json.load(sys.stdin)['checks']['listener']; print(f\"{c['ip']}:{c['port']}\" if c['configured'] else 'NO CONFIGURADO')" 2>/dev/null)
    MSF_OK=$(echo "$HEALTH" | python3 -c "import sys,json; print('ONLINE' if json.load(sys.stdin)['checks']['msf_rpc']['connected'] else 'OFFLINE')" 2>/dev/null)

    echo -e "${GREEN}[+]${NC} MongoDB: $MONGO_OK"
    echo -e "${GREEN}[+]${NC} Listener: $LISTENER"
    echo -e "$([ "$MSF_OK" = "ONLINE" ] && echo "${GREEN}[+]" || echo "${DIM}[*]")${NC} MSF RPC: $MSF_OK"
fi

echo ""
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo -e "${GREEN} Framework listo${NC}"
echo -e "${BOLD} UI:      ${CYAN}http://localhost:3000${NC}"
echo -e "${BOLD} API:     ${CYAN}http://localhost:8001/api/${NC}"
echo -e "${BOLD} Health:  ${CYAN}http://localhost:8001/api/health${NC}"
echo -e "${BOLD} Logs:    ${DIM}tail -f /tmp/redteam-backend.log${NC}"
echo -e "${BOLD}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${DIM}Para detener: ./stop.sh${NC}"
