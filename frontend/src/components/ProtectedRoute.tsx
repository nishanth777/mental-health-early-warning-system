import {
  Navigate,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

function ProtectedRoute() {
  const { isAuthenticated, loading: authLoading, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [checking, setChecking] = useState(false);

  // When the page is restored from BFCache or re-mounted,
  // always re-validate authentication by fetching the profile.
  useEffect(() => {
    const checkAuth = async () => {
      // If we're already loading from context, wait for that
      if (authLoading) return;

      const token = localStorage.getItem("access_token");
      if (!token) {
        if (isAuthenticated) logout();
        return;
      }

      setChecking(true);
      try {
        await api.get("/auth/profile");
        // Token is valid
      } catch (error) {
        // Invalid/missing token – clear session
        logout();
        navigate("/login", { replace: true });
      } finally {
        setChecking(false);
      }
    };

    checkAuth();
  }, [location, authLoading, isAuthenticated, logout, navigate]);

  if (authLoading || checking) {
    return (
      <div className="auth-loading">
        Checking your session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export default ProtectedRoute;