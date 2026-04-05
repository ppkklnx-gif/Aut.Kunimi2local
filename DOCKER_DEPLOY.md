# Red Team Framework v5.0 — Guía de Instalación

---

## Arquitectura

```
┌────────── Docker ──────────┐
│                             │
│  ┌───────────┐ ┌─────────┐│
│  │ Frontend  │ │ MongoDB │││
│  │ (Nginx)   │ │ (Mongo7)│││
│  │ :3000     │ │ :27017  │││
│  └─────┬─────┘ └─────────┘│
│        │ proxy /api/       │
└────────│───────────────────┘
         │
         ↓ localhost:8001
┌──────── Kali Host ─────────┐
│                             │
│  ┌──────────┐ ┌──────────┐│
│  │ Backend  │ │ msfrpcd  ││
│  │ (FastAPI)│ │ :55553   ││
│  │ :8001    │ └──────────┘│
│  └──────────┘              │
│  ┌──────────┐ ┌──────────┐│
│  │ sliver   │ │ nmap     ││
│  │ server   │ │ nikto    ││
│  └──────────┘ │ gobuster ││
│               └──────────┘│
└─────────────────────────────┘
```

**Docker:** Frontend (React compilado + Nginx) y MongoDB. Limpio, portable, sin configuración.

**Kali host:** Backend (FastAPI), msfrpcd, Sliver, nmap, nikto, y todas las herramientas ofensivas. Comunicación directa, sin barreras de red.

---

## PASO 0: Requisitos en Kali

### 0.1 Actualizar sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 0.2 Docker

```bash
sudo apt install -y docker.io
docker --version
```

Si no muestra versión:
```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 0.3 Docker Compose

```bash
docker compose version
```

Si no funciona:
```bash
sudo apt install -y docker-compose-plugin
```

### 0.4 Docker sin sudo

```bash
sudo usermod -aG docker $USER
```

**Cierra la terminal y abre una nueva.** Verifica:
```bash
docker ps
```

Debe mostrar una tabla vacía sin error.

### 0.5 Python 3 y pip

```bash
python3 --version    # Debe ser 3.9+
pip3 --version
```

Si falta pip:
```bash
sudo apt install -y python3-pip
```

### 0.6 Herramientas ofensivas

```bash
sudo apt install -y nmap nikto gobuster
```

### 0.7 Checklist

```bash
docker --version          # Docker 20+
docker compose version    # Compose v2+
docker ps                 # Sin error
python3 --version         # 3.9+
pip3 --version            # Cualquiera
nmap --version            # Cualquiera
```

Todos deben funcionar. Si sí, continúa.

---

## PASO 1: Descargar

```bash
cd ~
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

Verifica:
```bash
ls docker-compose.yml start.sh stop.sh backend/server.py frontend/Dockerfile
```

Los 5 archivos deben existir.

---

## PASO 2: Configurar

### 2.1 Crear el .env del backend

```bash
cp .env.docker backend/.env
```

### 2.2 Editar

```bash
nano backend/.env
```

### 2.3 Qué cambiar

```env
# TU API KEY DE MOONSHOT (para análisis AI)
# Sin ella la app funciona pero sin análisis inteligente
KIMI_API_KEY=sk-xxxxxxxxxxxxxxxx

# IP DE TU VPS / MÁQUINA ATACANTE
# Esta IP se inyecta automáticamente en TODOS los payloads
# Para ver tu IP: ip addr show | grep 'inet ' | grep -v 127.0.0.1
# Con Tailscale: tailscale ip -4
LISTENER_IP=100.88.122.107
LISTENER_PORT=4444

# PASSWORD DE msfrpcd (el mismo que usas con msfrpcd -P)
# Si no usas Metasploit: déjalo vacío
MSF_RPC_TOKEN=MiTokenSecreto123

# RUTA AL CONFIG DE SLIVER
# Si no usas Sliver: déjalo vacío
# Debe apuntar al ARCHIVO .cfg, NO al directorio
# Ejemplo: /home/pp/.sliver-client/configs/default.cfg
SLIVER_CONFIG_PATH=
```

**NO cambiar:** `MONGO_URL`, `DB_NAME`, `MSF_RPC_HOST`, `MSF_RPC_PORT`, `CORS_ORIGINS`.

