import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { User, Mail, Lock, Eye, EyeOff } from "lucide-react";

import api from "../services/api";
import "../App.css";

const taglines = [
  "Understand yourself. Grow every day.",
  "Clearer mind. Better wellbeing.",
  "Small check-ins. Better wellbeing.",
  "Take a moment. Check in with yourself.",
  "Your wellbeing deserves attention too.",
];

function Register() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [tagline] = useState(() => {
    const index = Math.floor(Math.random() * taglines.length);
    return taglines[index];
  });

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!fullName.trim() || !email.trim() || !password) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      await api.post("/auth/signup", {
        full_name: fullName.trim(),
        email: email.trim(),
        password,
      });

      setSuccess(
        "Account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } catch (error: any) {
      console.error("Registration failed:", error);

      if (error.response?.status === 409) {
        setError("This email is already registered.");
      } else if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError(
          "Unable to create your account. Please try again."
        );
      }
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

      {/* Register section */}
      <section className="login-section">
        <div className="login-content">

          {/* Brand */}
          <div className="brand">
            <span className="brand-name">
              Clarity
            </span>

            <p>{tagline}</p>
          </div>

          {/* Card */}
          <div className="login-card register-card">

            <div className="login-heading">
              <h1>Create your account</h1>

              <p>
                Start monitoring your wellbeing and track
                your progress over time.
              </p>
            </div>

            <form
              className="register-form"
              onSubmit={handleSubmit}
            >

              {/* Full name */}
              <div className="register-form-group">
                <label htmlFor="fullName">
                  Full name
                </label>

                <div className="register-input-wrapper">
                  <User size={18} />

                  <input
                    id="fullName"
                    type="text"
                    placeholder="Enter your full name"
                    value={fullName}
                    onChange={(event) =>
                      setFullName(event.target.value)
                    }
                    autoComplete="name"
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Email */}
              <div className="register-form-group">
                <label htmlFor="register-email">
                  Email address
                </label>

                <div className="register-input-wrapper">
                  <Mail size={18} />

                  <input
                    id="register-email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(event) =>
                      setEmail(event.target.value)
                    }
                    autoComplete="email"
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Password */}
              <div className="register-form-group">
                <label htmlFor="register-password">
                  Password
                </label>

                <div className="register-input-wrapper">
                  <Lock size={18} />

                  <input
                    id="register-password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    placeholder="Create a password"
                    value={password}
                    onChange={(event) =>
                      setPassword(event.target.value)
                    }
                    autoComplete="new-password"
                    disabled={loading}
                  />

                  <button
                    type="button"
                    className="register-password-toggle"
                    onClick={() =>
                      setShowPassword(
                        (current) => !current
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
                      <EyeOff size={18} />
                    ) : (
                      <Eye size={18} />
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm password */}
              <div className="register-form-group">
                <label htmlFor="confirmPassword">
                  Confirm password
                </label>

                <div className="register-input-wrapper">
                  <Lock size={18} />

                  <input
                    id="confirmPassword"
                    type={
                      showConfirmPassword
                        ? "text"
                        : "password"
                    }
                    placeholder="Confirm your password"
                    value={confirmPassword}
                    onChange={(event) =>
                      setConfirmPassword(
                        event.target.value
                      )
                    }
                    autoComplete="new-password"
                    disabled={loading}
                  />

                  <button
                    type="button"
                    className="register-password-toggle"
                    onClick={() =>
                      setShowConfirmPassword(
                        (current) => !current
                      )
                    }
                    aria-label={
                      showConfirmPassword
                        ? "Hide password"
                        : "Show password"
                    }
                    disabled={loading}
                  >
                    {showConfirmPassword ? (
                      <EyeOff size={18} />
                    ) : (
                      <Eye size={18} />
                    )}
                  </button>
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="register-error">
                  {error}
                </div>
              )}

              {/* Success */}
              {success && (
                <div className="register-success">
                  {success}
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                className="login-button register-submit"
                disabled={loading}
              >
                {loading
                  ? "Creating account..."
                  : "Create account"}
              </button>

            </form>

            {/* Footer */}
            <p className="register-prompt">
              Already have an account?{" "}
              <Link to="/login">
                Sign in
              </Link>
            </p>

          </div>

          <p className="login-footer">
            Clarity is designed to support awareness and wellbeing.
          </p>

        </div>
      </section>

    </main>
  );
}

export default Register;