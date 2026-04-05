"""
Test Payload Generator and LHOST Injection
==========================================
Tests for:
1. GET /api/payloads/templates - 11 payloads with global_lhost
2. POST /api/payloads/generate - LHOST injection in all payload types
3. GET/PUT /api/config - Global config persistence
4. POST /api/chains/*/generate - LHOST injection in chain commands
5. POST /api/metasploit/execute - LHOST in RC files
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test LHOST/LPORT values
TEST_LHOST = "10.10.14.99"
TEST_LPORT = 5555


class TestGlobalConfig:
    """Test global config endpoints"""
    
    def test_get_config(self):
        """GET /api/config returns listener_ip and listener_port"""
        response = requests.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "listener_ip" in data, "Missing listener_ip in config"
        assert "listener_port" in data, "Missing listener_port in config"
        print(f"✓ Config: listener_ip={data.get('listener_ip')}, listener_port={data.get('listener_port')}")
    
    def test_update_config_persists(self):
        """PUT /api/config updates and persists config"""
        # Set config
        payload = {
            "listener_ip": TEST_LHOST,
            "listener_port": TEST_LPORT,
            "c2_protocol": "tcp",
            "operator_name": "test_operator",
            "auto_lhost": True
        }
        response = requests.put(f"{BASE_URL}/api/config", json=payload)
        assert response.status_code == 200, f"PUT failed: {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "updated", "Config not updated"
        assert data.get("config", {}).get("listener_ip") == TEST_LHOST, "LHOST not set"
        assert data.get("config", {}).get("listener_port") == TEST_LPORT, "LPORT not set"
        
        # Verify persistence by re-fetching
        verify_response = requests.get(f"{BASE_URL}/api/config")
        verify_data = verify_response.json()
        assert verify_data.get("listener_ip") == TEST_LHOST, "LHOST not persisted"
        assert verify_data.get("listener_port") == TEST_LPORT, "LPORT not persisted"
        print(f"✓ Config persisted: {TEST_LHOST}:{TEST_LPORT}")


class TestPayloadTemplates:
    """Test payload templates endpoint"""
    
    def test_get_payload_templates_returns_11(self):
        """GET /api/payloads/templates returns 11 payloads"""
        # First ensure config is set
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.get(f"{BASE_URL}/api/payloads/templates")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        payloads = data.get("payloads", [])
        assert len(payloads) == 11, f"Expected 11 payloads, got {len(payloads)}"
        
        # Verify global_lhost and global_lport
        assert data.get("global_lhost") == TEST_LHOST, f"global_lhost mismatch: {data.get('global_lhost')}"
        assert data.get("global_lport") == str(TEST_LPORT), f"global_lport mismatch: {data.get('global_lport')}"
        
        print(f"✓ Got {len(payloads)} payload templates with global_lhost={data.get('global_lhost')}")
        
        # List all payload IDs
        for p in payloads:
            print(f"  - {p.get('id')}: {p.get('name')} ({p.get('type')})")
    
    def test_payload_templates_have_lhost_in_commands(self):
        """All payload templates have LHOST injected in generator_cmd and handler_cmd"""
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.get(f"{BASE_URL}/api/payloads/templates")
        data = response.json()
        payloads = data.get("payloads", [])
        
        for p in payloads:
            pid = p.get("id")
            gen_cmd = p.get("generator_cmd", "")
            handler_cmd = p.get("handler_cmd", "")
            
            # Check LHOST in generator_cmd
            assert TEST_LHOST in gen_cmd, f"LHOST not in generator_cmd for {pid}: {gen_cmd}"
            
            # Check LHOST in handler_cmd (except for sliver which uses different format)
            if "sliver" not in pid:
                assert TEST_LHOST in handler_cmd or str(TEST_LPORT) in handler_cmd, f"LHOST/LPORT not in handler_cmd for {pid}: {handler_cmd}"
            
            print(f"✓ {pid}: LHOST={TEST_LHOST} injected")


class TestPayloadGeneration:
    """Test payload generation with LHOST injection"""
    
    def test_generate_bash_reverse_has_lhost(self):
        """POST /api/payloads/generate with bash_reverse returns payload_content with LHOST"""
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.post(f"{BASE_URL}/api/payloads/generate", json={"payload_id": "bash_reverse"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("lhost") == TEST_LHOST, f"LHOST mismatch: {data.get('lhost')}"
        assert data.get("lport") == str(TEST_LPORT), f"LPORT mismatch: {data.get('lport')}"
        
        # For oneliners, payload_content should contain LHOST
        payload_content = data.get("payload_content", "")
        assert TEST_LHOST in payload_content, f"LHOST not in payload_content: {payload_content}"
        assert str(TEST_LPORT) in payload_content, f"LPORT not in payload_content: {payload_content}"
        
        print(f"✓ bash_reverse payload_content: {payload_content[:80]}...")
    
    def test_generate_windows_meterpreter_has_lhost(self):
        """POST /api/payloads/generate with windows/meterpreter/reverse_tcp returns generator_cmd with LHOST"""
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.post(f"{BASE_URL}/api/payloads/generate", json={"payload_id": "windows/meterpreter/reverse_tcp"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("lhost") == TEST_LHOST, f"LHOST mismatch: {data.get('lhost')}"
        
        generator_cmd = data.get("generator_cmd", "")
        assert f"LHOST={TEST_LHOST}" in generator_cmd, f"LHOST not in generator_cmd: {generator_cmd}"
        assert f"LPORT={TEST_LPORT}" in generator_cmd, f"LPORT not in generator_cmd: {generator_cmd}"
        
        handler_cmd = data.get("handler_cmd", "")
        assert TEST_LHOST in handler_cmd, f"LHOST not in handler_cmd: {handler_cmd}"
        
        print(f"✓ windows/meterpreter/reverse_tcp generator_cmd: {generator_cmd[:80]}...")
    
    def test_generate_powershell_reverse_has_lhost(self):
        """POST /api/payloads/generate with powershell_reverse returns payload_content with LHOST"""
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.post(f"{BASE_URL}/api/payloads/generate", json={"payload_id": "powershell_reverse"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        payload_content = data.get("payload_content", "")
        assert TEST_LHOST in payload_content, f"LHOST not in payload_content: {payload_content[:100]}"
        
        print(f"✓ powershell_reverse has LHOST={TEST_LHOST}")
    
    def test_generate_sliver_session_has_mtls_lhost(self):
        """POST /api/payloads/generate with sliver_session returns generator_cmd with mtls lhost"""
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.post(f"{BASE_URL}/api/payloads/generate", json={"payload_id": "sliver_session"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        generator_cmd = data.get("generator_cmd", "")
        # Sliver uses --mtls {lhost}:{lport} format
        assert TEST_LHOST in generator_cmd, f"LHOST not in sliver generator_cmd: {generator_cmd}"
        assert "mtls" in generator_cmd.lower(), f"mtls not in sliver generator_cmd: {generator_cmd}"
        
        print(f"✓ sliver_session generator_cmd: {generator_cmd[:80]}...")
    
    def test_generate_without_lhost_returns_400(self):
        """POST /api/payloads/generate without LHOST configured returns 400 error"""
        # Clear LHOST
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": "", "listener_port": TEST_LPORT})
        
        response = requests.post(f"{BASE_URL}/api/payloads/generate", json={"payload_id": "bash_reverse"})
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "LHOST" in data.get("detail", ""), f"Error should mention LHOST: {data}"
        
        print(f"✓ Generate without LHOST returns 400: {data.get('detail')}")
        
        # Restore LHOST for other tests
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})


class TestChainLhostInjection:
    """Test LHOST injection in attack chains"""
    
    def test_chain_generate_injects_lhost(self):
        """POST /api/chains/web_to_shell/generate injects LHOST from global config"""
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.post(
            f"{BASE_URL}/api/chains/web_to_shell/generate",
            json={"target": "192.168.1.100", "domain": "test.local"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        commands = data.get("commands", [])
        assert len(commands) > 0, "No commands generated"
        
        # Check that LHOST is injected in persistence step (step 4)
        found_lhost = False
        for step in commands:
            for cmd in step.get("commands", []):
                cmd_text = cmd.get("command", "")
                if TEST_LHOST in cmd_text:
                    found_lhost = True
                    print(f"✓ Found LHOST in step {step.get('step_id')}: {cmd_text[:80]}...")
        
        assert found_lhost, f"LHOST {TEST_LHOST} not found in any chain commands"
    
    def test_chain_execute_injects_lhost(self):
        """POST /api/chains/execute for phishing_to_shell injects LHOST from global config"""
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.post(
            f"{BASE_URL}/api/chains/execute",
            json={
                "scan_id": "test_scan_123",
                "chain_id": "phishing_to_shell",
                "target": "192.168.1.100",
                "context": {},
                "auto_execute": False
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        commands = data.get("commands", [])
        
        # Check LHOST in commands
        found_lhost = False
        for step in commands:
            for cmd in step.get("commands", []):
                cmd_text = cmd.get("command", "")
                if TEST_LHOST in cmd_text:
                    found_lhost = True
                    print(f"✓ Found LHOST in phishing_to_shell step {step.get('step_id')}: {cmd_text[:80]}...")
        
        assert found_lhost, f"LHOST {TEST_LHOST} not found in phishing_to_shell chain commands"


class TestMetasploitLhostInjection:
    """Test LHOST injection in Metasploit execution"""
    
    def test_msf_execute_rc_contains_lhost(self):
        """POST /api/metasploit/execute rc_command contains set LHOST with global config IP"""
        requests.put(f"{BASE_URL}/api/config", json={"listener_ip": TEST_LHOST, "listener_port": TEST_LPORT})
        
        response = requests.post(
            f"{BASE_URL}/api/metasploit/execute",
            json={
                "scan_id": "test_scan_123",
                "node_id": "test_node",
                "module": "exploit/windows/smb/ms17_010_eternalblue",
                "target_host": "192.168.1.100",
                "target_port": 445,
                "options": {},
                "lhost": None,  # Should use global config
                "lport": None   # Should use global config
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        rc_command = data.get("rc_command", "")
        
        # Check LHOST in RC command
        assert f"set LHOST {TEST_LHOST}" in rc_command, f"LHOST not in rc_command: {rc_command}"
        assert f"set LPORT {TEST_LPORT}" in rc_command, f"LPORT not in rc_command: {rc_command}"
        
        print(f"✓ MSF rc_command contains LHOST: {rc_command[:100]}...")
        
        # Verify simulated flag (msfconsole not available in preview)
        if data.get("simulated"):
            print("  (simulated=true - msfconsole not available in preview)")


class TestScanFlow:
    """Test scan start and status"""
    
    def test_scan_start_returns_scan_id(self):
        """POST /api/scan/start starts scan and returns scan_id"""
        response = requests.post(
            f"{BASE_URL}/api/scan/start",
            json={"target": "192.168.1.100", "scan_phases": ["reconnaissance"]}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "scan_id" in data, "Missing scan_id"
        assert data.get("status") == "started", f"Status not started: {data.get('status')}"
        
        print(f"✓ Scan started: {data.get('scan_id')}")
        return data.get("scan_id")
    
    def test_scan_status_completes(self):
        """GET /api/scan/{id}/status returns completed status after ~8 seconds"""
        # Start scan
        start_response = requests.post(
            f"{BASE_URL}/api/scan/start",
            json={"target": "192.168.1.100", "scan_phases": ["reconnaissance"]}
        )
        scan_id = start_response.json().get("scan_id")
        
        # Poll for completion
        max_wait = 15
        completed = False
        for i in range(max_wait):
            status_response = requests.get(f"{BASE_URL}/api/scan/{scan_id}/status")
            status_data = status_response.json()
            
            if status_data.get("status") == "completed":
                completed = True
                print(f"✓ Scan completed in {i+1} seconds")
                break
            
            time.sleep(1)
        
        assert completed, f"Scan did not complete within {max_wait} seconds"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