### 2.4 Guardar

`Ctrl+O` → `Enter` → `Ctrl+X`

---

## PASO 3: Instalar dependencias Python

```bash
cd ~/TU_REPOSITORIO
pip3 install -r backend/requirements.docker.txt
```

Si algún paquete falla:
```bash
sudo apt install -y python3-dev gcc libffi-dev
pip3 install -r backend/requirements.docker.txt
```

Verificar que instaló bien:
```bash
python3 -c "import fastapi, motor, httpx, pymetasploit3; print('OK')"
```

Debe imprimir `OK`.

---

## PASO 4: Levantar todo

### 4.1 Un solo comando

```bash
cd ~/TU_REPOSITORIO
./start.sh
```

Esto hace todo automáticamente:
1. Levanta MongoDB + Frontend en Docker
2. Espera a que Mongo esté listo
3. Inicia el backend en tu Kali
4. Verifica conectividad

Salida esperada:
```
[1/4] Levantando Docker (MongoDB + Frontend)...
[+] MongoDB: LISTO (puerto 27017)
[2/4] Verificando dependencias Python...
[+] Dependencias Python: OK
[3/4] Iniciando Backend...
[+] Backend: LISTO (puerto 8001, PID 12345)
[4/4] Verificación...
[+] MongoDB: connected
[+] Listener: 100.88.122.107:4444
[*] MSF RPC: OFFLINE

═══════════════════════════════════════════
 Framework listo
 UI:      http://localhost:3000
 API:     http://localhost:8001/api/
═══════════════════════════════════════════
```

### 4.2 Abrir en navegador

```
http://localhost:3000
```

Debes ver el dashboard oscuro con tema Cyberpunk.
En el sidebar: `LHOST: 100.88.122.107` en verde.

---

## PASO 5: Conectar Metasploit RPC

### 5.1 Iniciar msfrpcd

En otra terminal:
```bash
msfrpcd -P MiTokenSecreto123 -S -a 127.0.0.1 -p 55553
```

Usa el **mismo password** que pusiste en `MSF_RPC_TOKEN`.

### 5.2 Verificar que escucha

```bash
ss -tlnp | grep 55553
```

Debe mostrar `LISTEN`.

### 5.3 Verificar conexión

```bash
curl -s http://localhost:8001/api/msf/diagnostics | python3 -m json.tool
```

Esperado:
```json
{
    "connected": true,
    "host": "127.0.0.1",
    "port": 55553,
    "token_set": true,
    "port_reachable": true,
    "reconnecting": false
}
```

`connected: true` = Metasploit operativo.

### 5.4 Verificar en la UI

1. Click en **C2** en el sidebar
2. Panel **Metasploit RPC** debe mostrar **ONLINE** en verde
3. Muestra versión de MSF y número de sesiones

Si dice OFFLINE, click en **RECONNECT** y revisa los diagnostics.

---

## PASO 6: Conectar Sliver (opcional)

### 6.1 Instalar Sliver

```bash
curl https://sliver.sh/install | sudo bash
```

### 6.2 Iniciar servidor

En otra terminal:
```bash
sliver-server
```

### 6.3 Generar config de operador

Dentro de la consola Sliver (reemplaza TU_USER con tu usuario):
```
new-operator --name redteam --lhost 127.0.0.1 --save /home/TU_USER/.sliver-client/configs/default.cfg
```

### 6.4 Configurar la ruta en el backend

```bash
nano backend/.env
```

Cambiar:
```env
SLIVER_CONFIG_PATH=/home/TU_USER/.sliver-client/configs/default.cfg
```

Reiniciar backend:
```bash
pkill -f "uvicorn server:app"
cd backend && nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /tmp/redteam-backend.log 2>&1 &
```

### 6.5 Verificar

```bash
curl -s http://localhost:8001/api/sliver/status | python3 -m json.tool
```

Busca `"connected": true`.

En la UI: **C2** → panel Sliver debe mostrar **ONLINE**.

---

## PASO 7: Prueba mínima (5 tests)

Copia y pega todo este bloque en tu terminal:

