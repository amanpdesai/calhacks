// using System.Collections;
// using System.Collections.Generic;
// using System.IO;
// using UnityEngine;

// // for stt
// using UnityEngine.Networking;
// using Newtonsoft.Json.Linq; // add to package manager
// using System;
// using System.Text;
// using System.Threading.Tasks;

// public class ContinuousRecord : MonoBehaviour
// {
//     private AudioClip recordedClip;
//     [SerializeField] AudioSource audioSource;
//     private string deepGramApiKey = "077b7002b19330ce99f96adf7134bf8c50896f78"; //not good practice ik

//     private string directoryPath = "/Users/aj/My project/Recordings";
//     private float startTime;
//     private float recordingLength;
//     private int sampleRate = 44100;
//     private int lengthSec = 10;
//     private bool isRecordingContinuous = false;
//     private Coroutine recordingCoroutine;
//     private int recordingCounter = 0;

//     // VAD Parameters
//     [Range(0f, 1f)]
//     public float silenceThreshold = 0.01f; // Adjust based on testing

//     [Tooltip("Duration (in seconds) of continuous silence to stop recording.")]
//     public float silenceDurationLimit = 3f;

//     [Tooltip("Interval (in seconds) between silence checks.")]
//     public float silenceCheckInterval = 0.5f;


//     private void Awake()
//     {
//         // Use Application.persistentDataPath for platform-independent storage
//         // directoryPath = Path.Combine(Application.persistentDataPath, "Recordings");
//         Debug.Log($"Directory Path Set To: {directoryPath}");

//         if (!Directory.Exists(directoryPath))
//         {
//             Directory.CreateDirectory(directoryPath);
//             Debug.Log($"Created directory: {directoryPath}");
//         }
//         else
//         {
//             Debug.Log($"Directory already exists: {directoryPath}");
//         }

//         // Initialize recordingCounter based on existing files to prevent filename conflicts
//         var existingFiles = Directory.GetFiles(directoryPath, "recording_*.wav");
//         recordingCounter = existingFiles.Length;
//         Debug.Log($"Initial recordingCounter set to {recordingCounter}");
//     }

//     /// <summary>
//     /// Starts the continuous recording process.
//     /// </summary>
//     public void StartContinuousRecording()
//     {
//         if (Microphone.devices.Length == 0)
//         {
//             Debug.LogError("No microphone devices found.");
//             return;
//         }

//         if (!isRecordingContinuous)
//         {
//             isRecordingContinuous = true;
//             recordingCoroutine = StartCoroutine(RecordLoop());
//             Debug.Log("Started continuous recording.");
//         }
//         else
//         {
//             Debug.LogWarning("Continuous recording is already in progress.");
//         }
//     }

//     /// <summary>
//     /// Stops the continuous recording process.
//     /// </summary>
//     public void StopContinuousRecording()
//     {
//         if (isRecordingContinuous)
//         {
//             isRecordingContinuous = false;
//             if (recordingCoroutine != null)
//             {
//                 StopCoroutine(recordingCoroutine);
//                 recordingCoroutine = null;
//             }
//             Microphone.End(null);
//             Debug.Log("Stopped continuous recording.");
//         }
//         else
//         {
//             Debug.LogWarning("Continuous recording is not active.");
//         }
//     }

//     /// <summary>
//     /// Coroutine that handles the continuous recording loop.
//     /// </summary>
//     /// <returns></returns>
//     private IEnumerator RecordLoop()
//     {
//         string device = Microphone.devices[0];
//         Debug.Log($"Using microphone: {device}");

//         while (isRecordingContinuous)
//         {
//             // Start Recording
//             Debug.Log("Attempting to start recording...");
//             recordedClip = Microphone.Start(device, false, lengthSec, sampleRate);
//             if (recordedClip == null)
//             {
//                 Debug.LogError("Microphone.Start returned null. Recording failed to start.");
//                 yield break;
//             }
//             startTime = Time.realtimeSinceStartup;
//             Debug.Log("Recording started...");

//             // Wait for the duration of the recording
//             yield return new WaitForSeconds(lengthSec);

