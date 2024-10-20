import http.client
import json
import os


def text_to_wav(given_text, output_dir="../../Assets/TextToSpeech/"):
    url = "api.deepgram.com"
    conn = http.client.HTTPSConnection(url)
    headers = {
        "Authorization": "Token 077b7002b19330ce99f96adf7134bf8c50896f78",
        "Content-Type": "application/json",
    }

    request_body = json.dumps({"text": given_text})
    conn.request(
        "POST", "/v1/speak?model=aura-luna-en&encoding=linear16", request_body, headers
    )
    response = conn.getresponse()

    # Count all files in the directory
    i = len(os.listdir(output_dir)) + 1
    file_path = f"tts_file_{i}.wav"

    with open(os.path.join(output_dir, file_path), "wb") as output_file:
        output_file.write(response.read())

    conn.close()
    print(f"File saved as {file_path}")