```bash
echo "=== TEST 1: Backend ==="
curl -sf http://localhost:8001/api/ > /dev/null && echo "PASS" || echo "FAIL"

echo "=== TEST 2: MongoDB ==="
curl -s http://localhost:8001/api/health | python3 -c "
import sys, json; d = json.load(sys.stdin)
print('PASS' if d['checks']['mongodb']['status'] == 'connected' else 'FAIL')
"

echo "=== TEST 3: Listener configurado ==="
curl -s http://localhost:8001/api/health | python3 -c "
import sys, json; c = json.load(sys.stdin)['checks']['listener']
print(f'PASS (LHOST={c[\"ip\"]}:{c[\"port\"]})' if c['configured'] else 'FAIL: LISTENER_IP vacio en .env')
"

echo "=== TEST 4: Scan funcional ==="
SCAN_ID=\$(curl -s -X POST http://localhost:8001/api/scan/start \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","scan_phases":["reconnaissance"],"tools":["nmap"]}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['scan_id'])")
echo "  Scan: \$SCAN_ID (esperando 15s...)"
sleep 15
STATUS=\$(curl -s http://localhost:8001/api/scan/\$SCAN_ID/status \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
[ "\$STATUS" = "completed" ] && echo "PASS" || echo "FAIL (status=\$STATUS)"

echo "=== TEST 5: Frontend ==="
curl -sf http://localhost:3000 > /dev/null && echo "PASS" || echo "FAIL"
```

**Resultado esperado: 5/5 PASS.**

Si MSF está corriendo, agrega:
```bash
echo "=== TEST 6: MSF RPC ==="
curl -s http://localhost:8001/api/msf/diagnostics | python3 -c "
import sys, json; d = json.load(sys.stdin)
print('PASS' if d['connected'] else f'FAIL: {d.get(\"last_error\",\"?\")}')
"
```

---

## Detener

```bash
./stop.sh
```

Esto detiene el backend y Docker.

## Reiniciar desde cero

```bash
# Parar todo
./stop.sh

# Borrar base de datos
docker compose down -v

# Limpiar imágenes Docker
docker system prune -f

# Levantar todo limpio
./start.sh
```

---

## Comandos del día a día

```bash
# Iniciar
./start.sh

# Parar
./stop.sh

# Ver logs del backend
tail -f /tmp/redteam-backend.log

# Reiniciar solo backend (después de cambiar .env)
pkill -f "uvicorn server:app"
cd backend && nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /tmp/redteam-backend.log 2>&1 &

# Reconstruir frontend (después de git pull)
docker compose up -d --build frontend

# Estado de Docker
docker compose ps

# Entrar a MongoDB
docker compose exec mongo mongosh redteam_framework
```

---

## Troubleshooting

### Backend no arranca
```bash
tail -20 /tmp/redteam-backend.log
# Si dice "ModuleNotFoundError": pip3 install -r backend/requirements.docker.txt
# Si dice "Address already in use": pkill -f "uvicorn server:app" y vuelve a iniciar
```

### MongoDB no arranca
```bash
docker compose logs mongo
# Si dice permission denied:
docker compose down -v
docker compose up -d
```

### Frontend en blanco
```bash
docker compose logs frontend
# Si dice "502 Bad Gateway": el backend no está corriendo. Ejecuta ./start.sh
```

### MSF RPC dice OFFLINE
```bash
# 1. Verificar que msfrpcd corre
ss -tlnp | grep 55553

# 2. Si no corre, iniciarlo
msfrpcd -P TU_TOKEN -S -a 127.0.0.1 -p 55553

# 3. Verificar token
grep MSF_RPC_TOKEN backend/.env
# Debe coincidir con el -P de msfrpcd

# 4. Forzar reconexión
curl -s -X POST http://localhost:8001/api/msf/connect | python3 -m json.tool
```

### Sliver dice "is a directory"
```bash
# SLIVER_CONFIG_PATH debe apuntar al ARCHIVO, no al directorio
# Incorrecto: /home/pp/.sliver-client
# Correcto:   /home/pp/.sliver-client/configs/default.cfg

# Buscar archivos .cfg
find ~/.sliver-client -name "*.cfg"
# Copiar la ruta del archivo a backend/.env
```
