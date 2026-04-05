# Red Team Framework v5.0 — Guía de Instalación Completa

---

## PASO 0: Requisitos previos en tu Kali Linux

Abre una terminal y ejecuta cada comando. Si alguno falla, sigue las instrucciones de error antes de continuar.

### 0.1 Actualizar sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 0.2 Instalar Docker

```bash
sudo apt install -y docker.io
docker --version
```

Debe mostrar: `Docker version 24.x.x` o superior.

Si no muestra nada:
```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 0.3 Instalar Docker Compose

```bash
docker compose version
```

Debe mostrar: `Docker Compose version v2.x.x`

Si no funciona:
```bash
sudo apt install -y docker-compose-plugin
```

### 0.4 Configurar Docker para tu usuario

```bash
sudo usermod -aG docker $USER
```

**Cierra la terminal y abre una nueva.** Luego verifica:

```bash
docker ps
```

Debe mostrar una tabla vacía sin error de permisos. Si falla, reinicia tu Kali: `sudo reboot`

### 0.5 Checklist

```bash
docker --version          # Docker 24+
docker compose version    # Compose v2+
docker ps                 # Sin error
```

Los 3 deben funcionar. Si sí, continúa.

---

## PASO 1: Descargar el proyecto

```bash
cd ~
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

Verifica que existen los archivos clave:

```bash
ls docker-compose.yml .env.docker backend/Dockerfile frontend/Dockerfile
```

Debes ver los 4 archivos listados sin error.

---

## PASO 2: Configurar el archivo .env

### 2.1 Copiar la plantilla

```bash
cp .env.docker .env
```

### 2.2 Editar

```bash
nano .env
```

### 2.3 Qué cambiar

| Variable | Qué es | Ejemplo | Obligatorio |
|---|---|---|---|
| `KIMI_API_KEY` | API key de Moonshot/Kimi para análisis AI | `sk-4zTj5qt...` | No (app funciona sin AI) |
| `LISTENER_IP` | IP de tu VPS donde recibes shells | `100.88.122.107` | Sí para payloads |
| `LISTENER_PORT` | Puerto del listener | `4444` | Ya tiene default |
| `MSF_RPC_TOKEN` | Password de msfrpcd | `MiToken123` | Sí para MSF |
| `MSF_RPC_HOST` | Dónde corre msfrpcd | `host.docker.internal` | Ya tiene default |
| `MSF_RPC_PORT` | Puerto de msfrpcd | `55553` | Ya tiene default |

**NO cambiar:** `MONGO_URL`, `DB_NAME`, `CORS_ORIGINS`, `FRONTEND_PORT`, `BACKEND_PORT`.

Para encontrar tu IP de listener:
```bash
# Si usas Tailscale
tailscale ip -4

# Si usas red local
ip addr show | grep 'inet ' | grep -v 127.0.0.1
```

### 2.4 Guardar

`Ctrl+O` → `Enter` → `Ctrl+X`

### 2.5 Verificar

```bash
grep -v '^#' .env | grep -v '^$'
```

Debes ver tus valores sin espacios alrededor de `=`.

---

## PASO 3: Levantar la aplicación

### 3.1 Construir e iniciar

```bash
docker compose up -d --build
```

La primera vez tarda 3-5 minutos. Verás descargas de imágenes y compilación.

### 3.2 Verificar que los 3 servicios corren

```bash
docker compose ps
```

Esperado:
```
NAME               STATUS          PORTS
redteam-mongo      Up (healthy)    27017/tcp
redteam-backend    Up (healthy)    0.0.0.0:8001->8001/tcp
redteam-frontend   Up (healthy)    0.0.0.0:3000->80/tcp
```

**Los 3 deben decir "Up".** Si alguno dice "Exit" o "Restarting", ve al Troubleshooting.

### 3.3 Verificar backend

```bash
curl -s http://localhost:8001/api/ | python3 -m json.tool
```

Debe responder con `"version": "5.0.0"`.

### 3.4 Health check completo

```bash
curl -s http://localhost:8001/api/health | python3 -m json.tool
```

Busca:
- `"mongodb": {"status": "connected"}` → Base de datos OK
- `"listener": {"configured": true}` → Tu IP de VPS cargada

---

## PASO 4: Abrir la aplicación

En tu navegador:

```
http://localhost:3000
```

Debes ver:
- Dashboard oscuro tema Cyberpunk/Matrix
- Sidebar con 9 secciones
- `LHOST: TU_IP` en verde en la parte inferior del sidebar

