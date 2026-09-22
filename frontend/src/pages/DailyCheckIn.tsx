import {
  Home,
  ClipboardCheck,
  TrendingUp,
  User,
  Settings,
  Moon,
  LogOut,
  Menu,
  X,
  Heart,
  Brain,
  Activity,
  Send,
  CheckCircle2,
  AlertCircle,
  Mic,
} from "lucide-react";

import { useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

import api from "../services/api";
import VoiceInput from "../components/VoiceInput";
import "../App.css";

interface AssessmentResult {
  prediction: number;
  risk_score: number;
  risk_level: string;
  recommendations: string[];

  voice_used?: boolean;
  voice_features?: Record<string, number> | null;
}

function DailyCheckIn() {
  const { logout } = useAuth();

  const {
    darkMode,
    toggleDarkMode,
  } = useTheme();

  const navigate = useNavigate();

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  const [result, setResult] =
    useState<AssessmentResult | null>(null);

  const [sleepHours, setSleepHours] =
    useState("");

  const [sleepQuality, setSleepQuality] =
    useState<number | null>(null);

  const [stressLevel, setStressLevel] =
    useState<number | null>(null);

  const [academicPressure, setAcademicPressure] =
    useState<number | null>(null);

  const [mood, setMood] =
    useState<number | null>(null);

  const [energyLevel, setEnergyLevel] =
    useState<number | null>(null);

  const [socialInteraction, setSocialInteraction] =
    useState<number | null>(null);

  const [exerciseMinutes, setExerciseMinutes] =
    useState("");

  const [screenTime, setScreenTime] =
    useState("");

  const [studyHours, setStudyHours] =
    useState("");

  const [journalText, setJournalText] =
    useState("");

  const [voiceAudio, setVoiceAudio] =
    useState<Blob | null>(null);

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");
    setResult(null);

    if (
      sleepQuality === null ||
      stressLevel === null ||
      academicPressure === null ||
      mood === null ||
      energyLevel === null ||
      socialInteraction === null
    ) {
      setError(
        "Please complete all wellbeing ratings before submitting."
      );
      return;
    }

    const sleep = Number(sleepHours);
    const exercise = Number(exerciseMinutes);
    const screen = Number(screenTime);
    const study = Number(studyHours);

    if (
      !Number.isFinite(sleep) ||
      sleep < 3 ||
      sleep > 9
    ) {
      setError(
        "Sleep duration should be between 3 and 9 hours."
      );
      return;
    }

    if (
      !Number.isFinite(exercise) ||
      exercise < 0 ||
      exercise > 90
    ) {
      setError(
        "Exercise duration should be between 0 and 90 minutes."
      );
      return;
    }

    if (
      !Number.isFinite(screen) ||
      screen < 0 ||
      screen > 24
    ) {
      setError(
        "Screen time should be between 0 and 24 hours."
      );
      return;
    }

    if (
      !Number.isFinite(study) ||
      study < 2 ||
      study > 12
    ) {
      setError(
        "Study hours should be between 2 and 12 hours."
      );
      return;
    }

    if (!journalText.trim()) {
      setError(
        "Please write a short reflection before submitting."
      );
      return;
    }

    try {
      setSubmitting(true);

      const token =
        localStorage.getItem("access_token");

      if (!token) {
        logout();
        return;
      }

      const formData = new FormData();

      formData.append(
        "sleep_hours",
        String(sleep)
      );

      formData.append(
        "sleep_quality",
        String(sleepQuality)
      );

      formData.append(
        "stress_level",
        String(stressLevel)
      );

      formData.append(
        "academic_pressure",
        String(academicPressure)
      );

      formData.append(
        "mood",
        String(mood)
      );

      formData.append(
        "energy_level",
        String(energyLevel)
      );

      formData.append(
        "social_interaction",
        String(socialInteraction)
      );

      formData.append(
        "exercise_minutes",
        String(exercise)
      );

      formData.append(
        "screen_time",
        String(screen)
      );

      formData.append(
        "study_hours",
        String(study)
      );

      formData.append(
        "journal_text",
        journalText.trim()
      );

      if (voiceAudio) {
        formData.append(
          "voice_audio",
          voiceAudio,
          "voice_recording.webm"
        );

        console.log(
          "🎙️ Sending voice audio:",
          voiceAudio.size,
          "bytes",
          voiceAudio.type
        );
      } else {
        console.log(
          "🎙️ No voice audio recorded."
        );
      }

      const response =
        await api.post(
          "/assessment/",
          formData,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

      console.log(
        "✅ Assessment submitted:",
        response.data
      );

      setResult(response.data);

    } catch (err: any) {
      console.error(
        "Assessment submission failed:",
        err
      );

      if (
        err.response?.status === 401
      ) {
        logout();
        return;
      }

      setError(
        err.response?.data?.error ||
          "Unable to submit your check-in. Please try again."
      );

    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="dashboard-page">

      {/* Mobile menu */}
      <button
        className="mobile-menu-button"
        onClick={() =>
          setSidebarOpen(true)
        }
        aria-label="Open navigation"
      >
        <Menu size={22} />
      </button>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() =>
            setSidebarOpen(false)
          }
        />
      )}

      {/* Sidebar */}
      <aside
        className={`dashboard-sidebar ${
          sidebarOpen
            ? "sidebar-open"
            : ""
        }`}
      >
        <div className="sidebar-top">

          <div className="sidebar-brand">

            <span>
              Clarity
            </span>

            <button
              className="mobile-close-button"
              onClick={() =>
                setSidebarOpen(false)
              }
              aria-label="Close navigation"
            >
              <X size={20} />
            </button>

          </div>

          <nav className="sidebar-navigation">

            <Link
              to="/dashboard"
              className="sidebar-item"
              onClick={() =>
                setSidebarOpen(false)
              }
            >
              <Home size={19} />
              <span>
                Dashboard
              </span>
            </Link>

            <Link
              to="/check-in"
              className="sidebar-item active"
              onClick={() =>
                setSidebarOpen(false)
              }
            >
              <ClipboardCheck size={19} />
              <span>
                Daily Check-In
              </span>
            </Link>

            <Link
              to="/progress"
              className="sidebar-item"
              onClick={() =>
                setSidebarOpen(false)
              }
            >
              <TrendingUp size={19} />
              <span>
                Progress
              </span>
            </Link>

            <Link
              to="/profile"
              className="sidebar-item"
              onClick={() =>
                setSidebarOpen(false)
              }
            >
              <User size={19} />
              <span>
                Profile
              </span>
            </Link>

          </nav>

        </div>

        <div className="sidebar-bottom">

          <Link
            to="/settings"
            className="sidebar-item"
            onClick={() =>
              setSidebarOpen(false)
            }
          >
            <Settings size={19} />
            <span>
              Settings
            </span>
          </Link>

          <button
            className="sidebar-item sidebar-button"
            type="button"
            onClick={toggleDarkMode}
          >
            <Moon size={19} />

            <span>
              {darkMode
                ? "Light Mode"
                : "Dark Mode"}
            </span>
          </button>

          <button
            className="sidebar-item sidebar-button logout-item"
            type="button"
            onClick={logout}
          >
            <LogOut size={19} />

            <span>
              Logout
            </span>
          </button>

        </div>
      </aside>

      {/* Main */}
      <main className="dashboard-main checkin-main">

        <header className="checkin-header">

          <div>

            <p className="dashboard-eyebrow">
              Daily wellbeing check-in
            </p>

            <h1>
              How are you feeling today?
            </h1>

            <p className="dashboard-subtitle">
              Take a few minutes to reflect
              on how you've been doing.
            </p>

          </div>

        </header>

        {/* =========================
            RESULT
        ========================== */}

        {result && (
          <section className="assessment-result">

            <div className="result-icon">
              <CheckCircle2 size={30} />
            </div>

            <p className="dashboard-eyebrow">
              Assessment complete
            </p>

            <h2>
              Your wellbeing snapshot
            </h2>

            <div className="result-score">

              <strong>
                {result.risk_score}%
              </strong>

              <span
                className={`risk-${result.risk_level.toLowerCase()}`}
              >
                {result.risk_level}
              </span>

            </div>

            <p className="result-description">
              This result is an awareness
              indicator based on your
              self-reported wellbeing data.
              It is not a medical diagnosis.
            </p>

            {/* =========================
                VOICE ANALYSIS
            ========================== */}

            {result.voice_used && (
              <div className="voice-analysis-status">

                <div className="voice-analysis-icon">
                  <Mic size={20} />
                </div>

                <div className="voice-analysis-content">

                  <strong>
                    Voice analysis captured
                  </strong>

                  <p>
                    Your voice recording was
                    successfully processed for
                    acoustic feature extraction.
                  </p>

                  <small>
                    Voice features are currently
                    collected separately and are
                    not used to determine the
                    displayed risk score.
                  </small>

                </div>

              </div>
            )}

            {/* Recommendations */}

            {result.recommendations &&
              result.recommendations.length >
                0 && (
                <div className="recommendations">

                  <h3>
                    Suggestions
                  </h3>

                  <ul>
                    {result.recommendations.map(
                      (
                        recommendation,
                        index
                      ) => (
                        <li key={index}>
                          {recommendation}
                        </li>
                      )
                    )}
                  </ul>

                </div>
              )}

            <button
              className="primary-dashboard-button"
              type="button"
              onClick={() =>
                navigate("/progress")
              }
            >
              View my progress
            </button>

          </section>
        )}

        {/* =========================
            FORM
        ========================== */}

        {!result && (
          <form
            className="checkin-form"
            onSubmit={handleSubmit}
          >

            {error && (
              <div className="checkin-error">

                <AlertCircle size={20} />

                <span>
                  {error}
                </span>

              </div>
            )}

            {/* Sleep */}

            <section className="checkin-card">

              <div className="checkin-card-header">

                <div className="checkin-section-icon">
                  <Moon size={21} />
                </div>

                <div>

                  <span>
                    01
                  </span>

                  <h2>
                    Sleep
                  </h2>

                  <p>
                    How has your sleep
                    been recently?
                  </p>

                </div>

              </div>

              <div className="checkin-fields">

                <div className="checkin-field">

                  <label htmlFor="sleep-hours">
                    How many hours did you
                    sleep?
                  </label>

                  <div className="number-input-row">

                    <input
                      id="sleep-hours"
                      type="number"
                      min="3"
                      max="9"
                      step="0.1"
                      placeholder="7.5"
                      value={sleepHours}
                      onChange={(event) =>
                        setSleepHours(
                          event.target.value
                        )
                      }
                    />

                    <span>
                      hours
                    </span>

                  </div>

                  <small>
                    Between 3 and 9 hours
                  </small>

                </div>

                <RatingSelector
                  label="How would you rate your sleep quality?"
                  value={sleepQuality}
                  onChange={
                    setSleepQuality
                  }
                  labels={[
                    "Very poor",
                    "Poor",
                    "Okay",
                    "Good",
                    "Excellent",
                  ]}
                />

              </div>

            </section>

            {/* Mind & Mood */}

            <section className="checkin-card">

              <div className="checkin-card-header">

                <div className="checkin-section-icon">
                  <Brain size={21} />
                </div>

                <div>

                  <span>
                    02
                  </span>

                  <h2>
                    Mind & Mood
                  </h2>

                  <p>
                    Reflect on your emotional
                    and mental wellbeing.
                  </p>

                </div>

              </div>

              <div className="checkin-fields">

                <RatingSelector
                  label="How would you describe your mood?"
                  value={mood}
                  onChange={setMood}
                  labels={[
                    "Very low",
                    "Low",
                    "Okay",
                    "Good",
                    "Very good",
                  ]}
                />

                <RatingSelector
                  label="How stressed have you been feeling?"
                  value={stressLevel}
                  onChange={
                    setStressLevel
                  }
                  labels={[
                    "Very low",
                    "Low",
                    "Moderate",
                    "High",
                    "Very high",
                  ]}
                />

                <RatingSelector
                  label="How much academic pressure are you experiencing?"
                  value={academicPressure}
                  onChange={
                    setAcademicPressure
                  }
                  labels={[
                    "Very low",
                    "Low",
                    "Moderate",
                    "High",
                    "Very high",
                  ]}
                />

                <RatingSelector
                  label="How would you rate your energy?"
                  value={energyLevel}
                  onChange={
                    setEnergyLevel
                  }
                  labels={[
                    "Very low",
                    "Low",
                    "Okay",
                    "Good",
                    "Very high",
                  ]}
                />

              </div>

            </section>

            {/* Lifestyle */}

            <section className="checkin-card">

              <div className="checkin-card-header">

                <div className="checkin-section-icon">
                  <Activity size={21} />
                </div>

                <div>

                  <span>
                    03
                  </span>

                  <h2>
                    Lifestyle
                  </h2>

                  <p>
                    Tell us a little about
                    your daily routine.
                  </p>

                </div>

              </div>

              <div className="checkin-fields">

                <RatingSelector
                  label="How much social interaction have you had?"
                  value={
                    socialInteraction
                  }
                  onChange={
                    setSocialInteraction
                  }
                  labels={[
                    "Very little",
                    "Little",
                    "Some",
                    "Good",
                    "Very good",
                  ]}
                />

                <div className="input-grid">

                  <NumberField
                    id="exercise"
                    label="Exercise"
                    value={
                      exerciseMinutes
                    }
                    onChange={
                      setExerciseMinutes
                    }
                    placeholder="30"
                    suffix="minutes"
                    min="0"
                    max="90"
                    step="1"
                  />

                  <NumberField
                    id="screen-time"
                    label="Screen time"
                    value={screenTime}
                    onChange={
                      setScreenTime
                    }
                    placeholder="5"
                    suffix="hours"
                    min="0"
                    max="24"
                    step="0.1"
                  />

                  <NumberField
                    id="study-hours"
                    label="Study time"
                    value={studyHours}
                    onChange={
                      setStudyHours
                    }
                    placeholder="5"
                    suffix="hours"
                    min="2"
                    max="12"
                    step="0.1"
                  />

                </div>

              </div>

            </section>

            {/* Reflection */}

            <section className="checkin-card">

              <div className="checkin-card-header">

                <div className="checkin-section-icon">
                  <Heart size={21} />
                </div>

                <div>

                  <span>
                    04
                  </span>

                  <h2>
                    Reflection
                  </h2>

                  <p>
                    Put your thoughts into
                    words.
                  </p>

                </div>

              </div>

              <div className="checkin-field">

                <label htmlFor="journal">
                  Is there anything you'd like
                  to share about how you're
                  feeling?
                </label>

                <VoiceInput
                  existingText={journalText}
                  onTranscript={(text) =>
                    setJournalText(text)
                  }
                  onAudioRecorded={(audioBlob) =>
                    setVoiceAudio(audioBlob)
                  }
                />

                <textarea
                  id="journal"
                  rows={6}
                  placeholder="Write a few thoughts about your day..."
                  value={journalText}
                  onChange={(event) =>
                    setJournalText(
                      event.target.value
                    )
                  }
                />

                <small>
                  Your reflection is saved with
                  your assessment.
                </small>

              </div>

            </section>

            {/* Submit */}

            <div className="checkin-submit">

              <div>

                <p>
                  Ready to check in?
                </p>

                <span>
                  Your responses will be used
                  to create your wellbeing
                  snapshot.
                </span>

              </div>

              <button
                className="submit-checkin-button"
                type="submit"
                disabled={submitting}
              >

                {submitting ? (
                  <>
                    <Activity size={18} />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send size={18} />
                    Analyze my check-in
                  </>
                )}

              </button>

            </div>

            <p className="assessment-disclaimer">
              Clarity is designed for awareness
              and preventive wellbeing support.
              It does not diagnose mental health
              conditions.
            </p>

          </form>
        )}

      </main>

    </div>
  );
}

