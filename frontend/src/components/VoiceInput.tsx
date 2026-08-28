import { Mic } from "lucide-react";

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  existingText?: string;
}

function VoiceInput({
  onTranscript,
}: VoiceInputProps) {
  const handleClick = () => {
    console.log("VOICE BUTTON CLICKED");

    onTranscript(
      "This is a voice input test."
    );
  };

  return (
    <div
      style={{
        padding: "16px",
        marginBottom: "12px",
        border: "2px solid red",
        borderRadius: "12px",
        background: "#fff",
      }}
    >
      <button
        type="button"
        onClick={handleClick}
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
        Speak Test
      </button>
    </div>
  );
}

export default VoiceInput;