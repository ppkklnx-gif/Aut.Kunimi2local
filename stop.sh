#!/bin/bash
# Detener Red Team Framework
echo "[*] Deteniendo backend..."
pkill -f "uvicorn server:app" 2>/dev/null && echo "[+] Backend detenido" || echo "[*] Backend no estaba corriendo"

echo "[*] Deteniendo Docker (frontend + MongoDB)..."
docker compose down 2>/dev/null && echo "[+] Docker detenido" || echo "[*] Docker no estaba corriendo"

echo "[+] Framework detenido"
echo ""
echo "Para limpiar todo (incluyendo base de datos):"
echo "  docker compose down -v"
