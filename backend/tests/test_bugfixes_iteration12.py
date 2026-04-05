"""
Test suite for 5 critical bugfixes from Kali deployment incident report:
1. MSF RPC handshake failures - diagnostics, SSL/non-SSL fallback, exponential backoff
2. Sliver config path validation - directory vs file error detection
3. Frontend attackTree.nodes.map crash - nodes is dict not array
4. Log permission issues with sudo (not testable via API)
5. Portability - no hardcoded paths (code review)

Tests verify the diagnostic quality and error handling improvements.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMSFDiagnostics:
    """Test MSF RPC diagnostic improvements - Issue #1"""
    
    def test_msf_status_returns_diagnostics_fields(self):
        """GET /api/msf/status should return token_set, port_reachable, reconnecting fields"""
        response = requests.get(f"{BASE_URL}/api/msf/status")
        assert response.status_code == 200
        data = response.json()
        
        # Must have diagnostics object with required fields
        assert "diagnostics" in data, "Response missing 'diagnostics' field"
        diag = data["diagnostics"]
        
        assert "token_set" in diag, "diagnostics missing 'token_set'"
        assert "port_reachable" in diag, "diagnostics missing 'port_reachable'"
        assert "reconnecting" in diag, "diagnostics missing 'reconnecting'"
        
        # Verify types
        assert isinstance(diag["token_set"], bool), "token_set should be boolean"
        assert isinstance(diag["port_reachable"], bool), "port_reachable should be boolean"
        assert isinstance(diag["reconnecting"], bool), "reconnecting should be boolean"
        
        print(f"MSF Status diagnostics: token_set={diag['token_set']}, port_reachable={diag['port_reachable']}, reconnecting={diag['reconnecting']}")
    
    def test_msf_status_returns_error_and_hint_when_offline(self):
        """GET /api/msf/status should return error and hint when MSF is offline"""
        response = requests.get(f"{BASE_URL}/api/msf/status")
        assert response.status_code == 200
        data = response.json()
        
        # Since MSF RPC is offline, we expect connected=False
        assert data.get("connected") == False, "Expected connected=False when MSF offline"
        
        # Should have error message
        assert "error" in data, "Response missing 'error' field when offline"
        assert len(data["error"]) > 0, "Error message should not be empty"
        
        # Should have hint for user
        assert "hint" in data, "Response missing 'hint' field when offline"
        assert len(data["hint"]) > 0, "Hint should not be empty"
        
        print(f"MSF offline error: {data['error']}")
        print(f"MSF offline hint: {data['hint']}")
    
    def test_msf_diagnostics_endpoint(self):
        """GET /api/msf/diagnostics should return detailed connection info"""
        response = requests.get(f"{BASE_URL}/api/msf/diagnostics")
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        required_fields = ["connected", "host", "port", "token_set", "port_reachable", "last_error", "retry_count", "reconnecting"]
        for field in required_fields:
            assert field in data, f"diagnostics missing '{field}'"
        
        # Verify host and port match expected config
        assert data["host"] == "127.0.0.1", f"Expected host 127.0.0.1, got {data['host']}"
        assert data["port"] == 55553, f"Expected port 55553, got {data['port']}"
        
        print(f"MSF Diagnostics: {data}")
    
    def test_msf_connect_forces_reconnect(self):
        """POST /api/msf/connect should force reconnect and return status"""
        response = requests.post(f"{BASE_URL}/api/msf/connect")
        assert response.status_code == 200
        data = response.json()
        
        # Should return status with diagnostics
        assert "connected" in data, "Response missing 'connected' field"
        assert "diagnostics" in data, "Response missing 'diagnostics' field"
        
        print(f"MSF Connect result: connected={data['connected']}")


