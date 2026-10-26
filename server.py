from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Global database to store host sessions
# Format: { "user_id": { "username": str, "place_id": int, "job_id": str, "pos": list, "last_seen": float } }
active_hosts = {}

CLEANUP_TIMEOUT = 10  # Remove hosts if they haven't updated in 10 seconds

def cleanup_hosts():
    """Removes dead hosts who stopped sending updates."""
    now = time.time()
    dead_hosts = [uid for uid, data in active_hosts.items() if now - data['last_seen'] > CLEANUP_TIMEOUT]
    for uid in dead_hosts:
        del active_hosts[uid]

@app.route('/host', methods=['POST'])
def host_heartbeat():
    cleanup_hosts()
    data = request.json
    user_id = str(data.get('userId'))
    
    active_hosts[user_id] = {
        "username": data.get('username'),
        "place_id": data.get('placeId'),
        "job_id": data.get('jobId'),
        "pos": data.get('pos', [0, 0, 0]),
        "last_seen": time.time()
    }
    return jsonify({"status": "success", "total_hosts": len(active_hosts)})

@app.route('/get_hosts', methods=['GET'])
def get_hosts():
    cleanup_hosts()
    # Strip the internal 'last_seen' timestamp before returning to client
    public_data = {uid: {k: v for k, v in d.items() if k != 'last_seen'} for uid, d in active_hosts.items()}
    return jsonify(public_data)

if __name__ == '__main__':
    # Runs on http://127.0.0.1:5000
    app.run(host='0.0.0.0', port=5000)
