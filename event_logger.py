import json
import os
from datetime import datetime

EVENT_LOG_FILE = 'logs/event_log.json'

# Ensure log directory exists
os.makedirs(os.path.dirname(EVENT_LOG_FILE), exist_ok=True)

def write_event_log(message, level='INFO'):
    """Append an event to the IDS event log."""
    event = {
        'timestamp': datetime.now().isoformat(),
        'level': level.upper(),
        'message': message
    }

    logs = []
    if os.path.exists(EVENT_LOG_FILE):
        try:
            with open(EVENT_LOG_FILE, 'r') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []

    logs.append(event)

    # Keep only the last 100 logs
    logs = logs[-100:]

    with open(EVENT_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

    print(f"[{event['level']}] {event['timestamp']} - {message}")


def read_event_logs(limit=20):
    """Return the latest N event logs."""
    if not os.path.exists(EVENT_LOG_FILE):
        return []
    try:
        with open(EVENT_LOG_FILE, 'r') as f:
            logs = json.load(f)
            return logs[-limit:]
    except json.JSONDecodeError:
        return []

# Example Usage
if __name__ == "__main__":
    write_event_log("IDS service started", "INFO")
    write_event_log("Configuration file reloaded", "INFO")
    write_event_log("High packet drop rate detected", "WARNING")
    write_event_log("Packet capture started on eth0", "DEBUG")
    write_event_log("Unauthorized access attempt detected", "ERROR")

    # Print last 5 logs
    recent = read_event_logs(5)
    for log in recent:
        print(f"[{log['level']}] {log['timestamp']}: {log['message']}")
