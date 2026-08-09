import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import api from "../services/api";
import "../App.css";
import { useAuth } from "../context/AuthContext";

const taglines = [
  "Understand yourself. Grow every day.",
  "Clearer mind. Better wellbeing.",
  "Small check-ins. Better wellbeing.",
  "Take a moment. Check in with yourself.",
  "Your wellbeing deserves attention too.",
];

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [tagline] = useState(() => {
    const index = Math.floor(Math.random() * taglines.length);
    return taglines[index];
  });

  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setError("");

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    try {
      setLoading(true);

      // Send login request to Flask backend
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      const token = response.data.access_token;

      if (!token) {
        throw new Error("No access token received.");
      }

      /*
       * Let AuthContext handle the token and
       * verify the authenticated user.
       */
      await login(token);

      /*
       * Only navigate after authentication
       * has been successfully verified.
       */
      navigate("/dashboard");
    } catch (err: any) {
      console.error("Login failed:", err);

      const message =
        err.response?.data?.error ||
        "Unable to sign in. Please try again.";

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">

      {/* Left visual section */}
      <section className="login-visual">

        <div className="visual-orb orb-one" />
        <div className="visual-orb orb-two" />

        <div className="wellness-placeholder">
          <div className="placeholder-circle" />
          <div className="placeholder-leaf leaf-one" />
          <div className="placeholder-leaf leaf-two" />
        </div>

        <p className="visual-caption">
          A calmer way to understand your wellbeing.
        </p>

      </section>

      {/* Right login section */}
      <section className="login-section">

        <div className="login-content">

          {/* Brand */}
          <div className="brand">

            <span className="brand-name">
              Clarity
            </span>

            <p>
              {tagline}
            </p>

          </div>

          {/* Login card */}
          <div className="login-card">

            {/* Heading */}
            <div className="login-heading">

              <h1>
                Welcome back
              </h1>

              <p>
                Take a moment for yourself.
              </p>

            </div>

            {/* Google OAuth */}
            <button
              className="google-button"
              type="button"
              onClick={() => {
                // Google OAuth will be connected later.
              }}
            >
              Continue with Google
            </button>

            {/* Divider */}
            <div className="divider">
              <span>or</span>
            </div>

            {/* Login form */}
            <form onSubmit={handleLogin}>

              {/* Email */}
              <div className="form-group">

                <label htmlFor="email">
                  Email
                </label>

                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  autoComplete="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  disabled={loading}
                />

              </div>

              {/* Password */}
              <div className="form-group">

                <div className="password-label">

                  <label htmlFor="password">
                    Password
                  </label>

                  <button
                    type="button"
                    className="forgot-password"
                    onClick={() => {
                      // Forgot password will be implemented later.
                    }}
                    disabled={loading}
                  >
                    Forgot password?
                  </button>

                </div>

                <div className="password-input">

                  <input
                    id="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) =>
                      setPassword(event.target.value)
                    }
                    disabled={loading}
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() =>
                      setShowPassword(
                        (value) => !value
                      )
                    }
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    disabled={loading}
                  >
                    {showPassword ? (
                      <EyeOff size={19} />
                    ) : (
                      <Eye size={19} />
                    )}
                  </button>

                </div>

              </div>

              {/* Error message */}
              {error && (
                <p className="login-error">
                  {error}
                </p>
              )}

              {/* Sign in button */}
              <button
                className="login-button"
                type="submit"
                disabled={loading}
              >
                {loading
                  ? "Signing in..."
                  : "Sign In"}
              </button>

            </form>

            {/* Register */}
            <p className="register-prompt">

              Don't have an account?{" "}

              <a href="/register">
                Create account
              </a>

            </p>

          </div>

          {/* Footer */}
          <p className="login-footer">
            Clarity is designed to support awareness
            and wellbeing.
          </p>

        </div>

      </section>

    </main>
  );
}

export default Login;