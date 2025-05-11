import pytest
import json
from utils.packet_capture import PacketCapture

@pytest.fixture
def packet_capture():
    return PacketCapture(interface="test0", log_file="logs/test_packet_log.json")

def test_log_to_file_creates_file(tmp_path, packet_capture):
    test_data = {'src_ip': '1.1.1.1', 'dst_ip': '2.2.2.2', 'protocol': 'TCP', 'timestamp': '2025-01-01'}
    test_log_path = tmp_path / "test_packet_log.json"
    packet_capture.log_file = str(test_log_path)
    packet_capture.log_to_file(test_data)

    with open(test_log_path, 'r') as f:
        content = f.read()
        assert '1.1.1.1' in content