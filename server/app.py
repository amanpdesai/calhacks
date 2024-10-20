from flask import Flask, jsonify, request, render_template, Response, send_file
import cv2
import numpy as np
import io
import pymysql
from image_description import generate_full_summary, checkai_instr_vs_summaries, serber
import requests

connection = pymysql.connect(
    host='svc-f90325a9-8b27-495d-a436-7cb5c7764c62-dml.aws-oregon-3.svc.singlestore.com',
    user='admin',
    password='Flj3M3k6N1of0CXLuR73YiPRMkf9JiTj',
    database='instructions',
    port=3306
)

app = Flask(__name__)
camera = cv2.VideoCapture(0)

step_tracker = 1
latest_transcript = ""

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

def generate_frames():
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/")
def test():
    return jsonify("Hola Mundo")

@app.route("/descriptions")
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:
        file.save('uploads/' + file.filename)
        return 'File uploaded successfully'

@app.route('/stream')
def stream():
    return render_template("./index.html")

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/grab-frame')
def grab_frame():
    url = serber + 'video'

    # Open the video stream using OpenCV
    cap = cv2.VideoCapture(url)

    # Check if the video capture was successful
    if not cap.isOpened():
        return "Unable to open video stream", 500

    # Read a single frame from the video stream
    ret, frame = cap.read()

    # Release the video capture object
    cap.release()

    if not ret or frame is None:
        return "No frame available", 404

    # Encode the frame as JPEG
    ret, jpeg = cv2.imencode('.jpg', frame)
    if not ret:
        return "Failed to encode frame", 500

    # Convert the JPEG image to bytes
    image_bytes = jpeg.tobytes()

    # Create an in-memory bytes buffer
    buffer = io.BytesIO(image_bytes)

    # Send the image as a downloadable file
    buffer.seek(0)
    return send_file(buffer, mimetype='image/jpeg', as_attachment=True, download_name='frame.jpg')

@app.route('/compare-input-vs-instr')
def compare():
    global step_tracker
    instruction = get_instruction(step_tracker)
    image_summary = generate_full_summary()
    audio_summary = latest_transcript
    push_latest_transcript_to_sql()
    resp = checkai_instr_vs_summaries(instruction, image_summary, audio_summary)
    chat_log = update_sql_base(audio_summary, resp)
    if resp.split('. ')[-1] == "Proceed.":
        step_tracker += 1
    return chat_log

def push_latest_transcript_to_sql():
    try:
        with connection.cursor() as cursor:
            
            # SQL query
            #query = f"INSERT INTO Step_{step_tracker} (ID,SPEAKER,MESSAGE) VALUES (%s, %s, %s);", (idx + 1, "User", user)
            
            # Execute the query
            cursor.execute(f"INSERT INTO Transcript (STEP,TEXT) VALUES (%s, %s);", (step_tracker, latest_transcript))

            connection.commit()

            return f"Step: {step_tracker}\nTranscript: {latest_transcript}"

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return f"Error: {e}"

def get_last_index(step_tracker):
    with connection.cursor() as cursor:
        search_query = f"SELECT MAX(id) AS highest_index FROM Step_{step_tracker}"
        cursor.execute(search_query)
        results = cursor.fetchall()
        return results[0][0]

def update_sql_base(user, chat):
    global step_tracker
    idx = get_last_index(step_tracker)
    try:
        with connection.cursor() as cursor:
            
            # SQL query
            #query = f"INSERT INTO Step_{step_tracker} (ID,SPEAKER,MESSAGE) VALUES (%s, %s, %s);", (idx + 1, "User", user)
            
            # Execute the query
            cursor.execute(f"INSERT INTO Step_{step_tracker} (ID,SPEAKER,MESSAGE) VALUES (%s, %s, %s);", (idx + 1, "User", user))
            cursor.execute(f"INSERT INTO Step_{step_tracker} (ID,SPEAKER,MESSAGE) VALUES (%s, %s, %s);", (idx + 2, "Judgement", chat))

            connection.commit()

            return f"Judgement: {chat}   \nUser: {user}"

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return f"Error: {e}"

def get_instruction(table_number):
    try:
        with connection.cursor() as cursor:
            
            # SQL query
            query = f"SELECT * FROM Step_{table_number} WHERE SPEAKER='Instruction';"
            
            # Execute the query
            cursor.execute(query)

            # Fetch the results
            results = cursor.fetchall()
            return results[0][2]

    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return f"Error: {e}"

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
    print(f"Received transcript: {latest_transcript}")

    return jsonify({'status': 'success'}), 200

if __name__ == "__main__":
    app.run()