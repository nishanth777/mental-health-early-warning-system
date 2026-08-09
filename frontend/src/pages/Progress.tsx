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
  Activity,
  Heart,
  Brain,
  RefreshCw,
} from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

import api from "../services/api";

import "../App.css";

interface Assessment {
  id: number;
  prediction_score: number;

  sleep_hours: number;
  sleep_quality: number;

  stress_level: number;
  academic_pressure: number;

  mood: number;
  energy_level: number;
  social_interaction: number;

  exercise_minutes: number;

  screen_time: number;
  study_hours: number;

  journal_text: string;

  created_at: string;
}

interface HistoryResponse {
  count: number;
  assessments: Assessment[];
}

interface ChartAssessment {
  date: string;
  risk: number;
  mood: number;
  energy: number;
  sleep: number;
  stress: number;
}

function Progress() {
  const { logout } = useAuth();

  /*
   * Global theme state.
   *
   * This is important:
   * Progress no longer owns its own dark-mode state.
   * The same ThemeContext is shared by Dashboard,
   * Daily Check-In, Profile and Settings.
   */
  const {
    darkMode,
    toggleDarkMode,
  } = useTheme();

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const [assessments, setAssessments] =
    useState<Assessment[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError("");

      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!token) {
        logout();
        return;
      }

      const response =
        await api.get<HistoryResponse>(
          "/assessment/history",
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

      setAssessments(
        response.data.assessments
      );

    } catch (err: any) {
      console.error(
        "Failed to load assessment history:",
        err
      );

      /*
       * Session expired.
       */
      if (
        err.response?.status === 401
      ) {
        logout();
        return;
      }

      /*
       * No history yet.
       */
      if (
        err.response?.status === 404
      ) {
        setAssessments([]);
        return;
      }

      setError(
        "Unable to load your wellbeing history."
      );

    } finally {
      setLoading(false);
    }
  };

  /*
   * Convert risk score into readable level.
   */
  const getRiskLevel = (
    score: number
  ) => {
    if (score < 30) {
      return "Low";
    }

    if (score < 70) {
      return "Moderate";
    }

    return "High";
  };

  /*
   * CSS class for risk level.
   */
  const getRiskClass = (
    score: number
  ) => {
    if (score < 30) {
      return "risk-low";
    }

    if (score < 70) {
      return "risk-moderate";
    }

    return "risk-high";
  };

  /*
   * Format dates for charts.
   */
  const formatDate = (
    date: string
  ) => {
    return new Date(
      date
    ).toLocaleDateString(
      "en-IN",
      {
        day: "numeric",
        month: "short",
      }
    );
  };

  /*
   * Backend returns newest first.
   *
   * Charts should display:
   *
   * oldest → newest
   */
  const chartData: ChartAssessment[] =
    [...assessments]
      .reverse()
      .map(
        (assessment) => ({
          date: formatDate(
            assessment.created_at
          ),

          risk:
            assessment.prediction_score,

          mood:
            assessment.mood,

          energy:
            assessment.energy_level,

          sleep:
            assessment.sleep_hours,

          stress:
            assessment.stress_level,
        })
      );

  /*
   * Latest assessment.
   */
  const latestAssessment =
    assessments.length > 0
      ? assessments[0]
      : null;

  /*
   * Previous assessment.
   */
  const previousAssessment =
    assessments.length > 1
      ? assessments[1]
      : null;

  /*
   * Calculate current trend.
   */
  let trend =
    "Not enough data";

  if (
    latestAssessment &&
    previousAssessment
  ) {
    const difference =
      latestAssessment.prediction_score -
      previousAssessment.prediction_score;

    if (difference >= 10) {
      trend = "Increasing";
    } else if (
      difference <= -10
    ) {
      trend = "Improving";
    } else {
      trend = "Stable";
    }
  }

  return (
    <div className="dashboard-page">

      {/* =================================
          MOBILE MENU
      ================================= */}

      <button
        className="mobile-menu-button"
        onClick={() =>
          setSidebarOpen(true)
        }
        aria-label="Open navigation"
      >
        <Menu size={22} />
      </button>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() =>
            setSidebarOpen(false)
          }
        />
      )}

      {/* =================================
          SIDEBAR
      ================================= */}

      <aside
        className={`dashboard-sidebar ${
          sidebarOpen
            ? "sidebar-open"
            : ""
        }`}
      >

        <div className="sidebar-top">

          {/* Brand */}
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

          {/* Navigation */}
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
              className="sidebar-item"
              onClick={() =>
                setSidebarOpen(false)
              }
            >
              <ClipboardCheck
                size={19}
              />

              <span>
                Daily Check-In
              </span>
            </Link>

            <Link
              to="/progress"
              className="sidebar-item active"
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

        {/* Sidebar bottom */}
        <div className="sidebar-bottom">

          {/* Settings */}
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

          {/* GLOBAL DARK MODE */}
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

          {/* Logout */}
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

      {/* =================================
          MAIN CONTENT
      ================================= */}

      <main className="dashboard-main">

        {/* Header */}
        <header className="dashboard-header">

          <div>

            <p className="dashboard-eyebrow">
              Your wellbeing journey
            </p>

            <h1>
              Your Progress
            </h1>

            <p className="dashboard-subtitle">
              See how your wellbeing patterns
              have changed over time.
            </p>

          </div>

          {/* Refresh */}
          <button
            className="refresh-button"
            type="button"
            onClick={fetchHistory}
            aria-label="Refresh progress"
          >
            <RefreshCw size={18} />
          </button>

        </header>

        {/* =================================
            LOADING
        ================================= */}

        {loading && (
          <div className="progress-empty-state">

            <Activity size={32} />

            <h2>
              Loading your progress...
            </h2>

            <p>
              We're retrieving your wellbeing
              history.
            </p>

          </div>
        )}

        {/* =================================
            ERROR
        ================================= */}

        {!loading &&
          error && (
            <div className="checkin-error">

              <Activity size={20} />

              <span>
                {error}
              </span>

            </div>
          )}

        {/* =================================
            EMPTY STATE
        ================================= */}

        {!loading &&
          !error &&
          assessments.length === 0 && (
            <div className="progress-empty-state">

              <div className="empty-icon">
                <Heart size={32} />
              </div>

              <h2>
                Your progress starts here
              </h2>

              <p>
                Complete your first daily
                check-in to begin building
                your wellbeing history.
              </p>

              <Link
                to="/check-in"
                className="primary-dashboard-button"
              >
                Start a check-in
              </Link>

            </div>
          )}

        {/* =================================
            DATA
        ================================= */}

        {!loading &&
          !error &&
          assessments.length > 0 && (
            <>

              {/* =================================
                  OVERVIEW
              ================================= */}

              <section className="progress-overview">

                {/* Check-ins */}
                <div className="progress-card">

                  <div className="progress-card-icon">
                    <ClipboardCheck
                      size={20}
                    />
                  </div>

                  <div>

                    <span>
                      Check-ins
                    </span>

                    <strong>
                      {assessments.length}
                    </strong>

                    <small>
                      Total completed
                    </small>

                  </div>

                </div>

                {/* Trend */}
                <div className="progress-card">

                  <div className="progress-card-icon">
                    <TrendingUp
                      size={20}
                    />
                  </div>

                  <div>

                    <span>
                      Current trend
                    </span>

                    <strong>
                      {trend}
                    </strong>

                    <small>
                      Based on recent
                      assessments
                    </small>

                  </div>

                </div>

                {/* Latest risk */}
                {latestAssessment && (
                  <div className="progress-card">

                    <div className="progress-card-icon">
                      <Brain size={20} />
                    </div>

                    <div>

                      <span>
                        Latest risk
                      </span>

                      <strong
                        className={getRiskClass(
                          latestAssessment
                            .prediction_score
                        )}
                      >
                        {
                          latestAssessment
                            .prediction_score
                        }%
                      </strong>

                      <small>
                        {
                          getRiskLevel(
                            latestAssessment
                              .prediction_score
                          )
                        }{" "}
                        level
                      </small>

                    </div>

                  </div>
                )}

              </section>

              {/* =================================
                  RISK CHART
              ================================= */}

              <section className="progress-section">

                <div className="progress-section-heading">

                  <div>

                    <p className="dashboard-eyebrow">
                      Recent pattern
                    </p>

                    <h2>
                      Risk score over time
                    </h2>

                  </div>

                </div>

                <div className="chart-card">

                  <ResponsiveContainer
                    width="100%"
                    height={300}
                  >

                    <LineChart
                      data={chartData}
                      margin={{
                        top: 10,
                        right: 20,
                        left: 0,
                        bottom: 5,
                      }}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                      />

                      <XAxis
                        dataKey="date"
                      />

                      <YAxis
                        domain={[
                          0,
                          100,
                        ]}
                        tickFormatter={(
                          value
                        ) =>
                          `${value}%`
                        }
                      />

                      <Tooltip
                        formatter={(
                          value
                        ) =>
                          `${value}%`
                        }
                      />

                      <Line
                        type="monotone"
                        dataKey="risk"
                        name="Risk score"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        dot={{
                          r: 5,
                        }}
                        activeDot={{
                          r: 7,
                        }}
                      />

                    </LineChart>

                  </ResponsiveContainer>

                </div>

              </section>

              {/* =================================
                  MOOD + ENERGY
              ================================= */}

              <section className="progress-section">

                <div className="progress-section-heading">

                  <div>

                    <p className="dashboard-eyebrow">
                      Emotional wellbeing
                    </p>

                    <h2>
                      Mood & Energy
                    </h2>

                  </div>

                </div>

                <div className="chart-card">

                  <ResponsiveContainer
                    width="100%"
                    height={300}
                  >

                    <LineChart
                      data={chartData}
                      margin={{
                        top: 10,
                        right: 20,
                        left: 0,
                        bottom: 5,
                      }}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                      />

                      <XAxis
                        dataKey="date"
                      />

                      <YAxis
                        domain={[
                          1,
                          5,
                        ]}
                        ticks={[
                          1,
                          2,
                          3,
                          4,
                          5,
                        ]}
                      />

                      <Tooltip />

                      <Legend />

                      <Line
                        type="monotone"
                        dataKey="mood"
                        name="Mood"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        dot={{
                          r: 4,
                        }}
                      />

                      <Line
                        type="monotone"
                        dataKey="energy"
                        name="Energy"
                        stroke="#60a5fa"
                        strokeWidth={3}
                        dot={{
                          r: 4,
                        }}
                      />

                    </LineChart>

                  </ResponsiveContainer>

                </div>

              </section>

              {/* =================================
                  SLEEP + STRESS
              ================================= */}

              <section className="progress-section">

                <div className="progress-section-heading">

                  <div>

                    <p className="dashboard-eyebrow">
                      Daily habits
                    </p>

                    <h2>
                      Sleep & Stress
                    </h2>

                  </div>

                </div>

                <div className="chart-card">

                  <ResponsiveContainer
                    width="100%"
                    height={300}
                  >

                    <LineChart
                      data={chartData}
                      margin={{
                        top: 10,
                        right: 20,
                        left: 0,
                        bottom: 5,
                      }}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                      />

                      <XAxis
                        dataKey="date"
                      />

                      <YAxis />

                      <Tooltip />

                      <Legend />

                      <Line
                        type="monotone"
                        dataKey="sleep"
                        name="Sleep hours"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        dot={{
                          r: 4,
                        }}
                      />

                      <Line
                        type="monotone"
                        dataKey="stress"
                        name="Stress"
                        stroke="#f59e0b"
                        strokeWidth={3}
                        dot={{
                          r: 4,
                        }}
                      />

                    </LineChart>

                  </ResponsiveContainer>

                </div>

              </section>

              {/* =================================
                  LATEST WELLBEING
              ================================= */}

              {latestAssessment && (
                <section className="progress-section">

                  <div className="progress-section-heading">

                    <div>

                      <p className="dashboard-eyebrow">
                        Latest assessment
                      </p>

                      <h2>
                        Wellbeing indicators
                      </h2>

                    </div>

                    <span>
                      {formatDate(
                        latestAssessment
                          .created_at
                      )}
                    </span>

                  </div>

                  <div className="indicator-grid">

                    <Indicator
                      label="Mood"
                      value={
                        latestAssessment
                          .mood
                      }
                      icon={
                        <Heart size={19} />
                      }
                    />

                    <Indicator
                      label="Sleep quality"
                      value={
                        latestAssessment
                          .sleep_quality
                      }
                      icon={
                        <Moon size={19} />
                      }
                    />

                    <Indicator
                      label="Energy"
                      value={
                        latestAssessment
                          .energy_level
                      }
                      icon={
                        <Activity size={19} />
                      }
                    />

                    <Indicator
                      label="Stress"
                      value={
                        latestAssessment
                          .stress_level
                      }
                      icon={
                        <Brain size={19} />
                      }
                      inverse
                    />

                  </div>

                </section>
              )}

              {/* =================================
                  ASSESSMENT HISTORY
              ================================= */}

              <section className="progress-section">

                <div className="progress-section-heading">

                  <div>

                    <p className="dashboard-eyebrow">
                      Your records
                    </p>

                    <h2>
                      Assessment history
                    </h2>

                  </div>

                </div>

                <div className="assessment-history">

                  {assessments.map(
                    (assessment) => (
                      <div
                        className="assessment-history-row"
                        key={
                          assessment.id
                        }
                      >

                        <div>

                          <strong>
                            {new Date(
                              assessment.created_at
                            ).toLocaleDateString(
                              "en-IN",
                              {
                                day: "numeric",
                                month: "short",
                                year: "numeric",
                              }
                            )}
                          </strong>

                          <span>
                            Mood{" "}
                            {
                              assessment
                                .mood
                            }
                            /5
                            {" • "}
                            Sleep{" "}
                            {
                              assessment
                                .sleep_hours
                            }
                            h
                          </span>

                        </div>

                        <div
                          className={`history-risk ${getRiskClass(
                            assessment
                              .prediction_score
                          )}`}
                        >

                          {
                            assessment
                              .prediction_score
                          }%

                          <span>
                            {
                              getRiskLevel(
                                assessment
                                  .prediction_score
                              )
                            }
                          </span>

                        </div>

                      </div>
                    )
                  )}

                </div>

              </section>

              <p className="assessment-disclaimer">
                Clarity shows patterns in your
                self-reported wellbeing data.
                These indicators are intended for
                awareness and are not a medical
                diagnosis.
              </p>

            </>
          )}

      </main>

    </div>
  );
}

interface IndicatorProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  inverse?: boolean;
}

function Indicator({
  label,
  value,
  icon,
  inverse = false,
}: IndicatorProps) {
  return (
    <div className="indicator-card">

      <div className="indicator-icon">
        {icon}
      </div>

      <div className="indicator-content">

        <span>
          {label}
        </span>

        <strong>
          {value}/5
        </strong>

        <div className="indicator-bar">

          <div
            className={
              inverse
                ? "indicator-fill indicator-inverse"
                : "indicator-fill"
            }
            style={{
              width:
                `${value * 20}%`,
            }}
          />

        </div>

      </div>

    </div>
  );
}

export default Progress;