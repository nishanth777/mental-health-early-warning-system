import {
  Navigate,
  Outlet,
  useLocation,
  useNavigate,
  useBlocker,
} from "react-router-dom";

import { useEffect, useState } from "react";
import { LogOut, ShieldAlert, X } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import api from "../services/api";

function ProtectedRoute() {
  const {
    isAuthenticated,
    loading: authLoading,
    logout,
  } = useAuth();

  const location = useLocation();
  const navigate = useNavigate();

  const [checking, setChecking] = useState(false);

  // Routes that require authentication
  const protectedPaths = [
    "/dashboard",
    "/check-in",
    "/progress",
    "/profile",
    "/settings",
  ];

  // Intercept navigation away from protected pages
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) => {
      const currentlyProtected =
        protectedPaths.includes(currentLocation.pathname);

      const goingToProtected =
        protectedPaths.includes(nextLocation.pathname);

      return (
        isAuthenticated &&
        currentlyProtected &&
        !goingToProtected
      );
    }
  );

  // Validate the current session
  useEffect(() => {
    const checkAuth = async () => {
      if (authLoading) return;

      const token = localStorage.getItem("access_token");

      if (!token) {
        if (isAuthenticated) logout();
        return;
      }

      setChecking(true);

      try {
        await api.get("/auth/profile");
      } catch {
        logout();
        navigate("/login", { replace: true });
      } finally {
        setChecking(false);
      }
    };

    checkAuth();
  }, [
    location.pathname,
    authLoading,
    isAuthenticated,
    logout,
    navigate,
  ]);

  // Show loading while authentication is being checked
  if (authLoading || checking) {
    return (
      <div className="auth-loading">
        Checking your session...
      </div>
    );
  }

  // Prevent access without authentication
  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }}
      />
    );
  }

  // User chooses to log out
  const handleLogout = () => {
    logout();
    blocker.reset?.();
    navigate("/login", { replace: true });
  };

  // User chooses to stay
  const handleStay = () => {
    blocker.reset?.();
  };

  return (
    <>
      <Outlet />

      {blocker.state === "blocked" && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(0, 0, 0, 0.55)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="logout-dialog-title"
            style={{
              width: "100%",
              maxWidth: "420px",
              padding: "28px",
              borderRadius: "18px",
              background: "var(--card-bg, #ffffff)",
              color: "var(--text-primary, #222222)",
              boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: "48px",
                height: "48px",
                borderRadius: "50%",
                background: "rgba(220, 70, 70, 0.12)",
                color: "#dc4646",
                marginBottom: "18px",
              }}
            >
              <ShieldAlert size={25} />
            </div>

            <h2
              id="logout-dialog-title"
              style={{
                margin: "0 0 10px",
                fontSize: "21px",
              }}
            >
              Leave Clarity?
            </h2>

            <p
              style={{
                margin: "0 0 24px",
                lineHeight: 1.6,
                opacity: 0.75,
              }}
            >
              You are currently logged in.
              Do you want to log out before
              leaving your dashboard?
            </p>

            <div
              style={{
                display: "flex",
                gap: "12px",
                flexDirection: "column",
              }}
            >
              <button
                type="button"
                onClick={handleStay}
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "none",
                  borderRadius: "9px",
                  background: "#557b68",
                  color: "#ffffff",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <X size={17} />
                  Stay on Clarity
                </span>
              </button>

              <button
                type="button"
                onClick={handleLogout}
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "1px solid rgba(220,70,70,0.3)",
                  borderRadius: "9px",
                  background: "transparent",
                  color: "#dc4646",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  <LogOut size={17} />
                  Logout and Leave
                </span>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ProtectedRoute;