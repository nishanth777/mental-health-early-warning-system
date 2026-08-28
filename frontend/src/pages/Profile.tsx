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
  Mail,
  UserRound,
  ShieldCheck,
} from "lucide-react";

import { useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

import "../App.css";

function Profile() {
  const { user, logout } = useAuth();

  const {
    darkMode,
    toggleDarkMode,
  } = useTheme();

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  const getInitials = (
    name: string
  ) => {
    return name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map(
        (part) =>
          part
            .charAt(0)
            .toUpperCase()
      )
      .join("");
  };

  const handleLogout = () => {
    logout();
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
              className="sidebar-item active"
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

          {/* Dark Mode */}
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
            onClick={handleLogout}
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
              Your account
            </p>

            <h1>
              Profile
            </h1>

            <p className="dashboard-subtitle">
              Manage your Clarity account
              information.
            </p>

          </div>

        </header>

        {/* Profile content */}
        <section className="profile-layout">

          {/* Identity card */}
          <div className="profile-card profile-identity-card">

            <div className="profile-avatar">

              {user
                ? getInitials(
                    user.full_name
                  )
                : "U"}

            </div>

            <h2>
              {user?.full_name ||
                "User"}
            </h2>

            <p>
              {user?.email ||
                "Email unavailable"}
            </p>

            <div className="profile-status">

              <ShieldCheck size={16} />

              <span>
                Account verified
              </span>

            </div>

          </div>

          {/* Personal information */}
          <div className="profile-card">

            <div className="profile-card-heading">

              <div>

                <p className="dashboard-eyebrow">
                  Account details
                </p>

                <h2>
                  Personal information
                </h2>

              </div>

              <UserRound size={22} />

            </div>

            <div className="profile-information">

              {/* Full name */}
              <div className="profile-information-row">

                <div className="profile-information-icon">
                  <UserRound
                    size={18}
                  />
                </div>

                <div>

                  <span>
                    Full name
                  </span>

                  <strong>
                    {user?.full_name ||
                      "Not available"}
                  </strong>

                </div>

              </div>

              {/* Email */}
              <div className="profile-information-row">

                <div className="profile-information-icon">
                  <Mail size={18} />
                </div>

                <div>

                  <span>
                    Email address
                  </span>

                  <strong>
                    {user?.email ||
                      "Not available"}
                  </strong>

                </div>

              </div>

            </div>

          </div>

          {/* Privacy */}
          <div className="profile-card profile-privacy-card">

            <div className="profile-card-heading">

              <div>

                <p className="dashboard-eyebrow">
                  Privacy
                </p>

                <h2>
                  Your wellbeing data
                </h2>

              </div>

              <ShieldCheck
                size={22}
              />

            </div>

            <p>
              Your check-ins are associated
              with your account so Clarity
              can show your personal wellbeing
              patterns and progress over time.
            </p>

            <p>
              Clarity is designed for
              awareness and preventive
              wellbeing support. Its risk
              indicators are not medical
              diagnoses.
            </p>

          </div>

          {/* Sign out */}
          <div className="profile-card profile-logout-card">

            <div>

              <h2>
                Sign out
              </h2>

              <p>
                Sign out of your Clarity
                account on this device.
              </p>

            </div>

            <button
              className="profile-logout-button"
              type="button"
              onClick={handleLogout}
            >
              <LogOut size={18} />
              Sign out
            </button>

          </div>

        </section>

      </main>

    </div>
  );
}

export default Profile;