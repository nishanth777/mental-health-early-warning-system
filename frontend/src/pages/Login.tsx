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
  const [resendLoading, setResendLoading] = useState(false);
  const [resendMessage, setResendMessage] = useState("");
  const [resendError, setResendError] = useState("");
  const [canResendVerification, setCanResendVerification] =
    useState(false);

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
    setResendMessage("");
    setResendError("");
    setCanResendVerification(false);

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    try {
      setLoading(true);

      const response = await api.post("/auth/login", {
        email,
        password,
      });

      const token = response.data.access_token;

      if (!token) {
        throw new Error("No access token received.");
      }

      await login(token);
      navigate("/dashboard");
    } catch (err: any) {
      console.error("Login failed:", err);

      const status = err.response?.status;
      const message =
        err.response?.data?.error ||
        "Unable to sign in. Please try again.";

      setError(message);

      // Enable resend only when the backend explicitly
      // identifies email verification as the problem.
      if (
        status === 403 &&
        /verif/i.test(message)
      ) {
        setCanResendVerification(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setResendMessage("");
    setResendError("");

    if (!email.trim()) {
      setResendError("Enter your email address first.");
      return;
    }

    try {
      setResendLoading(true);

     const response = await api.post("/auth/resend-verification", {
  email: email.trim(),
});

setResendMessage(
  response.data?.message || "Verification request processed."
);
    } catch (err: any) {
      console.error("Resend verification failed:", err);

      setResendError(
        err.response?.data?.error ||
          "Unable to process your request. Please try again."
      );
    } finally {
      setResendLoading(false);
    }
  };

  const handleGoogleLogin = async (credentialResponse: any) => {
    setError("");
    setResendMessage("");
    setResendError("");
    setCanResendVerification(false);

    if (!credentialResponse.credential) {
      setError("Google sign-in did not return a valid credential.");
      return;
    }

    try {
      setLoading(true);

      const response = await api.post("/auth/google", {
        credential: credentialResponse.credential,
      });

      const token = response.data.access_token;

      if (!token) {
        throw new Error("No access token received.");
      }

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
            <span className="brand-name">Clarity</span>
            <p>{tagline}</p>
          </div>

          {/* Login card */}
          <div className="login-card">
            {/* Heading */}
            <div className="login-heading">
              <h1>Welcome back</h1>
              <p>Take a moment for yourself.</p>
            </div>

            {/* Google OAuth — existing implementation preserved */}
            <div className="google-login-wrapper">
              <button
                type="button"
                className="custom-google-button"
              >
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
                <label htmlFor="email">Email</label>

                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => {
                    setEmail(event.target.value);
                    setResendMessage("");
                    setResendError("");
                  }}
                  disabled={loading || resendLoading}
                />
              </div>

              {/* Password */}
              <div className="form-group">
                <div className="password-label">
                  <label htmlFor="password">Password</label>

                  <button
                    type="button"
                    className="forgot-password"
                    onClick={() => {
                      // Forgot password will be implemented later.
                    }}
                    disabled={loading || resendLoading}
                  >
                    Forgot password?
                  </button>
                </div>

                <div className="password-input">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) =>
                      setPassword(event.target.value)
                    }
                    disabled={loading || resendLoading}
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() =>
                      setShowPassword((value) => !value)
                    }
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                    disabled={loading || resendLoading}
                  >
                    {showPassword ? (
                      <EyeOff size={19} />
                    ) : (
                      <Eye size={19} />
                    )}
                  </button>
                </div>
              </div>

              {/* Login error */}
              {error && (
                <p className="login-error" role="alert">
                  {error}
                </p>
              )}

              {/* Resend verification option */}
              {canResendVerification && (
                <div className="resend-verification-section">
                  <button
                    type="button"
                    className="forgot-password"
                    onClick={handleResendVerification}
                    disabled={loading || resendLoading}
                  >
                    {resendLoading
                      ? "Processing request..."
                      : "Resend verification email"}
                  </button>

                  {resendMessage && (
                    <p role="status">{resendMessage}</p>
                  )}

                  {resendError && (
                    <p className="login-error" role="alert">
                      {resendError}
                    </p>
                  )}
                </div>
              )}

              {/* Sign in button */}
              <button
                className="login-button"
                type="submit"
                disabled={loading || resendLoading}
              >
                {loading ? "Signing in..." : "Sign In"}
              </button>
            </form>

            {/* Register */}
            <p className="register-prompt">
              Don't have an account?{" "}
              <a href="/register">Create account</a>
            </p>
          </div>

          {/* Footer */}
          <p className="login-footer">
            Clarity is designed to support awareness and wellbeing.
          </p>
        </div>
      </section>
    </main>
  );
}

export default Login;