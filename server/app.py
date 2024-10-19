from flask import Flask, jsonify, request, render_template, Response, send_file
import cv2
import numpy as np
import io

app = Flask(__name__)
camera = cv2.VideoCapture(0)

latest_frame = None

def generate_frames():
    global latest_frame
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            latest_frame = frame.copy()
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
    global latest_frame
    if latest_frame is None:
        return "No frame available", 404

    # Encode the latest frame as a JPEG image
    ret, jpeg = cv2.imencode('.jpg', latest_frame)
    if not ret:
        return "Failed to encode frame", 500

    # Convert the JPEG image to bytes
    image_bytes = jpeg.tobytes()
    # Create an in-memory bytes buffer
    buffer = io.BytesIO(image_bytes)

    # Send the image as a downloadable file
    buffer.seek(0)
    return send_file(buffer, mimetype='image/jpeg', as_attachment=True, download_name='frame.jpg')

if __name__ == "__main__":
    app.run()