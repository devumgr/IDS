import re 
class SnortRuleParser:
    def __init__(self, rule_file):
        self.rule_file = rule_file

    def parse_rules(self):
        rules = []
        with open(self.rule_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                rule = self.parse_snort_rule(line)
                if rule:
                    rules.append(rule)
        return rules

    def parse_snort_rule(self, line):
        try:
            if "(" not in line or ")" not in line:
                print(f"[!] Malformed rule: {line}")
                return None

            header, options_str = line.split("(", 1)
            options_str = options_str.rstrip(")")
            options = self._parse_options(options_str)

            parts = header.strip().split()
            if len(parts) < 7:
                print(f"[!] Incomplete rule header: {line}")
                return None

            protocol = parts[1]
            dst_port = parts[6]

            pattern = options.get("content")
            if pattern:
                pattern = self.parse_snort_content(pattern)

            return {
                "id": int(options.get("sid", 0)),
                "description": options.get("msg", ""),
                "severity": "high",
                "protocol": protocol,
                "dst_port": int(dst_port) if dst_port.isdigit() else None,
                "type": "regex",
                "pattern": pattern
            }
        except Exception as e:
            print(f"Failed to parse rule: {line}\nError: {e}")
            return None

    def _parse_options(self, options_str):
        options = {}
        for part in options_str.split(";"):
            part = part.strip()
            if not part or ":" not in part:
                continue
            key, value = part.split(":", 1)
            options[key.strip()] = value.strip().strip('"')
        return options

    def parse_snort_content(self, content):
        result = ""
        parts = re.split(r'(\|[^\|]*\|)', content)
        for part in parts:
            if part.startswith("|") and part.endswith("|"):
                hex_bytes = part.strip("|").split()
                for byte in hex_bytes:
                    if byte:
                        result += f"\\x{byte.lower()}"
            else:
                result += re.escape(part)
        return result