//             // Stop Recording
//             Microphone.End(null);
//             recordingLength = Time.realtimeSinceStartup - startTime;
//             Debug.Log($"Recording stopped. Duration: {recordingLength} seconds.");

//             recordedClip = TrimClip(recordedClip, recordingLength);

//             // Save the recording
//             // SaveRecording();
//             TranscribeRecording();
//         }

//         Debug.Log("Exited recording loop.");
//     }

//     /// <summary>
//     /// Saves the recorded AudioClip as a WAV file with a unique name.
//     /// </summary>
//     public void SaveRecording()
//     {
//         if (recordedClip != null)
//         {
//             // Generate a unique filename using a counter and timestamp
//             string timestamp = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");
//             string uniqueFileName = $"recording_{timestamp}_{recordingCounter}.wav";
//             string fullPath = Path.Combine(directoryPath, uniqueFileName);

//             Debug.Log($"Saving recording to: {fullPath}");

//             // Save the AudioClip as a WAV file
//             WavUtility.Save(fullPath, recordedClip);
//             Debug.Log($"Recording saved successfully as {uniqueFileName}");
//             recordingCounter++;
//         }
//         else
//         {
//             Debug.LogError("No recording found to save.");
//         }
//     }

//     /// <summary>
//     /// Trims the AudioClip to the specified length.
//     /// </summary>
//     /// <param name="clip">The original AudioClip.</param>
//     /// <param name="length">Desired length in seconds.</param>
//     /// <returns>Trimmed AudioClip.</returns>
//     private AudioClip TrimClip(AudioClip clip, float length)
//     {
//         if (clip == null || length <= 0)
//         {
//             Debug.LogError("TrimClip called with null AudioClip or non-positive length.");
//             return null;
//         }

//         int samples = Mathf.FloorToInt(clip.frequency * length);
//         samples = Mathf.Clamp(samples, 0, clip.samples);

//         if (samples <= 0)
//         {
//             Debug.LogError("Calculated sample count is non-positive.");
//             return null;
//         }

//         float[] data = new float[samples * clip.channels];
//         bool success = clip.GetData(data, 0);
//         if (!success)
//         {
//             Debug.LogError("Failed to get audio data from clip.");
//             return null;
//         }

//         AudioClip trimmedClip = AudioClip.Create(clip.name + "_trimmed", samples, clip.channels, clip.frequency, false);
//         trimmedClip.SetData(data, 0);

//         Debug.Log("AudioClip trimmed successfully.");

//         return trimmedClip;
//     }

//     public void TranscribeRecording()
//     {
//         if (recordedClip != null)
//         {
//             StartCoroutine(TranscribeAudio(recordedClip));
//         }
//         else
//         {
//             Debug.LogError("No recording found to transcribe.");
//         }
//     }


//     private IEnumerator TranscribeAudio(AudioClip clip)
//     {
//         if (clip == null)
//         {
//             Debug.LogError("TranscribeAudio called with null AudioClip.");
//             yield break;
//         }

//         if (string.IsNullOrEmpty(deepGramApiKey) || deepGramApiKey == "YOUR_DEEPGRAM_API_KEY")
//         {
//             Debug.LogError("DeepGram API Key is not set. Please set it in the Inspector.");
//             yield break;
//         }

//         // Convert AudioClip to WAV byte array
//         byte[] wavData = WavUtility.ToWavBytes(clip);
//         if (wavData == null || wavData.Length == 0)
//         {
//             Debug.LogError("Failed to convert AudioClip to WAV format.");
//             yield break;
//         }

//         // Prepare the DeepGram API endpoint with query parameters
//         string url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true";

//         // Create the UnityWebRequest
//         UnityWebRequest request = new UnityWebRequest(url, "POST");
//         request.uploadHandler = new UploadHandlerRaw(wavData);
//         request.downloadHandler = new DownloadHandlerBuffer();

//         // Set headers
//         request.SetRequestHeader("Authorization", $"Token {deepGramApiKey}");
//         request.SetRequestHeader("Content-Type", "audio/wav");

