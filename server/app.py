from flask import Flask, jsonify, request, render_template_string
from flask_socketio import SocketIO, emit
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  
socketio = SocketIO(app, cors_allowed_origins="*")

# Variable to store the latest transcript
latest_transcript = ""

# HTML template with SocketIO client
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Transcript</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.4.1/socket.io.min.js"
            integrity="sha512-YqQ6oV6lFkjNz9BR6vSUIeMKv+jh6ePu4joaZK8+GaqV3FTgIo+UuhD6rwO6O6aTmghJxDg5nzB5d0CN8rQQVQ=="
            crossorigin="anonymous" referrerpolicy="no-referrer"></script>
</head>
<body>
    <h1>Live Transcript</h1>
    <p id="transcript">{{ transcript }}</p>

    <script type="text/javascript">
        var socket = io();

        socket.on('new_transcript', function(data) {
            document.getElementById('transcript').innerText = data.transcript;
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, transcript=latest_transcript)

@app.route('/transcript', methods=['POST'])
def receive_transcript():
    global latest_transcript
    try:
        # force=True to parse even if 'Content-Type' is incorrect
        data = request.get_json(force=True)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {'status': 'error', 'message': 'Invalid JSON'}, 400

    if not data or 'transcript' not in data:
        print("No 'transcript' field in the request.")
        return {'status': 'error', 'message': 'No transcript provided'}, 400

    latest_transcript = data['transcript']
    print(f"Received transcript: {latest_transcript}")  # Server-side logging

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
