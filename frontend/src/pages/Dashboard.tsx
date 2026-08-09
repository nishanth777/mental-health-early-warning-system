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
  Battery,
  Activity,
  AlertCircle,
  RefreshCw,
} from "lucide-react";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

import api from "../services/api";

import "../App.css";

interface DashboardData {
  total_assessments: number;
  latest_risk_score: number;
  latest_risk_level: string;
  trend: string;
  average_sleep: number;
  average_stress: number;
  average_mood: number;
  average_energy: number;
}

function Dashboard() {
  const { user, logout } = useAuth();

  /*
   * Global theme state.
   *
   * This is shared by Dashboard,
   * Progress, Profile, Settings,
   * and Daily Check-In.
   */
  const {
    darkMode,
    toggleDarkMode,
  } = useTheme();

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const [dashboardData, setDashboardData] =
    useState<DashboardData | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  /*
   * Determine greeting.
   */
  const currentHour =
    new Date().getHours();

  let greeting = "Good morning";

  if (
    currentHour >= 12 &&
    currentHour < 18
  ) {
    greeting = "Good afternoon";
  } else if (currentHour >= 18) {
    greeting = "Good evening";
  }

  /*
   * Fetch dashboard data.
   */
  useEffect(() => {
    const fetchDashboard = async () => {
      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!token) {
        setError(
          "Your session has expired. Please log in again."
        );

        setLoading(false);

        return;
      }

      try {
        setLoading(true);
        setError("");

        const response =
          await api.get(
            "/dashboard/",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          );

        setDashboardData(
          response.data
        );
      } catch (err: any) {
        console.error(
          "Dashboard error:",
          err
        );

        if (
          err.response?.status === 404
        ) {
          setDashboardData(null);
          setError("");
        } else if (
          err.response?.status === 401
        ) {
          logout();
        } else {
          setError(
            "Unable to load your wellbeing data. Please try again."
          );
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [logout]);

  /*
   * Risk level styling.
   */
  const getRiskClass = (
    level?: string
  ) => {
    if (!level) return "";

    switch (
      level.toLowerCase()
    ) {
      case "low":
        return "risk-low";

      case "moderate":
        return "risk-moderate";

      case "high":
        return "risk-high";

      default:
        return "";
    }
  };

  /*
   * Trend styling.
   */
  const getTrendClass = (
    trend?: string
  ) => {
    if (!trend) return "";

    switch (
      trend.toLowerCase()
    ) {
      case "improving":
        return "trend-improving";

      case "declining":
        return "trend-declining";

      case "stable":
        return "trend-stable";

      default:
        return "";
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

      {/* Mobile overlay */}
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
              className="sidebar-item active"
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

          {/* Global Dark Mode */}
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

      {/* Main content */}
      <main className="dashboard-main">

        {/* Header */}
        <header className="dashboard-header">

          <div>

            <p className="dashboard-eyebrow">
              Your wellbeing overview
            </p>

            <h1>
              {greeting},{" "}
              {user?.full_name ||
                "there"} 🌿
            </h1>

            <p className="dashboard-subtitle">
              Here's a gentle look at how
              you've been doing.
            </p>

          </div>

          <button
            className="refresh-button"
            type="button"
            onClick={() =>
              window.location.reload()
            }
            aria-label="Refresh dashboard"
          >
            <RefreshCw size={18} />
          </button>

        </header>

        {/* Loading */}
        {loading && (
          <section className="dashboard-loading">

            <div className="loading-spinner">
              <RefreshCw size={24} />
            </div>

            <p>
              Gathering your wellbeing
              data...
            </p>

          </section>
        )}

        {/* Error */}
        {!loading && error && (
          <section className="dashboard-error">

            <AlertCircle size={24} />

            <div>

              <h3>
                Something went wrong
              </h3>

              <p>
                {error}
              </p>

            </div>

          </section>
        )}

        {/* No assessments */}
        {!loading &&
          !error &&
          !dashboardData && (
            <section className="empty-dashboard">

              <div className="empty-dashboard-icon">
                <Heart size={30} />
              </div>

              <h2>
                Your Clarity journey
                starts here
              </h2>

              <p>
                Complete your first
                wellbeing assessment to
                start understanding your
                patterns.
              </p>

              <Link
                to="/check-in"
                className="primary-dashboard-button"
              >
                Start your first
                check-in
              </Link>

            </section>
          )}

        {/* Dashboard data */}
        {!loading &&
          dashboardData && (
            <>

              {/* Assessment summary */}
              <div className="assessment-summary">

                <div>

                  <span className="summary-label">
                    Assessments completed
                  </span>

                  <strong>
                    {
                      dashboardData
                        .total_assessments
                    }
                  </strong>

                </div>

                <div className="summary-trend">

                  <TrendingUp
                    size={18}
                  />

                  <span
                    className={getTrendClass(
                      dashboardData.trend
                    )}
                  >
                    {
                      dashboardData.trend
                    }
                  </span>

                </div>

              </div>

              {/* Quick stats */}
              <section className="stats-grid">

                {/* Mood */}
                <article className="stat-card">

                  <div className="stat-icon mood-icon">
                    <Heart size={20} />
                  </div>

                  <div className="stat-content">

                    <span>
                      Mood
                    </span>

                    <strong>
                      {
                        dashboardData
                          .average_mood
                      }

                      <small>
                        /5
                      </small>
                    </strong>

                    <p>
                      Average mood
                    </p>

                  </div>

                </article>

                {/* Sleep */}
                <article className="stat-card">

                  <div className="stat-icon sleep-icon">
                    <Moon size={20} />
                  </div>

                  <div className="stat-content">

                    <span>
                      Sleep
                    </span>

                    <strong>
                      {
                        dashboardData
                          .average_sleep
                      }

                      <small>
                        {" "}
                        hrs
                      </small>
                    </strong>

                    <p>
                      Average sleep
                    </p>

                  </div>

                </article>

                {/* Energy */}
                <article className="stat-card">

                  <div className="stat-icon energy-icon">
                    <Battery
                      size={20}
                    />
                  </div>

                  <div className="stat-content">

                    <span>
                      Energy
                    </span>

                    <strong>
                      {
                        dashboardData
                          .average_energy
                      }

                      <small>
                        /5
                      </small>
                    </strong>

                    <p>
                      Average energy
                    </p>

                  </div>

                </article>

                {/* Stress */}
                <article className="stat-card">

                  <div className="stat-icon stress-icon">
                    <Brain size={20} />
                  </div>

                  <div className="stat-content">

                    <span>
                      Stress
                    </span>

                    <strong>
                      {
                        dashboardData
                          .average_stress
                      }

                      <small>
                        /5
                      </small>
                    </strong>

                    <p>
                      Average stress
                    </p>

                  </div>

                </article>

              </section>

              {/* Lower dashboard */}
              <section className="dashboard-lower-grid">

                {/* Risk */}
                <article className="risk-card">

                  <div className="section-card-header">

                    <div>

                      <span className="card-eyebrow">
                        Latest assessment
                      </span>

                      <h2>
                        Wellbeing status
                      </h2>

                    </div>

                    <Activity
                      size={21}
                    />

                  </div>

                  <div className="risk-content">

                    <div
                      className={`risk-circle ${getRiskClass(
                        dashboardData
                          .latest_risk_level
                      )}`}
                    >

                      <strong>
                        {
                          dashboardData
                            .latest_risk_score
                        }%
                      </strong>

                      <span>
                        risk score
                      </span>

                    </div>

                    <div className="risk-details">

                      <span className="risk-label">
                        Current level
                      </span>

                      <strong
                        className={getRiskClass(
                          dashboardData
                            .latest_risk_level
                        )}
                      >
                        {
                          dashboardData
                            .latest_risk_level
                        }
                      </strong>

                      <p>
                        This is an awareness
                        indicator based on your
                        latest assessment, not a
                        medical diagnosis.
                      </p>

                    </div>

                  </div>

                </article>

                {/* Trend */}
                <article className="trend-card">

                  <div className="section-card-header">

                    <div>

                      <span className="card-eyebrow">
                        Recent pattern
                      </span>

                      <h2>
                        Your trend
                      </h2>

                    </div>

                    <TrendingUp
                      size={21}
                    />

                  </div>

                  <div className="trend-content">

                    <div
                      className={`trend-badge ${getTrendClass(
                        dashboardData.trend
                      )}`}
                    >

                      <TrendingUp
                        size={22}
                      />

                      <span>
                        {
                          dashboardData
                            .trend
                        }
                      </span>

                    </div>

                    <p>
                      Your latest assessment
                      is being compared with
                      your previous one to
                      identify changes over
                      time.
                    </p>

                  </div>

                </article>

              </section>

              {/* Insight */}
              <section className="insight-card">

                <div className="insight-icon">
                  <Heart size={21} />
                </div>

                <div>

                  <span>
                    Clarity insight
                  </span>

                  <h2>
                    Keep checking in with
                    yourself.
                  </h2>

                  <p>
                    Regular check-ins help
                    Clarity understand changes
                    in your wellbeing patterns
                    over time.
                  </p>

                </div>

              </section>

            </>
          )}

      </main>
    </div>
  );
}

export default Dashboard;