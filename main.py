from utils.packet_capture import PacketCapture
from detectors.signature_based import SignatureDetector
from collections import deque
from event_logger import write_event_log
import time
import threading

class MainIDS:
    def __init__(self):
        self.sniffer = PacketCapture(interface="Wi-Fi")
        self.signature_detector = SignatureDetector(rule_file="rules/snort.rules")
        self.packet_buffer = deque(maxlen=1000)
        self.worker_thread = threading.Thread(target=self._process_loop, daemon=True)

    def process_packet(self, packet):
        alerts = self.signature_detector.analyze(packet)
        if alerts:
            for alert in alerts:
                print(f"Alert: {alert['description']} | Severity: {alert['severity']} | Timestamp: {alert['timestamp']}")
                self.packet_buffer.append(packet)
                self.sniffer.log_to_file(packet)
                
    def run(self):
        print("IDS is running ")
        self.running = True
        write_event_log("IDS has started.", level="INFO")
        try:
            # Start the packet sniffer in its own thread if needed
            self.sniffer.start(filter="ip")
            self.worker_thread.start()
        except KeyboardInterrupt:
            self.stop()

    def _process_loop(self):
        while self.running:
            try:
                if self.sniffer.buffer:
                    packet = self.sniffer.buffer.popleft()
                    try:
                        self.process_packet(packet)
                    except Exception as e:
                        print(f"[!] Error processing packet: {e}")
                else:
                    time.sleep(0.01)
            except Exception as e:
                print(f"[!] Loop error: {e}")
    def stop(self):
        self.running = False
        print("IDS have been stopped.")
        write_event_log("IDS has stopped.", level="INFO")

if __name__ == '__main__':
    # Initialize and run the IDS
    main = MainIDS()
    main.run()