//         Debug.Log($"Sending transcription request to DeepGram: {url}");

//         // Send the request and wait for the response
//         yield return request.SendWebRequest();

//         // Handle the response
//         if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
//         {
//             Debug.LogError($"DeepGram transcription failed: {request.error}");
//         }
//         else
//         {
//             // Parse the JSON response
//             string jsonResponse = request.downloadHandler.text;
//             Debug.Log($"DeepGram Response: {jsonResponse}");

//             try
//             {
//                 JObject response = JObject.Parse(jsonResponse);
//                 string transcript = response["results"]?["channels"]?[0]?["alternatives"]?[0]?["transcript"]?.ToString();

//                 if (!string.IsNullOrEmpty(transcript))
//                 {
//                     Debug.Log($"Transcription: {transcript}");
//                     // TODO: Handle the transcription result as needed (e.g., display in UI, send to server)
//                 }
//                 else
//                 {
//                     Debug.LogWarning("Transcription result is empty.");
//                 }
//             }
//             catch (Exception e)
//             {
//                 Debug.LogError($"Failed to parse DeepGram response: {e.Message}");
//             }
//         }
//     }

// }


using System;
using System.Text;
using System.Threading.Tasks;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json.Linq;

public class ContinuousRecord : MonoBehaviour
{
    private AudioClip recordedClip;
    [SerializeField] private AudioSource audioSource;
    [SerializeField] private string deepGramApiKey = "077b7002b19330ce99f96adf7134bf8c50896f78"; //not good practice ik

    private string directoryPath = "/Users/aj/My project/Recordings";
    private float startTime;
    private float recordingLength;
    private int sampleRate = 44100;
    private bool isRecordingContinuous = false;
    private Coroutine recordingCoroutine;
    private int recordingCounter = 0;

    [Header("Speech Detection Settings")]
    [Tooltip("Threshold above which audio is considered speech.")]
    [Range(0f, 1f)]
    public float speechThreshold = 0.02f; // Slightly higher than silence threshold

    [Tooltip("Number of consecutive checks that must detect speech to start recording.")]
    public int requiredSpeechChecks = 2;

    private bool isListening = false;
    private Coroutine listeningCoroutine;
    // private int speechChecks = 0;

    [Header("Silence Detection Settings")]
    [Tooltip("Threshold below which audio is considered silent.")]
    [Range(0f, 1f)]
    public float silenceThreshold = 0.015f; // Adjusted based on testing

    [Tooltip("Duration (in seconds) of continuous silence to stop recording.")]
    public float silenceDurationLimit = 4f;

    [Tooltip("Interval (in seconds) between silence checks.")]
    public float silenceCheckInterval = 0.5f;

    [Tooltip("Enable or disable silence detection for testing purposes.")]
    public bool disableSilenceDetection = false;

    [Header("Grace Period Settings")]
    [Tooltip("Duration (in seconds) to record before starting silence detection.")]
    public float gracePeriod = 5f;

    private string microphoneDevice;
    private int silentChecks = 0;
    private int requiredSilentChecks;
    private int speechChecks = 0;

    private void Awake()
    {
        // list all available microphone devices
        foreach (var device in Microphone.devices)
        {
            Debug.Log("Available Microphone Device: " + device);
        }
        microphoneDevice = Microphone.devices[0];
        Debug.Log($"Selected Microphone Device: {microphoneDevice}");

        // Define the directory path
        directoryPath = Path.Combine(Application.persistentDataPath, "Recordings");
        if (!Directory.Exists(directoryPath))
        {
            Directory.CreateDirectory(directoryPath);
            Debug.Log($"Created directory: {directoryPath}");
        }

        Debug.Log($"Directory Path Set To: {directoryPath}");


        // Identify number of existing recordings
        var existingFiles = Directory.GetFiles(directoryPath, "recording_*.wav");
        recordingCounter = existingFiles.Length;
        Debug.Log($"Initial recordingCounter set to {recordingCounter}");

        // Calculate required silent checks
        requiredSilentChecks = Mathf.CeilToInt(silenceDurationLimit / silenceCheckInterval);
        Debug.Log($"Required Silent Checks set to: {requiredSilentChecks}");

        StartListening();
    }