Si accedes desde otra máquina:
```
http://IP_DE_TU_KALI:3000
```

---

## PASO 5: Conectar Metasploit RPC

msfrpcd corre en tu Kali, fuera de Docker.

### 5.1 Iniciar msfrpcd

```bash
msfrpcd -P MiToken123 -S -a 0.0.0.0 -p 55553
```

Usa el **mismo password** que pusiste en `MSF_RPC_TOKEN` en tu `.env`.

### 5.2 Verificar que está escuchando

```bash
ss -tlnp | grep 55553
```

Debe mostrar una línea con `LISTEN`. Si no aparece, msfrpcd no arrancó.

### 5.3 Verificar conexión desde Docker

```bash
curl -s http://localhost:8001/api/msf/diagnostics | python3 -m json.tool
```

Resultado esperado cuando funciona:
```json
{
    "connected": true,
    "host": "host.docker.internal",
    "port": 55553,
    "token_set": true,
    "port_reachable": true,
    "reconnecting": false
}
```

### 5.4 Verificar visualmente en la UI

1. Abre `http://localhost:3000`
2. Click en **C2** en el sidebar
3. El panel **Metasploit RPC** debe mostrar:
   - **ONLINE** en verde
   - Versión de MSF
   - Número de sesiones activas

Si muestra **OFFLINE**:
- Click el botón **RECONNECT** azul en la parte superior
- Si sigue offline, revisa los diagnostics que aparecen debajo:
  - `Token set: NO` → Tu `MSF_RPC_TOKEN` está vacío en `.env`
  - `Port reachable: NO` → msfrpcd no está corriendo o `host.docker.internal` no funciona
  - `Auto-reconnecting...` → El backend está reintentando automáticamente

### 5.5 Si host.docker.internal no funciona

```bash
# Obtener IP del bridge Docker
ip addr show docker0 | grep 'inet '
# Ejemplo: inet 172.17.0.1/16

# Editar .env
nano .env
# Cambiar: MSF_RPC_HOST=172.17.0.1

# Reiniciar solo el backend
docker compose restart backend
```

---

## PASO 6: Conectar Sliver C2 (opcional)

### 6.1 Instalar Sliver

```bash
curl https://sliver.sh/install | sudo bash
```

### 6.2 Iniciar servidor

En una terminal separada:
```bash
sliver-server
```

### 6.3 Generar config de operador

Dentro de la consola Sliver:
```
new-operator --name redteam --lhost 127.0.0.1 --save /home/TU_USER/.sliver-client/configs/default.cfg
```

Reemplaza `TU_USER` con tu usuario (`whoami`).

### 6.4 Montar en Docker

```bash
nano docker-compose.yml
```

En la sección `backend:`, cambia volumes:

```yaml
    volumes:
      - /home/TU_USER/.sliver-client/configs:/configs:ro
```

Reinicia:
```bash
docker compose restart backend
```

### 6.5 Verificar que Sliver lee la ruta correcta

```bash
curl -s http://localhost:8001/api/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
s = d['checks']['sliver']
print(f'Connected: {s[\"connected\"]}')
print(f'Config path: {s[\"config_path\"]}')
"
```

Si dice `connected: false`, verifica los diagnostics detallados:

```bash
curl -s http://localhost:8001/api/sliver/status | python3 -m json.tool
```

Busca el campo `diagnostics`:
- `config_path_raw`: ruta que el backend intentó leer
- `resolved`: ruta final resuelta
- `validation_error`: si no es null, te dice exactamente qué falló (ej: "is a directory", "file not found", "permission denied")

En la UI: ve a **C2** y el panel de **Sliver C2** muestra los mismos diagnostics.

---

## PASO 7: Prueba mínima para confirmar que todo funciona

Ejecuta estos 5 comandos seguidos. Si los 5 pasan, el sistema está operativo:

