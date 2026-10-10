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
  const [statusMessage, setStatusMessage] = useState("");

  const recognitionRef = useRef<any>(null);
  const isListeningRef = useRef(false);
  const existingTextRef = useRef(existingText);
  const onTranscriptRef = useRef(onTranscript);

  // Keep the latest journal text available.
  useEffect(() => {
    existingTextRef.current = existingText;
  }, [existingText]);

  // Keep the latest callback available.
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  // Initialize speech recognition.
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.error(
        "VOICE: Speech recognition is not supported by this browser."
      );

      setSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-IN";
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      console.log("VOICE: Recognition started");

      isListeningRef.current = true;
      setIsListening(true);
      setErrorMessage("");
      setStatusMessage("Listening... Speak clearly.");
    };

    recognition.onaudiostart = () => {
      console.log("VOICE: Audio capture started");
    };

    recognition.onspeechstart = () => {
      console.log("VOICE: Speech detected");
      setStatusMessage("Speech detected... processing.");
    };

    recognition.onspeechend = () => {
      console.log("VOICE: Speech ended");
    };

    recognition.onresult = (event: any) => {
      console.log("VOICE: Result event received", event);

      let finalTranscript = "";
      let interimTranscript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        const result = event.results[i];
        const transcript = result[0]?.transcript ?? "";

        if (result.isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      // Show temporary recognition results while speaking.
      if (interimTranscript.trim()) {
        console.log("VOICE: Interim transcript:", interimTranscript);
        setStatusMessage(`Recognizing: ${interimTranscript}`);
      }

      // Add only finalized speech to the journal.
      if (finalTranscript.trim()) {
        const recognizedText = finalTranscript.trim();

        console.log("VOICE: Final transcript:", recognizedText);

        const currentText = existingTextRef.current.trim();

        const newText = currentText
          ? `${currentText} ${recognizedText}`
          : recognizedText;

        existingTextRef.current = newText;
        onTranscriptRef.current(newText);

        setStatusMessage("Speech added to your journal.");
      }
    };

    recognition.onerror = (event: any) => {
      console.error("VOICE: Recognition error:", event.error);

      isListeningRef.current = false;
      setIsListening(false);

      switch (event.error) {
        case "not-allowed":
        case "service-not-allowed":
          setErrorMessage(
            "Microphone or speech recognition permission was denied. Check Chrome site permissions."
          );
          break;

        case "no-speech":
          setErrorMessage(
            "No speech was detected. Check your microphone and try speaking louder."
          );
          break;

        case "network":
          setErrorMessage(
            "Speech recognition encountered a network error. Check your internet connection and try again."
          );
          break;

        case "audio-capture":
          setErrorMessage(
            "No microphone audio is available. Check your microphone settings."
          );
          break;

        case "aborted":
          setErrorMessage("");
          break;

        default:
          setErrorMessage(
            `Speech recognition failed: ${event.error}`
          );
      }

      setStatusMessage("");
    };

    recognition.onend = () => {
      console.log("VOICE: Recognition ended");

      isListeningRef.current = false;
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.abort();
      } catch {
        // Recognition may already be stopped.
      }

      recognitionRef.current = null;
      isListeningRef.current = false;
    };
  }, []);

  // Start speech recognition.
  const startListening = () => {
    console.log("VOICE: Speak button clicked");

    if (!supported) {
      setErrorMessage(
        "Speech recognition is not supported. Please use an up-to-date version of Google Chrome."
      );
      return;
    }

    if (!recognitionRef.current) {
      console.error("VOICE: Recognition is not initialized.");

      setErrorMessage(
        "Speech recognition is not initialized. Refresh the page and try again."
      );
      return;
    }

    if (isListeningRef.current) {
      console.log("VOICE: Recognition is already running.");
      return;
    }

    try {
      setErrorMessage("");
      setStatusMessage("Starting microphone and speech recognition...");

      recognitionRef.current.start();
    } catch (error: any) {
      console.error("VOICE: Unable to start recognition:", error);

      if (error.name === "InvalidStateError") {
        setErrorMessage(
          "Speech recognition is already running. Please wait or click Stop."
        );
      } else {
        setErrorMessage(
          `Unable to start speech recognition: ${
            error.message || error.name || "Unknown error"
          }`
        );
      }

      setStatusMessage("");
    }
  };

  // Stop speech recognition.
  const stopListening = () => {
    console.log("VOICE: Stop button clicked");

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error("VOICE: Error stopping recognition:", error);
      }
    }

    isListeningRef.current = false;
    setIsListening(false);
    setStatusMessage("Voice input stopped.");
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
        <p style={{ margin: 0, color: "#ef4444" }}>
          Speech recognition is not supported in this browser.
          Please use Google Chrome.
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
          {statusMessage || "Listening... Speak clearly."}
        </div>
      )}

      {!isListening && statusMessage && (
        <p
          style={{
            marginTop: "10px",
            color: "#6b7280",
            fontSize: "14px",
          }}
        >
          {statusMessage}
        </p>
      )}

      {errorMessage && (
        <div
          role="alert"
          style={{
            marginTop: "10px",
            display: "flex",
            alignItems: "flex-start",
            gap: "8px",
            color: "#dc2626",
            fontSize: "14px",
          }}
        >
          <MicOff size={18} />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}

export default VoiceInput;