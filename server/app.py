from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO
import logging

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize a global list to store transcripts
transcripts = []

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define your HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Transcripts</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .transcript { padding: 10px; border-bottom: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>Received Transcripts</h1>
</body>
</html>
"""


@app.route('/')
def index():
    # Pass the list of transcripts to the template
    logging.debug("Rendering index page with transcripts.")
    return render_template_string(HTML_TEMPLATE)


@app.route('/transcript', methods=['POST'])
def receive_transcript():
    global latest_transcript

    try:
        data = request.get_json(force=True)
    except Exception as e:
        logging.error(f"Error parsing JSON: {e}")
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    if not data or 'transcript' not in data:
        logging.warning("No 'transcript' field in the request.")
        return jsonify({'status': 'error', 'message': 'No transcript provided'}), 400

    # Parse for transcript
    latest_transcript = data['transcript'].strip()
    if latest_transcript:
        logging.info(f"Received transcript: {latest_transcript}")
    else:
        logging.warning("Received an empty transcript. Ignoring.")

    # Return a success response
    return jsonify({'status': 'success', 'message': 'Transcript received.'}), 200


if __name__ == '__main__':
    logging.info("Starting Flask application with SocketIO.")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
