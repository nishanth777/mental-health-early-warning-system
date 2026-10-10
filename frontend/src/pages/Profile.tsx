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
  Download,
  FileText,
  AlertCircle,
  CheckCircle2,
  Trash2,
  XCircle,
} from "lucide-react";

import { useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import api from "../services/api";

import "../App.css";

function Profile() {
  const { user, logout } = useAuth();

  const {
    darkMode,
    toggleDarkMode,
  } = useTheme();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [exportingData, setExportingData] = useState(false);
  const [exportingReport, setExportingReport] = useState(false);
  const [exportMessage, setExportMessage] = useState("");
  const [exportError, setExportError] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState("");
  const [deletingAccount, setDeletingAccount] = useState(false);
  const [deleteMessage, setDeleteMessage] = useState("");
  const [deleteError, setDeleteError] = useState(false);

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join("");
  };

  const handleLogout = () => {
    logout();
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmation !== "DELETE") {
      setDeleteError(true);
      setDeleteMessage('Type DELETE exactly to confirm account deletion.');
      return;
    }

    setDeletingAccount(true);
    setDeleteMessage("");
    setDeleteError(false);

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setDeleteError(true);
        setDeleteMessage("Your session has expired. Please sign in again.");
        logout();
        return;
      }

      await api.delete("/auth/delete-account", {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Close the dialog and clear local authentication after server confirms deletion.
      setShowDeleteDialog(false);
      localStorage.removeItem("access_token");
      logout();
    } catch (error: any) {
      console.error("Account deletion failed:", error);
      setDeleteError(true);

      if (error.response?.status === 401) {
        setDeleteMessage("Your session has expired. Please sign in again.");
        logout();
      } else if (error.response?.status === 404) {
        setDeleteMessage("Your account could not be found. Please sign in again.");
      } else {
        setDeleteMessage(
          error.response?.data?.error ||
          "Unable to delete your account. Please try again."
        );
      }
    } finally {
      setDeletingAccount(false);
    }
  };

  const handleDownloadReport = async () => {
    setExportingReport(true);
    setExportMessage("");
    setExportError(false);

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setExportError(true);
        setExportMessage("Your session has expired. Please sign in again.");
        logout();
        return;
      }

      const response = await api.get("/auth/export-report", {
        responseType: "blob",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const contentDisposition = response.headers?.["content-disposition"];
      const filenameMatch =
        typeof contentDisposition === "string"
          ? contentDisposition.match(/filename="?([^";]+)"?/i)
          : null;

      const filename =
        filenameMatch?.[1] ||
        `my_wellbeing_report_${new Date().toISOString().slice(0, 10)}.pdf`;

      const blobUrl = window.URL.createObjectURL(
        new Blob([response.data], { type: "application/pdf" })
      );

      const downloadLink = document.createElement("a");
      downloadLink.href = blobUrl;
      downloadLink.download = filename;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      downloadLink.remove();
      window.URL.revokeObjectURL(blobUrl);

      setExportMessage("Your PDF report has been downloaded successfully.");
    } catch (error: any) {
      console.error("PDF report export failed:", error);
      setExportError(true);

      if (error.response?.status === 401) {
        setExportMessage("Your session has expired. Please sign in again.");
        logout();
      } else if (error.response?.status === 404) {
        setExportMessage("Your account could not be found. Please sign in again.");
      } else {
        setExportMessage("Unable to download your PDF report. Please try again.");
      }
    } finally {
      setExportingReport(false);
    }
  };

  const handleDownloadData = async () => {
    setExportingData(true);
    setExportMessage("");
    setExportError(false);

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setExportError(true);
        setExportMessage("Your session has expired. Please sign in again.");
        logout();
        return;
      }

      const response = await api.get("/auth/export-data", {
        responseType: "blob",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const contentDisposition = response.headers?.["content-disposition"];
      const filenameMatch =
        typeof contentDisposition === "string"
          ? contentDisposition.match(/filename="?([^";]+)"?/i)
          : null;

      const filename =
        filenameMatch?.[1] ||
        `my_wellbeing_data_${new Date().toISOString().slice(0, 10)}.json`;

      const blobUrl = window.URL.createObjectURL(
        new Blob([response.data], { type: "application/json" })
      );

      const downloadLink = document.createElement("a");
      downloadLink.href = blobUrl;
      downloadLink.download = filename;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      downloadLink.remove();
      window.URL.revokeObjectURL(blobUrl);

      setExportMessage("Your data export has been downloaded successfully.");
    } catch (error: any) {
      console.error("Data export failed:", error);

      setExportError(true);

      if (error.response?.status === 401) {
        setExportMessage("Your session has expired. Please sign in again.");
        logout();
      } else if (error.response?.status === 404) {
        setExportMessage("Your account could not be found. Please sign in again.");
      } else {
        setExportMessage("Unable to download your data. Please try again.");
      }
    } finally {
      setExportingData(false);
    }
  };

  return (
    <div className="dashboard-page">
      {/* Mobile menu */}
      <button
        className="mobile-menu-button"
        onClick={() => setSidebarOpen(true)}
        aria-label="Open navigation"
      >
        <Menu size={22} />
      </button>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`dashboard-sidebar ${
          sidebarOpen ? "sidebar-open" : ""
        }`}
      >
        <div className="sidebar-top">
          <div className="sidebar-brand">
            <span>Clarity</span>

            <button
              className="mobile-close-button"
              onClick={() => setSidebarOpen(false)}
              aria-label="Close navigation"
            >
              <X size={20} />
            </button>
          </div>

          <nav className="sidebar-navigation">
            <Link
              to="/dashboard"
              className="sidebar-item"
              onClick={() => setSidebarOpen(false)}
            >
              <Home size={19} />
              <span>Dashboard</span>
            </Link>

            <Link
              to="/check-in"
              className="sidebar-item"
              onClick={() => setSidebarOpen(false)}
            >
              <ClipboardCheck size={19} />
              <span>Daily Check-In</span>
            </Link>

            <Link
              to="/progress"
              className="sidebar-item"
              onClick={() => setSidebarOpen(false)}
            >
              <TrendingUp size={19} />
              <span>Progress</span>
            </Link>

            <Link
              to="/profile"
              className="sidebar-item active"
              onClick={() => setSidebarOpen(false)}
            >
              <User size={19} />
              <span>Profile</span>
            </Link>
          </nav>
        </div>

        {/* Sidebar bottom */}
        <div className="sidebar-bottom">
          <Link
            to="/settings"
            className="sidebar-item"
            onClick={() => setSidebarOpen(false)}
          >
            <Settings size={19} />
            <span>Settings</span>
          </Link>

          <button
            className="sidebar-item sidebar-button"
            type="button"
            onClick={toggleDarkMode}
          >
            <Moon size={19} />
            <span>{darkMode ? "Light Mode" : "Dark Mode"}</span>
          </button>

          <button
            className="sidebar-item sidebar-button logout-item"
            type="button"
            onClick={handleLogout}
          >
            <LogOut size={19} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="dashboard-main">
        {/* Header */}
        <header className="dashboard-header">
          <div>
            <p className="dashboard-eyebrow">Your account</p>
            <h1>Profile</h1>
            <p className="dashboard-subtitle">
              Manage your Clarity account information.
            </p>
          </div>
        </header>

        {/* Profile content */}
        <section className="profile-layout">
          {/* Identity card */}
          <div className="profile-card profile-identity-card">
            <div className="profile-avatar">
              {user ? getInitials(user.full_name) : "U"}
            </div>

            <h2>{user?.full_name || "User"}</h2>
            <p>{user?.email || "Email unavailable"}</p>

            <div className="profile-status">
              <ShieldCheck size={16} />
              <span>Account verified</span>
            </div>
          </div>

          {/* Personal information */}
          <div className="profile-card">
            <div className="profile-card-heading">
              <div>
                <p className="dashboard-eyebrow">Account details</p>
                <h2>Personal information</h2>
              </div>
              <UserRound size={22} />
            </div>

            <div className="profile-information">
              <div className="profile-information-row">
                <div className="profile-information-icon">
                  <UserRound size={18} />
                </div>
                <div>
                  <span>Full name</span>
                  <strong>{user?.full_name || "Not available"}</strong>
                </div>
              </div>

              <div className="profile-information-row">
                <div className="profile-information-icon">
                  <Mail size={18} />
                </div>
                <div>
                  <span>Email address</span>
                  <strong>{user?.email || "Not available"}</strong>
                </div>
              </div>
            </div>
          </div>

          {/* Privacy */}
          <div className="profile-card profile-privacy-card">
            <div className="profile-card-heading">
              <div>
                <p className="dashboard-eyebrow">Privacy</p>
                <h2>Your wellbeing data</h2>
              </div>
              <ShieldCheck size={22} />
            </div>

            <p>
              Your check-ins are associated with your account so Clarity can
              show your personal wellbeing patterns and progress over time.
            </p>

            <p>
              Clarity is designed for awareness and preventive wellbeing
              support. Its risk indicators are not medical diagnoses.
            </p>
          </div>

          {/* Account and data management */}
          <div className="profile-card">
            <div className="profile-card-heading">
              <div>
                <p className="dashboard-eyebrow">Account management</p>
                <h2>Manage your data</h2>
              </div>
              <Download size={22} />
            </div>

            <p>
              Download a copy of your account information and assessment history,
              either as structured data or as a formatted PDF report.
            </p>

            <button
              className="profile-logout-button"
              type="button"
              onClick={handleDownloadData}
              disabled={exportingData}
            >
              <Download size={18} />
              {exportingData ? "Preparing download..." : "Download My Data"}
            </button>

            <button
              className="profile-logout-button"
              type="button"
              onClick={handleDownloadReport}
              disabled={exportingReport}
              style={{ marginTop: "12px" }}
            >
              <FileText size={18} />
              {exportingReport ? "Preparing report..." : "Download My Report (PDF)"}
            </button>

            {exportMessage && (
              <p
                role="status"
                aria-live="polite"
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: "8px",
                  marginTop: "12px",
                  color: exportError ? "var(--danger-color, #dc2626)" : "var(--success-color, #15803d)",
                }}
              >
                {exportError ? (
                  <AlertCircle size={18} />
                ) : (
                  <CheckCircle2 size={18} />
                )}
                <span>{exportMessage}</span>
              </p>
            )}

          </div>

          {/* Danger zone */}
          <div className="profile-card profile-danger-card">
            <div className="profile-card-heading">
              <div>
                <p className="dashboard-eyebrow">Danger zone</p>
                <h2>Delete My Account</h2>
              </div>
              <Trash2 size={22} />
            </div>

            <p>
              Permanently delete your account and all associated assessment
              history. This action cannot be undone.
            </p>

            <button
              className="profile-delete-button"
              type="button"
              onClick={() => {
                setDeleteConfirmation("");
                setDeleteMessage("");
                setDeleteError(false);
                setShowDeleteDialog(true);
              }}
              disabled={deletingAccount}
            >
              <Trash2 size={18} />
              Delete My Account
            </button>

            {deleteMessage && !showDeleteDialog && (
              <p role="alert" className={deleteError ? "profile-delete-error" : ""}>
                {deleteMessage}
              </p>
            )}
          </div>

          {/* Sign out */}
          <div className="profile-card profile-logout-card">
            <div>
              <h2>Sign out</h2>
              <p>Sign out of your Clarity account on this device.</p>
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
        {showDeleteDialog && (
          <div
            className="profile-modal-backdrop"
            role="presentation"
            onMouseDown={(event) => {
              if (event.target === event.currentTarget && !deletingAccount) {
                setShowDeleteDialog(false);
              }
            }}
          >
            <section
              className="profile-delete-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="delete-account-title"
              aria-describedby="delete-account-description"
            >
              <div className="profile-delete-modal-icon">
                <AlertCircle size={26} />
              </div>

              <button
                type="button"
                className="profile-delete-modal-close"
                aria-label="Close confirmation"
                disabled={deletingAccount}
                onClick={() => setShowDeleteDialog(false)}
              >
                <XCircle size={21} />
              </button>

              <p className="dashboard-eyebrow">Permanent action</p>
              <h2 id="delete-account-title">Delete your account?</h2>

              <p id="delete-account-description">
                This permanently deletes your account and all saved assessments.
                Your downloaded JSON and PDF files, if any, will not be deleted
                from your device.
              </p>

              <label htmlFor="delete-account-confirmation">
                Type <strong>DELETE</strong> to confirm
              </label>

              <input
                id="delete-account-confirmation"
                type="text"
                value={deleteConfirmation}
                onChange={(event) => setDeleteConfirmation(event.target.value)}
                placeholder="Type DELETE"
                autoComplete="off"
                disabled={deletingAccount}
              />

              {deleteMessage && (
                <p role="alert" className="profile-delete-error">
                  {deleteMessage}
                </p>
              )}

              <div className="profile-delete-modal-actions">
                <button
                  type="button"
                  className="profile-delete-cancel"
                  onClick={() => setShowDeleteDialog(false)}
                  disabled={deletingAccount}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="profile-delete-confirm"
                  onClick={handleDeleteAccount}
                  disabled={deletingAccount || deleteConfirmation !== "DELETE"}
                >
                  <Trash2 size={17} />
                  {deletingAccount ? "Deleting..." : "Permanently Delete"}
                </button>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}

export default Profile;
