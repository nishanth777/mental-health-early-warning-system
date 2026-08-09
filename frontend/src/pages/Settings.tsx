import {
  Home,
  ClipboardCheck,
  TrendingUp,
  User,
  Settings as SettingsIcon,
  Moon,
  Sun,
  LogOut,
  Menu,
  X,
  ShieldCheck,
  Bell,
  Palette,
} from "lucide-react";

import { useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

import "../App.css";

function Settings() {
  const { logout } =
    useAuth();

  const {
    darkMode,
    toggleDarkMode,
  } = useTheme();

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const [notifications, setNotifications] =
    useState(true);

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

        <div className="sidebar-bottom">

          <Link
            to="/settings"
            className="sidebar-item active"
            onClick={() =>
              setSidebarOpen(false)
            }
          >
            <SettingsIcon
              size={19}
            />

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
      <main className="dashboard-main settings-main">

        <header className="dashboard-header">

          <div>

            <p className="dashboard-eyebrow">
              Personal preferences
            </p>

            <h1>
              Settings
            </h1>

            <p className="dashboard-subtitle">
              Customize your Clarity
              experience.
            </p>

          </div>

        </header>

        <section className="settings-layout">

          {/* Appearance */}
          <div className="settings-card">

            <div className="settings-card-header">

              <div className="settings-card-icon">
                <Palette size={21} />
              </div>

              <div>

                <p className="dashboard-eyebrow">
                  Appearance
                </p>

                <h2>
                  Display preferences
                </h2>

              </div>

            </div>

            <div className="settings-option">

              <div className="settings-option-icon">

                {darkMode ? (
                  <Moon size={20} />
                ) : (
                  <Sun size={20} />
                )}

              </div>

              <div className="settings-option-content">

                <strong>
                  Dark mode
                </strong>

                <span>
                  Use a darker appearance
                  throughout Clarity.
                </span>

              </div>

              <button
                type="button"
                className={
                  darkMode
                    ? "settings-toggle active"
                    : "settings-toggle"
                }
                onClick={
                  toggleDarkMode
                }
                aria-label="Toggle dark mode"
                aria-pressed={darkMode}
              >
                <span />
              </button>

            </div>

          </div>

          {/* Notifications */}
          <div className="settings-card">

            <div className="settings-card-header">

              <div className="settings-card-icon">
                <Bell size={21} />
              </div>

              <div>

                <p className="dashboard-eyebrow">
                  Notifications
                </p>

                <h2>
                  Reminder preferences
                </h2>

              </div>

            </div>

            <div className="settings-option">

              <div className="settings-option-icon">
                <Bell size={20} />
              </div>

              <div className="settings-option-content">

                <strong>
                  Wellbeing reminders
                </strong>

                <span>
                  Receive reminders to
                  complete your daily
                  check-in.
                </span>

              </div>

              <button
                type="button"
                className={
                  notifications
                    ? "settings-toggle active"
                    : "settings-toggle"
                }
                onClick={() =>
                  setNotifications(
                    (current) =>
                      !current
                  )
                }
                aria-label="Toggle notifications"
                aria-pressed={
                  notifications
                }
              >
                <span />
              </button>

            </div>

            <p className="settings-note">
              Notification delivery will
              be connected when the reminder
              system is implemented.
            </p>

          </div>

          {/* Privacy */}
          <div className="settings-card">

            <div className="settings-card-header">

              <div className="settings-card-icon">
                <ShieldCheck
                  size={21}
                />
              </div>

              <div>

                <p className="dashboard-eyebrow">
                  Privacy
                </p>

                <h2>
                  Your wellbeing data
                </h2>

              </div>

            </div>

            <div className="settings-info">

              <p>
                Your assessment responses are
                associated with your account so
                Clarity can provide personalized
                progress information.
              </p>

              <p>
                Clarity is an awareness and
                preventive wellbeing system.
                Its risk scores are not medical
                diagnoses.
              </p>

            </div>

          </div>

          {/* Account */}
          <div className="settings-card settings-account-card">

            <div>

              <p className="dashboard-eyebrow">
                Account
              </p>

              <h2>
                Sign out
              </h2>

              <p>
                Sign out of your Clarity
                account on this device.
              </p>

            </div>

            <button
              className="settings-logout-button"
              type="button"
              onClick={logout}
            >
              <LogOut size={18} />
              Sign out
            </button>

          </div>

          <p className="assessment-disclaimer">
            Clarity is designed to support
            awareness and wellbeing. It does
            not diagnose mental health
            conditions.
          </p>

        </section>

      </main>

    </div>
  );
}

export default Settings;