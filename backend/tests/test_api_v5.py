"""
Red Team Framework v5.0 API Tests
Tests for hybrid architecture: Frontend+MongoDB in Docker, Backend on Kali host
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRootEndpoint:
    """Test GET /api/ - Version and features"""
    
    def test_root_returns_version_5(self):
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "5.0.0"
        assert "docker" in data["features"]
        assert "message" in data
        print(f"✓ Root endpoint: version={data['version']}, features={data['features']}")


class TestHealthEndpoint:
    """Test GET /api/health - MongoDB, listener, MSF/Sliver status"""
    
    def test_health_returns_mongodb_connected(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["checks"]["mongodb"]["status"] == "connected"
        print(f"✓ MongoDB status: {data['checks']['mongodb']['status']}")
    
    def test_health_returns_listener_configured(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        listener = data["checks"]["listener"]
        assert "ip" in listener
        assert "port" in listener
        assert "configured" in listener
        print(f"✓ Listener: {listener['ip']}:{listener['port']} configured={listener['configured']}")
    
    def test_health_returns_msf_status(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        msf = data["checks"]["msf_rpc"]
        assert "connected" in msf
        assert "host" in msf
        assert "port" in msf
        print(f"✓ MSF RPC: host={msf['host']}:{msf['port']} connected={msf['connected']}")
    
    def test_health_returns_sliver_status(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        sliver = data["checks"]["sliver"]
        assert "connected" in sliver
        print(f"✓ Sliver: connected={sliver['connected']}")


class TestConfigEndpoint:
    """Test GET/PUT /api/config - Global config with listener_ip"""
    
    def test_config_returns_listener_ip(self):
        response = requests.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "listener_ip" in data
        assert "listener_port" in data
        print(f"✓ Config: listener_ip={data['listener_ip']}:{data['listener_port']}")
    
    def test_config_update(self):
        # Get current config
        response = requests.get(f"{BASE_URL}/api/config")
        original = response.json()
        
        # Update config
        update_data = {
            "listener_ip": original.get("listener_ip", "10.10.14.5"),
            "listener_port": original.get("listener_port", 4444)
        }
        response = requests.put(f"{BASE_URL}/api/config", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        print(f"✓ Config update: status={data['status']}")


class TestPayloadsEndpoint:
    """Test GET /api/payloads/templates - Returns 11 payloads"""
    
    def test_payloads_returns_11_templates(self):
        response = requests.get(f"{BASE_URL}/api/payloads/templates")
        assert response.status_code == 200
        data = response.json()
        assert "payloads" in data
        assert len(data["payloads"]) == 11
        print(f"✓ Payloads: count={len(data['payloads'])}")
    
    def test_payloads_have_lhost(self):
        response = requests.get(f"{BASE_URL}/api/payloads/templates")
        assert response.status_code == 200
        data = response.json()
        assert "global_lhost" in data
        assert "global_lport" in data
        # Check each payload has lhost_configured
        for payload in data["payloads"]:
            assert "lhost_configured" in payload
        print(f"✓ Payloads LHOST: {data['global_lhost']}:{data['global_lport']}")
    
    def test_payload_generate(self):
        response = requests.post(f"{BASE_URL}/api/payloads/generate", json={
            "payload_id": "bash_reverse",
            "lport": 4444
        })
        assert response.status_code == 200
        data = response.json()
        assert "lhost" in data
        assert "generator_cmd" in data
        assert "handler_cmd" in data
        print(f"✓ Payload generate: lhost={data['lhost']}")


class TestC2Dashboard:
    """Test GET /api/c2/dashboard - MSF and Sliver diagnostics"""
    
    def test_c2_dashboard_returns_msf_diagnostics(self):
        response = requests.get(f"{BASE_URL}/api/c2/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "metasploit" in data
        msf = data["metasploit"]
        assert "diagnostics" in msf
        assert "port_reachable" in msf["diagnostics"]
        print(f"✓ C2 Dashboard MSF: port_reachable={msf['diagnostics']['port_reachable']}")
    
    def test_c2_dashboard_returns_sliver_diagnostics(self):
        response = requests.get(f"{BASE_URL}/api/c2/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "sliver" in data
        sliver = data["sliver"]
        assert "diagnostics" in sliver
        print(f"✓ C2 Dashboard Sliver: connected={sliver['connected']}")


class TestMSFDiagnostics:
    """Test GET /api/msf/diagnostics - Connection details with port_reachable"""
    
    def test_msf_diagnostics_has_port_reachable(self):
        response = requests.get(f"{BASE_URL}/api/msf/diagnostics")
        assert response.status_code == 200
        data = response.json()
        assert "port_reachable" in data
        assert "host" in data
        assert "port" in data
        assert "token_set" in data
        print(f"✓ MSF Diagnostics: host={data['host']}:{data['port']} port_reachable={data['port_reachable']}")


class TestScanEndpoints:
    """Test POST /api/scan/start and GET /api/scan/{id}/status"""
    
    def test_scan_start_and_status(self):
        # Start scan
        response = requests.post(f"{BASE_URL}/api/scan/start", json={
            "target": "scanme.nmap.org",
            "scan_phases": ["reconnaissance"],
            "tools": ["nmap"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        scan_id = data["scan_id"]
        print(f"✓ Scan started: scan_id={scan_id}")
        
        # Check status (may be running or completed)
        import time
        time.sleep(3)
        response = requests.get(f"{BASE_URL}/api/scan/{scan_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["running", "completed"]
        print(f"✓ Scan status: {data['status']}")


class TestChainsEndpoint:
    """Test GET /api/chains - Returns 6 chains"""
    
    def test_chains_returns_6(self):
        response = requests.get(f"{BASE_URL}/api/chains")
        assert response.status_code == 200
        data = response.json()
        assert "chains" in data
        assert len(data["chains"]) == 6
        
        # Verify chain names
        chain_ids = [c["id"] for c in data["chains"]]
        expected = ["web_to_shell", "smb_to_domain", "kerberos_attack", "linux_privesc", "windows_privesc", "phishing_to_shell"]
        for expected_id in expected:
            assert expected_id in chain_ids, f"Missing chain: {expected_id}"
        
        print(f"✓ Chains: count={len(data['chains'])}, ids={chain_ids}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