class TestSliverConfigValidation:
    """Test Sliver config path validation - Issue #2"""
    
    def test_sliver_status_returns_validation_error_when_empty(self):
        """GET /api/sliver/status should return validation_error when SLIVER_CONFIG_PATH is empty"""
        response = requests.get(f"{BASE_URL}/api/sliver/status")
        assert response.status_code == 200
        data = response.json()
        
        # Since SLIVER_CONFIG_PATH is empty, we expect connected=False
        assert data.get("connected") == False, "Expected connected=False when config path empty"
        
        # Should have error message about config path
        assert "error" in data, "Response missing 'error' field"
        error_msg = data["error"].lower()
        assert "sliver_config_path" in error_msg or "not set" in error_msg, f"Error should mention config path: {data['error']}"
        
        # Should have hint
        assert "hint" in data, "Response missing 'hint' field"
        
        # Should have diagnostics with validation info
        assert "diagnostics" in data, "Response missing 'diagnostics' field"
        diag = data["diagnostics"]
        
        # config_path_raw should be empty or None
        assert diag.get("config_path_raw") == "" or diag.get("config_path_raw") is None, "config_path_raw should be empty"
        
        print(f"Sliver status error: {data['error']}")
        print(f"Sliver diagnostics: {diag}")
    
    def test_sliver_reconnect_endpoint(self):
        """POST /api/sliver/reconnect should force reconnect"""
        response = requests.post(f"{BASE_URL}/api/sliver/reconnect")
        assert response.status_code == 200
        data = response.json()
        
        # Should return status
        assert "connected" in data, "Response missing 'connected' field"
        
        print(f"Sliver reconnect result: connected={data['connected']}")