    private void StartListening()
    {
        if (listeningCoroutine != null)
        {
            StopCoroutine(listeningCoroutine);
        }

        isListening = true;
        listeningCoroutine = StartCoroutine(ListeningLoop());
        Debug.Log("Started listening for speech...");
    }

    private IEnumerator ListeningLoop()
    {
        // Start microphone in listening mode
        AudioClip listenClip = Microphone.Start(microphoneDevice, true, 120, sampleRate);
        yield return new WaitForSeconds(0.1f); // Wait for mic to initialize

        while (isListening)
        {
            yield return new WaitForSeconds(silenceCheckInterval);

            // Get latest audio samples
            float[] samples = GetLastSamples(listenClip, silenceCheckInterval, microphoneDevice);
            if (samples == null || samples.Length == 0)
            {
                continue;
            }

            float rms = CalculateRMS(samples);
            Debug.Log($"Listening RMS: {rms}");

            if (rms > speechThreshold)
            {
                speechChecks++;
                Debug.Log($"Potential speech detected. Speech checks: {speechChecks}/{requiredSpeechChecks}");

                if (speechChecks >= requiredSpeechChecks)
                {
                    Debug.Log("Speech confirmed. Starting recording...");

                    // Stop listening and clean up
                    isListening = false;
                    Microphone.End(microphoneDevice);

                    // Start recording
                    StartContinuousRecording();
                    yield break;
                }
            }
            else
            {
                if (speechChecks > 0)
                {
                    Debug.Log("Reset speech detection counter.");
                }
                speechChecks = 0;
            }
        }
    }

    /// <summary>
    /// Starts the continuous recording process.
    /// </summary>
    public void StartContinuousRecording()
    {
        if (recordingCoroutine!=null)
        {
            Debug.LogWarning("Continuous recording is already in progress.");
            return;
        }
        
        isRecordingContinuous = true;
        recordingCoroutine = StartCoroutine(RecordLoop());
        Debug.Log("Started continuous recording.");
    }

    /// <summary>
    /// Stops the continuous recording process.
    /// </summary>
    public void StopContinuousRecording()
    {
        if (!isRecordingContinuous)
        {
            Debug.LogWarning("Continuous recording is not active.");
            return;
        }

        isRecordingContinuous = false;
        if (recordingCoroutine != null)
        {
            StopCoroutine(recordingCoroutine);
            recordingCoroutine = null;
        }
        Microphone.End(microphoneDevice);
        Debug.Log("Stopped recording.");
    }