```bash
echo "=== TEST 1: Backend responde ==="
curl -sf http://localhost:8001/api/ > /dev/null && echo "PASS" || echo "FAIL"

echo "=== TEST 2: MongoDB conectada ==="
curl -s http://localhost:8001/api/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
ok = d['checks']['mongodb']['status'] == 'connected'
print('PASS' if ok else 'FAIL: MongoDB no conectada')
"

echo "=== TEST 3: Listener configurado ==="
curl -s http://localhost:8001/api/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
ok = d['checks']['listener']['configured']
ip = d['checks']['listener']['ip']
print(f'PASS (LHOST={ip})' if ok else 'FAIL: LISTENER_IP no configurado en .env')
"

echo "=== TEST 4: Scan completo ==="
SCAN_ID=$(curl -s -X POST http://localhost:8001/api/scan/start \
  -H "Content-Type: application/json" \
  -d '{"target":"scanme.nmap.org","scan_phases":["reconnaissance"],"tools":["nmap"]}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['scan_id'])")
echo "Scan iniciado: $SCAN_ID (esperando 15s...)"
sleep 15
STATUS=$(curl -s http://localhost:8001/api/scan/$SCAN_ID/status | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
echo "Status: $STATUS"
[ "$STATUS" = "completed" ] && echo "PASS" || echo "FAIL: scan no completó"

echo "=== TEST 5: Frontend accesible ==="
curl -sf http://localhost:3000 > /dev/null && echo "PASS" || echo "FAIL"
```

**Resultado esperado:**
```
TEST 1: PASS
TEST 2: PASS
TEST 3: PASS (LHOST=100.88.122.107)
TEST 4: PASS
TEST 5: PASS
```

Si MSF RPC está corriendo, agrega este test extra:
```bash
echo "=== TEST 6: MSF RPC conectado ==="
curl -s http://localhost:8001/api/msf/diagnostics | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'PASS (v{d.get(\"version\",\"?\")})' if d['connected'] else f'FAIL: {d.get(\"last_error\",\"unknown\")}')
"
```

---

## Detener, limpiar y reiniciar desde cero

### Detener la aplicación (conserva datos)

```bash
docker compose down
```

Los datos de MongoDB se conservan en el volumen `mongo_data`.

Para volver a iniciar:
```bash
docker compose up -d
```

### Limpiar todo y empezar desde cero

Esto borra TODA la base de datos, configs guardadas, y historial de scans:

```bash
# Parar y borrar contenedores + volúmenes
docker compose down -v

# Borrar imágenes construidas (fuerza reconstrucción)
docker rmi redteam-backend redteam-frontend 2>/dev/null

# Limpiar cache de Docker (libera espacio)
docker system prune -f

# Reconstruir todo desde cero
docker compose up -d --build
```

### Reconstruir solo un servicio

```bash
# Solo backend (después de cambiar código Python)
docker compose up -d --build backend

# Solo frontend (después de cambiar código React)
docker compose up -d --build frontend

# Solo reiniciar (después de cambiar .env, sin reconstruir)
docker compose restart backend
```

### Nuclear: borrar absolutamente todo de Docker

```bash
docker compose down -v
docker system prune -af --volumes
# Esto borra TODAS las imágenes, contenedores y volúmenes de Docker
# Útil si algo está corrupto y quieres empezar limpio
docker compose up -d --build
```

---

## Comandos del día a día

```bash
# Iniciar (después de reiniciar Kali)
cd ~/TU_REPOSITORIO && docker compose up -d

# Parar
docker compose down

# Ver logs
docker compose logs -f              # Todos
docker compose logs -f backend      # Solo backend

# Estado
docker compose ps

# Reiniciar tras cambiar .env
docker compose restart backend

# Actualizar código (git pull)
git pull && docker compose up -d --build

# Debug: entrar al backend
docker compose exec backend bash

# Debug: entrar a MongoDB
docker compose exec mongo mongosh redteam_framework
```

---

## Troubleshooting

### "docker compose" no funciona
```bash
# Intenta con guión
docker-compose up -d --build
# Si tampoco, instala
sudo apt install -y docker-compose-plugin
```

### Un contenedor dice "Restarting" o "Exit"
```bash
docker compose logs SERVICIO
# Ejemplo: docker compose logs backend
```

### Backend no arranca: "ModuleNotFoundError"
```bash
# Reconstruir imagen
docker compose up -d --build backend
```

### "permission denied" al ejecutar docker
```bash
sudo usermod -aG docker $USER
# Cerrar terminal, abrir nueva
```

### MongoDB no arranca
```bash
docker compose logs mongo
# Si dice "permission denied" en /data/db:
docker compose down -v
docker compose up -d
```

### Frontend en blanco
```bash
docker compose exec frontend ls /usr/share/nginx/html/
# Si no hay archivos: reconstruir
docker compose up -d --build frontend
```

### host.docker.internal no resuelve
```bash
# Buscar IP del bridge
ip addr show docker0 | grep 'inet '
# Poner esa IP en .env como MSF_RPC_HOST
nano .env
docker compose restart backend
```