class TestC2ReconnectAndDashboard:
    """Test C2 unified reconnect and dashboard - Issues #1 and #2"""
    
    def test_c2_reconnect_both_services(self):
        """POST /api/c2/reconnect should reconnect both MSF and Sliver"""
        response = requests.post(f"{BASE_URL}/api/c2/reconnect")
        assert response.status_code == 200
        data = response.json()
        
        # Should have both metasploit and sliver status
        assert "metasploit" in data, "Response missing 'metasploit' field"
        assert "sliver" in data, "Response missing 'sliver' field"
        
        # Both should have connected field
        assert "connected" in data["metasploit"], "metasploit missing 'connected'"
        assert "connected" in data["sliver"], "sliver missing 'connected'"
        
        # Both should have diagnostics
        assert "diagnostics" in data["metasploit"], "metasploit missing 'diagnostics'"
        assert "diagnostics" in data["sliver"], "sliver missing 'diagnostics'"
        
        print(f"C2 Reconnect: MSF={data['metasploit']['connected']}, Sliver={data['sliver']['connected']}")
    
    def test_c2_dashboard_returns_both_services_with_diagnostics(self):
        """GET /api/c2/dashboard should return both MSF and Sliver with diagnostics"""
        response = requests.get(f"{BASE_URL}/api/c2/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Should have both services
        assert "metasploit" in data, "Dashboard missing 'metasploit'"
        assert "sliver" in data, "Dashboard missing 'sliver'"
        
        # MSF should have diagnostics
        msf = data["metasploit"]
        assert "diagnostics" in msf, "metasploit missing 'diagnostics'"
        assert "session_count" in msf, "metasploit missing 'session_count'"
        assert "job_count" in msf, "metasploit missing 'job_count'"
        
        # Sliver should have diagnostics
        sliver = data["sliver"]
        assert "diagnostics" in sliver, "sliver missing 'diagnostics'"
        assert "session_count" in sliver, "sliver missing 'session_count'"
        assert "beacon_count" in sliver, "sliver missing 'beacon_count'"
        
        print(f"C2 Dashboard: MSF sessions={msf['session_count']}, Sliver sessions={sliver['session_count']}")


class TestAttackTreeNodesFormat:
    """Test attack tree nodes format - Issue #3"""
    
    def test_scan_returns_attack_tree_with_nodes_as_dict(self):
        """POST /api/scan/start -> GET /api/scan/{id}/status should return attack_tree with nodes as dict"""
        # Start a scan
        scan_data = {
            "target": "192.168.1.1",
            "scan_phases": ["reconnaissance"],
            "tools": []
        }
        start_response = requests.post(f"{BASE_URL}/api/scan/start", json=scan_data)
        assert start_response.status_code == 200
        scan_id = start_response.json().get("scan_id")
        assert scan_id, "No scan_id returned"
        
        print(f"Started scan: {scan_id}")
        
        # Poll for completion (max 15 seconds)
        max_wait = 15
        start_time = time.time()
        status_data = None
        
        while time.time() - start_time < max_wait:
            status_response = requests.get(f"{BASE_URL}/api/scan/{scan_id}/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            if status_data.get("status") == "completed":
                break
            
            time.sleep(1)
        
        assert status_data.get("status") == "completed", f"Scan did not complete in {max_wait}s, status: {status_data.get('status')}"
        
        # Check attack_tree structure
        attack_tree = status_data.get("attack_tree")
        assert attack_tree is not None, "No attack_tree in response"
        
        # nodes should be a dict (not array)
        nodes = attack_tree.get("nodes")
        assert nodes is not None, "attack_tree missing 'nodes'"
        assert isinstance(nodes, dict), f"nodes should be dict, got {type(nodes).__name__}"
        
        print(f"Attack tree nodes type: {type(nodes).__name__}, count: {len(nodes)}")
        
        # Verify node structure
        for node_id, node in nodes.items():
            assert "id" in node, f"Node {node_id} missing 'id'"
            assert "type" in node, f"Node {node_id} missing 'type'"
            assert "name" in node, f"Node {node_id} missing 'name'"
            assert "status" in node, f"Node {node_id} missing 'status'"
        
        print(f"Scan completed with {len(nodes)} nodes in attack tree")


class TestScanCompletion:
    """Test scan completion timing"""
    
    def test_scan_completes_within_timeout(self):
        """Scan should complete with status=completed after ~8 seconds"""
        scan_data = {
            "target": "10.0.0.1",
            "scan_phases": ["reconnaissance"],
            "tools": []
        }
        start_response = requests.post(f"{BASE_URL}/api/scan/start", json=scan_data)
        assert start_response.status_code == 200
        scan_id = start_response.json().get("scan_id")
        
        # Wait for completion
        max_wait = 12
        start_time = time.time()
        final_status = None
        
        while time.time() - start_time < max_wait:
            status_response = requests.get(f"{BASE_URL}/api/scan/{scan_id}/status")
            final_status = status_response.json()
            
            if final_status.get("status") == "completed":
                elapsed = time.time() - start_time
                print(f"Scan completed in {elapsed:.1f}s")
                break
            
            time.sleep(1)
        
        assert final_status.get("status") == "completed", f"Scan did not complete, status: {final_status.get('status')}"


class TestAllNavigationEndpoints:
    """Test that all navigation-related endpoints work"""
    
    def test_mitre_tactics_endpoint(self):
        """GET /api/mitre/tactics should return tactics"""
        response = requests.get(f"{BASE_URL}/api/mitre/tactics")
        assert response.status_code == 200
        data = response.json()
        assert "tactics" in data
        print(f"MITRE tactics count: {len(data['tactics'])}")
    
    def test_chains_endpoint(self):
        """GET /api/chains should return attack chains"""
        response = requests.get(f"{BASE_URL}/api/chains")
        assert response.status_code == 200
        data = response.json()
        assert "chains" in data
        print(f"Attack chains count: {len(data['chains'])}")
    
    def test_metasploit_modules_endpoint(self):
        """GET /api/metasploit/modules should return modules"""
        response = requests.get(f"{BASE_URL}/api/metasploit/modules")
        assert response.status_code == 200
        data = response.json()
        assert "modules" in data
        print(f"MSF modules count: {len(data['modules'])}")
    
    def test_scan_history_endpoint(self):
        """GET /api/scan/history should return history"""
        response = requests.get(f"{BASE_URL}/api/scan/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Scan history count: {len(data)}")
    
    def test_config_endpoint(self):
        """GET /api/config should return config"""
        response = requests.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "listener_ip" in data
        assert "listener_port" in data
        print(f"Config: LHOST={data.get('listener_ip')}, LPORT={data.get('listener_port')}")
    
    def test_payloads_templates_endpoint(self):
        """GET /api/payloads/templates should return templates"""
        response = requests.get(f"{BASE_URL}/api/payloads/templates")
        assert response.status_code == 200
        data = response.json()
        assert "payloads" in data
        print(f"Payload templates count: {len(data['payloads'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
