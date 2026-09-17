import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import api from "../services/api";
import "../App.css";
import { useAuth } from "../context/AuthContext";
import { GoogleLogin } from "@react-oauth/google";

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

  const handleGoogleLogin = async (credentialResponse: any) => {
    setError("");

    if (!credentialResponse.credential) {
      setError("Google sign-in did not return a valid credential.");
      return;
    }

    try {
      setLoading(true);

      /*
       * Send Google's ID token to Flask.
       * Flask verifies the token and returns
       * our application's JWT.
       */
      const response = await api.post("/auth/google", {
        credential: credentialResponse.credential,
      });

      const token = response.data.access_token;

      if (!token) {
        throw new Error("No access token received.");
      }

      /*
       * Use the same authentication flow as
       * normal email/password login.
       */
      await login(token);

      navigate("/dashboard");
    } catch (err: any) {
      console.error("Google login failed:", err);

      const message =
        err.response?.data?.error ||
        "Unable to sign in with Google. Please try again.";

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
<div className="google-login-wrapper">
  <button type="button" className="custom-google-button">
    <svg
      className="google-logo"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        fill="#4285F4"
        d="M21.35 12.27c0-.71-.06-1.39-.18-2.05H12v3.88h5.24a4.48 4.48 0 0 1-1.94 2.94v2.44h3.14c1.84-1.69 2.91-4.18 2.91-7.21z"
      />
      <path
        fill="#34A853"
        d="M12 21.5c2.63 0 4.84-.87 6.45-2.36l-3.14-2.44c-.87.58-1.98.92-3.31.92-2.54 0-4.69-1.72-5.46-4.03H3.3v2.52A9.74 9.74 0 0 0 12 21.5z"
      />
      <path
        fill="#FBBC05"
        d="M6.54 13.59A5.85 5.85 0 0 1 6.23 12c0-.55.1-1.09.31-1.59V7.89H3.3A9.5 9.5 0 0 0 2.5 12c0 1.48.36 2.88.8 4.11l3.24-2.52z"
      />
      <path
        fill="#EA4335"
        d="M12 6.38c1.43 0 2.71.49 3.72 1.45l2.79-2.79C16.83 3.49 14.63 2.5 12 2.5a9.74 9.74 0 0 0-8.7 5.39l3.24 2.52C7.31 8.1 9.46 6.38 12 6.38z"
      />
    </svg>

    <span>Continue with Google</span>
  </button>

  <div className="google-login-overlay">
    <GoogleLogin
      onSuccess={handleGoogleLogin}
      onError={() => {
        setError(
          "Google sign-in was unsuccessful. Please try again."
        );
      }}
      useOneTap={false}
      theme="outline"
      size="large"
      text="continue_with"
      shape="rectangular"
      width="100%"
    />
  </div>
</div>

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