    /// <summary>
    /// Coroutine that handles the continuous recording loop with grace period and silence detection.
    /// </summary>
    /// <returns></returns>
    private IEnumerator RecordLoop()
    {
        if (string.IsNullOrEmpty(microphoneDevice))
        {
            Debug.LogError("Microphone device is not set.");
            yield break;
        }

        // Start Recording with looping enabled and a buffer length of 120 seconds
        recordedClip = Microphone.Start(microphoneDevice, true, 120, sampleRate);
        if (recordedClip == null)
        {
            Debug.LogError("Microphone.Start returned null. Recording failed to start.");
            yield break;
        }
        startTime = Time.realtimeSinceStartup;
        Debug.Log("Recording started...");

        // Grace Period: Record for 'gracePeriod' seconds before starting silence detection
        Debug.Log($"Starting grace period of {gracePeriod} seconds.");
        yield return new WaitForSeconds(gracePeriod);
        Debug.Log("Grace period ended. Starting silence detection.");

        while (isRecordingContinuous)
        {
            yield return new WaitForSeconds(silenceCheckInterval);

            // Calculate elapsed time
            float elapsedTime = Time.realtimeSinceStartup - startTime;

            // Get the last 'silenceCheckInterval' seconds of audio data
            float[] samples = GetLastSamples(recordedClip, silenceCheckInterval, microphoneDevice);
            if (samples == null || samples.Length == 0)
            {
                Debug.LogWarning("No samples fetched for silence detection.");
                continue;
            }

            // Calculate RMS (Root Mean Square) to determine volume
            float rms = CalculateRMS(samples);
            Debug.Log($"RMS: {rms}");

            if (!disableSilenceDetection && rms < silenceThreshold)
            {
                silentChecks++;
                Debug.Log($"Silence detected. Silent Checks: {silentChecks}/{requiredSilentChecks}");
                if (silentChecks >= requiredSilentChecks)
                {
                    // Debug.Log("Silence duration limit exceeded. Stopping recording.");
                    break;
                }
            }
            else if (!disableSilenceDetection)
            {
                if (silentChecks > 0)
                {
                    Debug.Log("Sound detected. Resetting silence checks.");
                }
                silentChecks = 0;
            }
        }

        // Stop Recording
        Microphone.End(microphoneDevice);
        recordingLength = Time.realtimeSinceStartup - startTime;
        Debug.Log($"Recording stopped. Duration: {recordingLength} seconds.");

        // Trim the clip to the actual length
        recordedClip = TrimClip(recordedClip, recordingLength);
        if (recordedClip != null)
        {
            TranscribeRecording();
        }

        // Reset recording state
        isRecordingContinuous = false;
        recordingCoroutine = null;
        Debug.Log("Exited recording loop.");

        // Start listening for next speech
        StartListening();
    }

    /// <summary>
    /// Initiates the transcription of the recorded AudioClip.
    /// </summary>
    private void TranscribeRecording()
    {
        if (recordedClip != null)
        {
            StartCoroutine(TranscribeAudio(recordedClip));
        }
        else
        {
            Debug.LogError("No recording found to transcribe.");
        }
    }

    /// <summary>
    /// Transcribes the given AudioClip using DeepGram's STT service.
    /// </summary>
    /// <param name="clip">The AudioClip to transcribe.</param>
    /// <returns>A Coroutine that handles the transcription.</returns>
    private IEnumerator TranscribeAudio(AudioClip clip)
    {
        if (clip == null)
        {
            Debug.LogError("TranscribeAudio called with null AudioClip.");
            yield break;
        }

        if (string.IsNullOrEmpty(deepGramApiKey) || deepGramApiKey == "YOUR_DEEPGRAM_API_KEY")
        {
            Debug.LogError("DeepGram API Key is not set. Please set it in the Inspector.");
            yield break;
        }

        // Convert AudioClip to WAV byte array
        byte[] wavData = WavUtility.ToWavBytes(clip);
        if (wavData == null || wavData.Length == 0)
        {
            Debug.LogError("Failed to convert AudioClip to WAV format.");
            yield break;
        }

        // Prepare the DeepGram API endpoint with query parameters
        string url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true";

        // Create the UnityWebRequest
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        request.uploadHandler = new UploadHandlerRaw(wavData);
        request.downloadHandler = new DownloadHandlerBuffer();

        // Set headers
        request.SetRequestHeader("Authorization", $"Token {deepGramApiKey}");
        request.SetRequestHeader("Content-Type", "audio/wav");

        Debug.Log($"Sending transcription request to DeepGram: {url}");

        // Send the request and wait for the response
        yield return request.SendWebRequest();

        // Handle the response
        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            Debug.LogError($"DeepGram transcription failed: {request.error}");
        }
        else
        {
            // Parse the JSON response
            string jsonResponse = request.downloadHandler.text;
            // Debug.Log($"DeepGram Response: {jsonResponse}");

            try
            {
                JObject response = JObject.Parse(jsonResponse);
                string transcript = response["results"]?["channels"]?[0]?["alternatives"]?[0]?["transcript"]?.ToString();

                if (!string.IsNullOrEmpty(transcript))
                {
                    Debug.Log($"Transcription: {transcript}");
                    // TODO: Handle the transcription result as needed (e.g., display in UI, send to server)
                }
                else
                {
                    Debug.LogWarning("Transcription result is empty.");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to parse DeepGram response: {e.Message}");
            }
        }
    }

