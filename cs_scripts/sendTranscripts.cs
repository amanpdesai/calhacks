using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class TranscriptSender : MonoBehaviour
{
    [Tooltip("URL of the Flask server endpoint to receive transcripts.")]
    public string flaskServerURL = "http://127.0.0.1:5001/transcript";

    // private void Awake()
    // {
        // Start the coroutine to send "hello" on Awake
        // StartCoroutine(SendTranscript("hello"));
    // }

    /// <summary>
    /// Coroutine to send a transcript to the Flask server.
    /// </summary>
    /// <param name="transcript">The transcript to send.</param>
    /// <returns></returns>
    private IEnumerator SendTranscript(string transcript)
    {
        // Create a JSON payload
        string jsonData = JsonUtility.ToJson(new TranscriptPayload { transcript = transcript });

        // Convert the JSON string to a byte array
        byte[] jsonToSend = new System.Text.UTF8Encoding().GetBytes(jsonData);

        // Create a new UnityWebRequest for POST
        UnityWebRequest request = new UnityWebRequest(flaskServerURL, "POST");
        request.uploadHandler = new UploadHandlerRaw(jsonToSend);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        // Send the request and wait for a response
        yield return request.SendWebRequest();

        // Check for errors
        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            Debug.LogError($"Error sending transcript: {request.error}");
        }
        else
        {
            Debug.Log("Transcript sent successfully.");
        }
    }

    /// <summary>
    /// Class to structure the JSON payload.
    /// </summary>
    [System.Serializable]
    private class TranscriptPayload
    {
        public string transcript;
    }
}
