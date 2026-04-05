#!/bin/bash
# Red Team Framework v5.0 - Start Script
# Handles log permissions, path detection, and service startup
set -e

# Detect current user (the actual user, not root)
REAL_USER="${SUDO_USER:-$(whoami)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "[*] Red Team Framework v5.0"
echo "[*] Directory: $SCRIPT_DIR"
echo "[*] User: $REAL_USER"

# Create log directory with correct ownership
mkdir -p "$LOG_DIR"
if [ "$(whoami)" = "root" ] && [ -n "$SUDO_USER" ]; then
    chown -R "$SUDO_USER:$SUDO_USER" "$LOG_DIR"
fi

# Fix existing log file permissions
for f in "$LOG_DIR"/*.log; do
    [ -f "$f" ] && chown "$REAL_USER:$REAL_USER" "$f" 2>/dev/null || true
done

# Check MongoDB
echo "[*] Checking MongoDB..."
if systemctl is-active --quiet mongod 2>/dev/null; then
    echo "[+] MongoDB: RUNNING"
elif mongod --version &>/dev/null; then
    echo "[!] MongoDB installed but not running. Starting..."
    sudo systemctl start mongod 2>/dev/null || mongod --fork --logpath /var/log/mongodb/mongod.log --dbpath /var/lib/mongodb 2>/dev/null || echo "[-] Failed to start MongoDB. Start it manually."
else
    echo "[-] MongoDB not found. Install: sudo apt install -y mongodb-org"
fi

# Check .env files
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "[!] Creating backend/.env from template..."
    cat > "$BACKEND_DIR/.env" << 'ENVEOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=redteam_framework
KIMI_API_KEY=
MSF_RPC_TOKEN=
MSF_RPC_HOST=127.0.0.1
MSF_RPC_PORT=55553
SLIVER_CONFIG_PATH=
ENVEOF
    [ -n "$SUDO_USER" ] && chown "$SUDO_USER:$SUDO_USER" "$BACKEND_DIR/.env"
    echo "[!] Edit backend/.env to add your API keys and config paths"
fi

if [ ! -f "$FRONTEND_DIR/.env" ]; then
    echo "[!] Creating frontend/.env..."
    echo "REACT_APP_BACKEND_URL=http://localhost:8001" > "$FRONTEND_DIR/.env"
    [ -n "$SUDO_USER" ] && chown "$SUDO_USER:$SUDO_USER" "$FRONTEND_DIR/.env"
fi

# Stop existing processes
echo "[*] Stopping existing processes..."
pkill -f "uvicorn server:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
sleep 1

# Start Backend
echo "[*] Starting Backend (port 8001)..."
if [ "$(whoami)" = "root" ] && [ -n "$SUDO_USER" ]; then
    su - "$REAL_USER" -c "cd '$BACKEND_DIR' && nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > '$LOG_DIR/backend.log' 2>&1 &"
else
    cd "$BACKEND_DIR"
    nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > "$LOG_DIR/backend.log" 2>&1 &
fi
echo "[+] Backend PID: $!"

sleep 2

# Verify backend
if curl -s http://localhost:8001/api/ > /dev/null 2>&1; then
    echo "[+] Backend: RUNNING"
else
    echo "[!] Backend may be starting up... check $LOG_DIR/backend.log"
fi

# Start Frontend
echo "[*] Starting Frontend (port 3000)..."
if [ "$(whoami)" = "root" ] && [ -n "$SUDO_USER" ]; then
    su - "$REAL_USER" -c "cd '$FRONTEND_DIR' && nohup yarn start > '$LOG_DIR/frontend.log' 2>&1 &"
else
    cd "$FRONTEND_DIR"
    nohup yarn start > "$LOG_DIR/frontend.log" 2>&1 &
fi
echo "[+] Frontend PID: $!"

echo ""
echo "========================================="
echo "[+] Red Team Framework v5.0 Started"
echo "[+] Frontend: http://localhost:3000"
echo "[+] Backend:  http://localhost:8001/api/"
echo "[+] Logs:     $LOG_DIR/"
echo "========================================="
echo ""
echo "IMPORTANT: Configure your LHOST in the app:"
echo "  1. Open http://localhost:3000"
echo "  2. Go to CONFIG tab"
echo "  3. Set your VPS/Listener IP"
echo "  4. Click SAVE CONFIG"
echo ""
echo "To stop: pkill -f 'uvicorn server:app' && pkill -f 'react-scripts start'"
