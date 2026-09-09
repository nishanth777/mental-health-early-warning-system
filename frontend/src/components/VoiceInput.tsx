import { useEffect, useRef, useState } from "react";
import { Mic, MicOff, Square } from "lucide-react";

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  existingText?: string;
}

function VoiceInput({
  onTranscript,
  existingText = "",
}: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const recognitionRef = useRef<any>(null);
  const isListeningRef = useRef(false);
  const existingTextRef = useRef(existingText);
  const onTranscriptRef = useRef(onTranscript);

  // Keep the latest journal text available without recreating recognition
  useEffect(() => {
    existingTextRef.current = existingText;
  }, [existingText]);

  // Keep the latest callback available
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
      console.log("🎤 Microphone started");

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

        const currentText = existingTextRef.current.trim();

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
        // Normal when Stop is pressed.
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

      recognitionRef.current = null;
      isListeningRef.current = false;
    };
  }, []);

  const startListening = () => {
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

    // Prevent duplicate start() calls
    if (isListeningRef.current) {
      console.log(
        "🎤 Recognition is already running."
      );
      return;
    }

    try {
      setErrorMessage("");

      recognitionRef.current.start();

      console.log(
        "🎤 Starting speech recognition..."
      );
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
          "Unable to start speech recognition. Please try again."
        );
      }
    }
  };

  const stopListening = () => {
    console.log(
      "🛑 Stopping speech recognition..."
    );

    if (!recognitionRef.current) {
      return;
    }

    try {
      recognitionRef.current.stop();
    } catch (error) {
      console.error(
        "Error stopping recognition:",
        error
      );
    }

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