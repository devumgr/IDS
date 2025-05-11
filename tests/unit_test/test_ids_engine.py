import pytest
from unittest.mock import patch
from main import MainIDS

@pytest.fixture
def main_ids():
    return MainIDS()

def test_process_packet_triggers_alert(main_ids):
    test_packet = {
        'protocol': 'tcp',
        'dst_port': 80,
        'payload': 'DROP TABLE users',
        'src_ip': '192.168.1.5',
        'dst_ip': '192.168.1.10',
        'timestamp': '2025-05-10T12:00:00'
    }

    with patch.object(main_ids.signature_detector, 'analyze', return_value=[{
        'description': 'SQL Injection attempt',
        'severity': 'high',
        'timestamp': '2025-05-10T12:00:00'
    }]):
        main_ids.process_packet(test_packet)
        assert len(main_ids.packet_buffer) == 1