/*
 * 1–5 rating selector.
 */
interface RatingSelectorProps {
  label: string;
  value: number | null;
  onChange: (value: number) => void;
  labels: string[];
}

function RatingSelector({
  label,
  value,
  onChange,
  labels,
}: RatingSelectorProps) {
  return (
    <div className="rating-field">

      <label>
        {label}
      </label>

      <div className="rating-options">

        {[1, 2, 3, 4, 5].map(
          (number) => (
            <button
              key={number}
              type="button"
              className={
                value === number
                  ? "rating-option selected"
                  : "rating-option"
              }
              onClick={() =>
                onChange(number)
              }
              aria-label={`${number} - ${labels[number - 1]}`}
            >
              <strong>
                {number}
              </strong>

              <span>
                {labels[number - 1]}
              </span>

            </button>
          )
        )}

      </div>

    </div>
  );
}

/*
 * Numerical input.
 */
interface NumberFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  suffix: string;
  min: string;
  max: string;
  step: string;
}

function NumberField({
  id,
  label,
  value,
  onChange,
  placeholder,
  suffix,
  min,
  max,
  step,
}: NumberFieldProps) {
  return (
    <div className="checkin-field">

      <label htmlFor={id}>
        {label}
      </label>

      <div className="number-input-row">

        <input
          id={id}
          type="number"
          min={min}
          max={max}
          step={step}
          placeholder={placeholder}
          value={value}
          onChange={(event) =>
            onChange(
              event.target.value
            )
          }
        />

        <span>
          {suffix}
        </span>

      </div>

    </div>
  );
}

export default DailyCheckIn;