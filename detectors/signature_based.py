import re
import os
import json
from datetime import datetime
from detectors.snort_rule_parser import SnortRuleParser

class SignatureDetector:
    def __init__(self, rule_file="rules/snort.rules"):
        parser = SnortRuleParser(rule_file)
        raw_rules = parser.parse_rules()
        self.compiled_rules = self.compile_rules(raw_rules)

    def compile_rules(self, rules):
        compiled_rules = []
        for rule in rules:
            try:
                compiled_rules.append({
                    'id': rule['id'],
                    'description': rule.get('description', ''),
                    'severity': rule.get('severity', 'low'),
                    'protocol': rule.get('protocol', '').lower(),
                    'dst_port': int(rule['dst_port']) if rule.get('dst_port') else None,
                    'type': rule.get('type', 'regex'),
                    'pattern': re.compile(rule['pattern'], re.IGNORECASE) if rule.get('pattern') else None
                })
            except re.error as e:
                print(f"[!] Invalid regex in rule {rule.get('id')}: {e}")
        return compiled_rules

    def save_alert(self, alert, path='logs/alerts.json'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            with open(path, 'r+') as f:
                try:
                    alerts = json.load(f)
                except json.JSONDecodeError:
                    alerts = []
                alerts.append(alert)
                f.seek(0)
                json.dump(alerts, f, indent=4)
        else:
            with open(path, 'w') as f:
                json.dump([alert], f, indent=4)

    def analyze(self, packet):
        alerts = []
        for rule in self.compiled_rules:
            if self.match_rule(packet, rule):
                alert = {
                    'rule_id': rule['id'],
                    'description': rule['description'],
                    'severity': rule['severity'],
                    'timestamp': datetime.now().isoformat(),
                    'packet': packet
                }
                alerts.append(alert)
                self.save_alert(alert)
        return alerts

    def match_rule(self, packet, rule):
        if rule['protocol'] and packet.get('protocol', '').lower() != rule['protocol']:
            return False
        if rule['dst_port'] and packet.get('dst_port') != rule['dst_port']:
            return False
        if rule['type'] == 'regex' and rule.get('pattern') and packet.get('payload'):
            return bool(rule['pattern'].search(packet['payload']))
        return True

