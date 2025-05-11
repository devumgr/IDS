import time
import os
import json
from scapy.all import sniff, IP, TCP, get_if_list, UDP, ICMP # Importing necessary modules from scapy library
from collections import deque


class PacketCapture:
    def __init__ (self, interface="Wi-Fi", buffer_size=1000, log_file="logs/packet_log.json"):
        self.interface = interface
        self.buffer = deque(maxlen=buffer_size)
        self.running = False
        self.log_file = log_file
    
    def _packet_handler(self, packet):
        parsed = self.parse_packet(packet)
        if parsed:
            self.buffer.append(parsed)
            self.log_to_file(parsed)
            return parsed
    
    def parse_packet(self, packet):
        if not packet.haslayer(IP):
            return None

        layers = []
        current_layer = packet
        while current_layer:
            layers.append(current_layer.name)
            current_layer = current_layer.payload

        return {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(packet.time)),
            'src_ip': packet[IP].src,
            'dst_ip': packet[IP].dst,
            'protocol': layers[1] if len(layers) > 1 else 'N/A',
            'src_port': packet.sport if hasattr(packet, 'sport') else None,
            'dst_port': packet.dport if hasattr(packet, 'dport') else None,
            'length': len(packet),
            'flags': self._get_flags(packet),
            'payload': str(packet.payload) if hasattr(packet, 'payload') else None
        }
    
    def _get_flags(self, packet):

        if packet.haslayer(TCP):
            return {
                'SYN': packet[TCP].flags.S,
                'ACK': packet[TCP].flags.A,
                'FIN': packet[TCP].flags.F,
                'RST': packet[TCP].flags.R,
                'URG': packet[TCP].flags.U,
                'PSH': packet[TCP].flags.P
            }
        return {}
    
    def log_to_file(self, data):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r+') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
                existing_data.append(data)
                f.seek(0)
                json.dump(existing_data, f, indent=4)
        else:
            with open(self.log_file, 'w') as f:
                json.dump([data], f, indent=4)	

    def start(self, filter=None):
        self.running = True
        sniff(iface=self.interface,
              prn=self._packet_handler,
              filter=filter)
        
    def stop(self):
        self.running = False