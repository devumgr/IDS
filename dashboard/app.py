from flask import Flask, render_template, jsonify, request
import json
import psutil
import time
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Helper functions
def load_json_log(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def ensure_dir_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Routes
@app.route('/')
def dashboard():
    packets = load_json_log('logs/packet_log.json')[-100:]
    alerts = load_json_log('logs/alerts.json')[-20:]
    logs = load_json_log('logs/event_log.json')[-20:]
    signatures = load_json_log('logs/signatures.json')

    total_packets = len(packets)
    packets_per_sec = total_packets / 60  # Simulated packets per second
    data_transferred = sum(p.get('length', 0) for p in packets) // 1024

    # Get unique connections
    seen_connections = set()
    connections = []
    for p in packets:
        if p.get('protocol') in ['TCP', 'UDP']:
            conn_key = f"{p.get('src_ip')}:{p.get('dst_ip')}:{p.get('protocol')}:{p.get('dst_port')}"
            if conn_key not in seen_connections:
                connections.append({
                    'src_ip': p.get('src_ip'),
                    'dst_ip': p.get('dst_ip'),
                    'protocol': p.get('protocol'),
                    'dst_port': p.get('dst_port')
                })
                seen_connections.add(conn_key)

    # Format packet data for display
    formatted_packets = []
    for p in packets[:10]:  # Show only the first 10 packets
        formatted_packets.append(json.dumps(p, indent=2))

    # Format TCP flags
    tcp_flags = []
    for p in packets:
        if p.get('protocol') == 'TCP' and p.get('flags'):
            flags_str = f"SRC: {p.get('src_ip')}:{p.get('src_port')} → DST: {p.get('dst_ip')}:{p.get('dst_port')}\nFlags: {json.dumps(p.get('flags'))}"
            tcp_flags.append(flags_str)

    # Count alerts by severity
    high_count = sum(1 for a in alerts if a.get('severity') == 'high')
    medium_count = sum(1 for a in alerts if a.get('severity') == 'medium')
    low_count = sum(1 for a in alerts if a.get('severity') == 'low')

    return render_template('dashboard.html',
        total_packets=total_packets,
        packets_sec=round(packets_per_sec, 2),
        data_transferred=data_transferred,
        connections=connections,
        alerts=alerts,
        logs=logs,
        packets=formatted_packets,
        signatures=signatures,
        flags=tcp_flags[:10],  # Show only the first 10 TCP flags
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count
    )

@app.route('/api/system_stats')
def system_stats():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    return jsonify({
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/packet_stats')
def packet_stats():
    packets = load_json_log('logs/packet_log.json')
    
    # Generate time series data for the last hour
    now = datetime.now()
    time_bins = {}
    
    # Initialize time bins for the last hour in 5-minute intervals
    for i in range(12):
        time_key = (now - timedelta(minutes=5*i)).strftime('%H:%M')
        time_bins[time_key] = {
            'tcp': 0,
            'udp': 0,
            'icmp': 0,
            'other': 0
        }
    
    # Fill the bins with actual data
    for packet in packets:
        try:
            packet_time = datetime.fromisoformat(packet.get('timestamp'))
            if now - packet_time <= timedelta(hours=1):
                time_key = packet_time.strftime('%H:%M')
                protocol = packet.get('protocol', 'other').lower()
                
                if time_key in time_bins:
                    if protocol in time_bins[time_key]:
                        time_bins[time_key][protocol] += 1
                    else:
                        time_bins[time_key]['other'] += 1
        except (ValueError, TypeError):
            pass  # Skip packets with invalid timestamps
    
    # Format data for Chart.js
    labels = list(reversed(time_bins.keys()))
    datasets = [
        {
            'label': 'TCP',
            'data': [time_bins[key]['tcp'] for key in labels],
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        },
        {
            'label': 'UDP',
            'data': [time_bins[key]['udp'] for key in labels],
            'borderColor': 'rgb(255, 99, 132)',
            'tension': 0.1
        },
        {
            'label': 'ICMP',
            'data': [time_bins[key]['icmp'] for key in labels],
            'borderColor': 'rgb(255, 205, 86)',
            'tension': 0.1
        },
        {
            'label': 'Other',
            'data': [time_bins[key]['other'] for key in labels],
            'borderColor': 'rgb(201, 203, 207)',
            'tension': 0.1
        }
    ]
    
    return jsonify({
        'labels': labels,
        'datasets': datasets
    })

if __name__ == '__main__':
    app.run(debug=True)
