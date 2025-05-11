import pytest
from unittest.mock import MagicMock
from utils.packet_capture import PacketCapture

@pytest.fixture
def packet_capture():
    return PacketCapture(interface="test0", log_file="logs/test_packet_log.json")

def test_parse_valid_packet(packet_capture):
    mock_packet = MagicMock()
    mock_packet.haslayer.side_effect = lambda x: x.__name__ == 'IP'
    mock_packet.time = 1680000000.0
    mock_packet.sport = 1234
    mock_packet.dport = 80
    mock_packet.__len__.return_value = 60
    mock_packet.payload.name = 'TCP'
    mock_packet.__getitem__.side_effect = lambda x: {
        'IP': MagicMock(src='192.168.1.2', dst='192.168.1.3'),
        'TCP': MagicMock(flags=MagicMock(S=1, A=1, F=0, R=0, U=0, P=0))
    }[x.__name__] if hasattr(x, '__name__') else None

    result = packet_capture.parse_packet(mock_packet)
    assert result is not None
    assert result['src_ip'] == '192.168.1.2'
    assert result['dst_port'] == 80