    /// <summary>
    /// Trims the AudioClip to the specified length.
    /// </summary>
    /// <param name="clip">The original AudioClip.</param>
    /// <param name="length">Desired length in seconds.</param>
    /// <returns>Trimmed AudioClip.</returns>
    private AudioClip TrimClip(AudioClip clip, float length)
    {
        if (clip == null)
        {
            Debug.LogError("TrimClip called with null AudioClip.");
            return null;
        }

        if (length <= 0)
        {
            Debug.LogError("TrimClip called with non-positive length.");
            return null;
        }

        int samples = Mathf.FloorToInt(clip.frequency * length);
        samples = Mathf.Clamp(samples, 0, clip.samples);

        if (samples <= 0)
        {
            Debug.LogError("Calculated sample count is non-positive.");
            return null;
        }

        float[] data = new float[samples * clip.channels];
        bool success = clip.GetData(data, 0);
        if (!success)
        {
            Debug.LogError("Failed to get audio data from clip.");
            return null;
        }

        AudioClip trimmedClip = AudioClip.Create(clip.name + "_trimmed", samples, clip.channels, clip.frequency, false);
        trimmedClip.SetData(data, 0);

        Debug.Log("AudioClip trimmed successfully.");

        return trimmedClip;
    }

    /// <summary>
    /// Retrieves the last 'seconds' seconds of audio data from the AudioClip.
    /// </summary>
    /// <param name="clip">The AudioClip to retrieve data from.</param>
    /// <param name="seconds">The duration in seconds of audio data to retrieve.</param>
    /// <param name="device">The microphone device name.</param>
    /// <returns>Array of float samples.</returns>
    private float[] GetLastSamples(AudioClip clip, float seconds, string device)
    {
        if (clip == null)
        {
            Debug.LogError("GetLastSamples called with null AudioClip.");
            return null;
        }

        // Calculate the number of samples to retrieve
        int samplesToRead = Mathf.FloorToInt(clip.frequency * seconds) * clip.channels;
        samplesToRead = Mathf.Min(samplesToRead, clip.samples); // Ensure we don't exceed the buffer
        float[] data = new float[samplesToRead];

        // Get the current recording position
        int currentPosition = Microphone.GetPosition(device);
        if (currentPosition < 0)
        {
            Debug.LogWarning("Microphone.GetPosition returned a negative value.");
            return null;
        }

        // Calculate the start sample index
        int startSample = currentPosition - samplesToRead;
        if (startSample < 0)
        {
            // Wrap around if necessary
            int firstPart = clip.samples - (samplesToRead - currentPosition);
            clip.GetData(data, firstPart);

            // If still required, fetch the remaining samples from the beginning
            if (samplesToRead > firstPart)
            {
                int secondPart = samplesToRead - firstPart;
                float[] tempData = new float[samplesToRead];
                clip.GetData(data, firstPart);
                clip.GetData(tempData, 0);
                Array.Copy(tempData, 0, data, firstPart, secondPart);
            }
        }
        else
        {
            // No wrap around
            clip.GetData(data, startSample);
        }

        // Debugging: Verify that samples are being fetched correctly
        bool hasNonZeroSamples = false;
        foreach (var sample in data)
        {
            if (sample != 0f)
            {
                hasNonZeroSamples = true;
                break;
            }
        }
        // Debug.Log(hasNonZeroSamples ? "Fetched non-zero samples successfully." : "Fetched samples are all zero.");

        return data;
    }

    /// <summary>
    /// Calculates the Root Mean Square (RMS) of the audio samples.
    /// </summary>
    /// <param name="samples">Array of float samples.</param>
    /// <returns>RMS value.</returns>
    private float CalculateRMS(float[] samples)
    {
        if (samples == null || samples.Length == 0)
        {
            Debug.LogWarning("CalculateRMS called with null or empty samples.");
            return 0f;
        }

        float sum = 0f;
        foreach (var sample in samples)
        {
            sum += sample * sample;
        }
        float rms = Mathf.Sqrt(sum / samples.Length);
        return rms;
    }
}
