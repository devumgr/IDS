import pytest
from unittest.mock import patch
from utils.packet_capture import PacketCapture

def test_start_calls_sniff_with_correct_args():
    pc = PacketCapture(interface="test0")
    with patch("scapy.all.sniff") as mock_sniff:
        pc.start(filter="tcp")
        mock_sniff.assert_called_once()
        args = mock_sniff.call_args[1]
        assert args['iface'] == "test0"
        assert args['filter'] == "tcp"
        assert callable(args['prn'])