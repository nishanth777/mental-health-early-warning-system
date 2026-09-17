import { useEffect, useRef, useState } from "react";
import { Mic, MicOff, Square } from "lucide-react";

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  existingText?: string;
  onAudioRecorded?: (audioBlob: Blob) => void;
}

function VoiceInput({
  onTranscript,
  existingText = "",
  onAudioRecorded,
}: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const recognitionRef = useRef<any>(null);
  const isListeningRef = useRef(false);

  const existingTextRef = useRef(existingText);
  const onTranscriptRef = useRef(onTranscript);

  // Audio recording references
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Keep the latest journal text available
  useEffect(() => {
    existingTextRef.current = existingText;
  }, [existingText]);

  // Keep the latest transcript callback available
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-IN";

    recognition.onstart = () => {
      console.log("🎤 Speech recognition started");

      isListeningRef.current = true;
      setIsListening(true);
      setErrorMessage("");
    };

    recognition.onresult = (event: any) => {
      let transcript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        if (event.results[i].isFinal) {
          transcript += event.results[i][0].transcript;
        }
      }

      if (transcript.trim()) {
        console.log("📝 Transcript:", transcript);

        const currentText =
          existingTextRef.current.trim();

        const newText = currentText
          ? `${currentText} ${transcript.trim()}`
          : transcript.trim();

        existingTextRef.current = newText;

        onTranscriptRef.current(newText);
      }
    };

    recognition.onerror = (event: any) => {
      console.error(
        "🎤 Speech recognition error:",
        event.error
      );

      isListeningRef.current = false;
      setIsListening(false);

      if (event.error === "not-allowed") {
        setErrorMessage(
          "Microphone permission was denied. Please allow microphone access in Chrome."
        );
      } else if (event.error === "no-speech") {
        setErrorMessage(
          "No speech detected. Please try speaking again."
        );
      } else if (event.error === "network") {
        setErrorMessage(
          "Speech recognition needs an internet connection."
        );
      } else if (event.error === "aborted") {
        setErrorMessage("");
      } else {
        setErrorMessage(
          `Speech recognition error: ${event.error}`
        );
      }
    };

    recognition.onend = () => {
      console.log("🎤 Speech recognition ended");

      isListeningRef.current = false;
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.stop();
      } catch {
        // Recognition may already be stopped.
      }

      if (mediaRecorderRef.current) {
        try {
          mediaRecorderRef.current.stop();
        } catch {
          // Recorder may already be stopped.
        }
      }

      if (mediaStreamRef.current) {
        mediaStreamRef.current
          .getTracks()
          .forEach((track) => track.stop());
      }

      recognitionRef.current = null;
      mediaRecorderRef.current = null;
      mediaStreamRef.current = null;
      isListeningRef.current = false;
    };
  }, []);

  /*
   * Start recording the actual microphone audio.
   *
   * This audio will later be used for voice-feature
   * extraction such as pitch, energy, pauses, MFCCs,
   * speaking rate, etc.
   */
  const startAudioRecording = async () => {
    try {
      console.log(
        "🎙️ Requesting microphone for audio analysis..."
      );

      if (
        !navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia
      ) {
        throw new Error(
          "Microphone recording is not supported."
        );
      }

      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      mediaStreamRef.current = stream;
      audioChunksRef.current = [];

      /*
       * Use WebM/Opus when available.
       * Chrome normally supports this format.
       */
      let options: MediaRecorderOptions = {};

      if (
        MediaRecorder.isTypeSupported(
          "audio/webm;codecs=opus"
        )
      ) {
        options = {
          mimeType: "audio/webm;codecs=opus",
        };
      } else if (
        MediaRecorder.isTypeSupported("audio/webm")
      ) {
        options = {
          mimeType: "audio/webm",
        };
      }

      const recorder = new MediaRecorder(
        stream,
        options
      );

      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onerror = (event) => {
        console.error(
          "🎙️ MediaRecorder error:",
          event
        );
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type:
              recorder.mimeType ||
              "audio/webm",
          }
        );

        console.log(
          "🎧 Audio recording created:",
          audioBlob.size,
          "bytes"
        );

        console.log(
          "🎧 Audio type:",
          audioBlob.type
        );

        /*
         * Send the recorded audio to the parent
         * component if it wants to use it.
         */
        if (onAudioRecorded) {
          onAudioRecorded(audioBlob);
        }

        /*
         * Release microphone resources.
         */
        stream
          .getTracks()
          .forEach((track) => track.stop());

        mediaStreamRef.current = null;
        mediaRecorderRef.current = null;
        audioChunksRef.current = [];
      };

      recorder.start();

      console.log(
        "🎙️ Audio recording started"
      );
    } catch (error) {
      console.error(
        "🎙️ Audio recording error:",
        error
      );

      setErrorMessage(
        "Unable to access the microphone for voice analysis."
      );

      throw error;
    }
  };

  /*
   * Stop the actual audio recorder.
   */
  const stopAudioRecording = () => {
    console.log(
      "🛑 Stopping audio recording..."
    );

    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }
  };

  /*
   * Start both:
   *
   * 1. SpeechRecognition → journal text
   * 2. MediaRecorder → audio Blob
   *
   * Speech recognition is started first so the existing
   * speech-to-text functionality remains the priority.
   */
  const startListening = async () => {
    console.log("VOICE BUTTON CLICKED");

    if (!supported) {
      setErrorMessage(
        "Speech recognition is not supported in this browser. Please use Google Chrome."
      );
      return;
    }

    if (!recognitionRef.current) {
      setErrorMessage(
        "Speech recognition is not initialized."
      );
      return;
    }

    if (isListeningRef.current) {
      console.log(
        "🎤 Recognition is already running."
      );
      return;
    }

    try {
      setErrorMessage("");

      /*
       * Start speech recognition first.
       */
      recognitionRef.current.start();

      console.log(
        "🎤 Starting speech recognition..."
      );

      /*
       * Start audio recording separately.
       *
       * If this fails, speech-to-text continues working.
       */
      try {
        await startAudioRecording();
      } catch (audioError) {
        console.error(
          "🎙️ Audio recording could not start:",
          audioError
        );

        /*
         * Do not stop speech recognition.
         * The journal voice input should continue working.
         */
      }
    } catch (error: any) {
      console.error(
        "Speech recognition start error:",
        error
      );

      if (error.name === "InvalidStateError") {
        console.log(
          "🎤 Recognition was already running."
        );

        isListeningRef.current = true;
        setIsListening(true);
      } else {
        setErrorMessage(
          "Unable to start voice input. Please try again."
        );
      }
    }
  };

  /*
   * Stop both speech recognition and audio recording.
   */
  const stopListening = () => {
    console.log(
      "🛑 Stopping voice input..."
    );

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error(
          "Error stopping recognition:",
          error
        );
      }
    }

    stopAudioRecording();

    isListeningRef.current = false;
    setIsListening(false);
  };

  if (!supported) {
    return (
      <div
        style={{
          padding: "16px",
          marginBottom: "12px",
          border: "1px solid #ef4444",
          borderRadius: "12px",
        }}
      >
        <p
          style={{
            margin: 0,
            color: "#ef4444",
          }}
        >
          Voice input is not supported in this
          browser. Please use Google Chrome.
        </p>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "16px",
        marginBottom: "12px",
        border: "1px solid #8b5cf6",
        borderRadius: "12px",
        background: "#fff",
      }}
    >
      {!isListening ? (
        <button
          type="button"
          onClick={startListening}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 16px",
            border: "none",
            borderRadius: "10px",
            background: "#8b5cf6",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          <Mic size={18} />
          Speak
        </button>
      ) : (
        <button
          type="button"
          onClick={stopListening}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "10px 16px",
            border: "none",
            borderRadius: "10px",
            background: "#ef4444",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          <Square size={18} />
          Stop
        </button>
      )}

      {isListening && (
        <div
          style={{
            marginTop: "10px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            color: "#8b5cf6",
            fontSize: "14px",
          }}
        >
          <Mic size={16} />
          Listening... Speak clearly.
        </div>
      )}

      {errorMessage && (
        <div
          style={{
            marginTop: "10px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            color: "#dc2626",
            fontSize: "14px",
          }}
        >
          <MicOff size={16} />
          {errorMessage}
        </div>
      )}
    </div>
  );
}

export default VoiceInput;