import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import DailyCheckIn from "./pages/DailyCheckIn";
import ProtectedRoute from "./components/ProtectedRoute";
import Progress from "./pages/Progress";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";

import { ThemeProvider } from "./context/ThemeContext";

function Register() {
  return <div>Clarity Register</div>;
}

function App() {
  return (
    <ThemeProvider>

      <BrowserRouter>

        <Routes>

          {/* =========================
              PUBLIC ROUTES
          ========================= */}

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/register"
            element={<Register />}
          />

          {/* =========================
              PROTECTED ROUTES
          ========================= */}

          <Route
            element={<ProtectedRoute />}
          >

            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/check-in"
              element={<DailyCheckIn />}
            />

            <Route
              path="/progress"
              element={<Progress />}
            />

            <Route
              path="/profile"
              element={<Profile />}
            />

            <Route
              path="/settings"
              element={<Settings />}
            />

          </Route>

          {/* =========================
              DEFAULT ROUTE
          ========================= */}

          <Route
            path="/"
            element={
              <Navigate
                to="/login"
                replace
              />
            }
          />

          {/* =========================
              UNKNOWN ROUTE
          ========================= */}

          <Route
            path="*"
            element={
              <Navigate
                to="/login"
                replace
              />
            }
          />

        </Routes>

      </BrowserRouter>

    </ThemeProvider>
  );
}

export default App;