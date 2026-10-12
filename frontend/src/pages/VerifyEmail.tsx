
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  CheckCircle,
  XCircle,
  LoaderCircle,
} from "lucide-react";

import api from "../services/api";
import "../App.css";

type VerificationStatus = "loading" | "success" | "error";

type VerificationResponse = {
  message?: string;
};

// Share an in-flight request between React Strict Mode effect runs.
const verificationRequests = new Map<
  string,
  ReturnType<typeof api.post<VerificationResponse>>
>();

function VerifyEmail() {
  const [searchParams] = useSearchParams();

  const [status, setStatus] =
    useState<VerificationStatus>("loading");

  const [message, setMessage] = useState(
    "Verifying your email address..."
  );

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setStatus("error");
      setMessage(
        "The verification link is missing its token. Please request a new verification email."
      );
      return;
    }

    let active = true;

    let request = verificationRequests.get(token);

    if (!request) {
      request = api.post<VerificationResponse>(
        "/auth/verify-email",
        { token }
      );

      verificationRequests.set(token, request);

      const currentRequest = request;

      const removeRequest = () => {
        if (verificationRequests.get(token) === currentRequest) {
          verificationRequests.delete(token);
        }
      };

      currentRequest.then(removeRequest, removeRequest);
    }

    request
      .then((response) => {
        if (!active) return;

        setStatus("success");
        setMessage(
          response.data?.message ||
            "Your email has been verified successfully. You can now sign in."
        );
      })
      .catch((error: unknown) => {
        if (!active) return;

        console.error("Email verification failed:", error);

        const apiError = error as {
          response?: {
            data?: {
              error?: string;
              message?: string;
            };
          };
          message?: string;
        };

        setStatus("error");

        setMessage(
          apiError.response?.data?.error ||
            apiError.response?.data?.message ||
            "We couldn't verify your email. The link may be invalid or expired."
        );
      });

    return () => {
      active = false;
    };
  }, [searchParams]);

  return (
    <main className="login-page">
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

      <section className="login-section">
        <div className="login-content">
          <div className="brand">
            <span className="brand-name">Clarity</span>

            <p>Understand yourself. Grow every day.</p>
          </div>

          <div className="login-card verification-card">
            <div className="verification-icon">
              {status === "loading" && (
                <LoaderCircle
                  size={48}
                  className="verification-spinner"
                />
              )}

              {status === "success" && (
                <CheckCircle size={48} />
              )}

              {status === "error" && (
                <XCircle size={48} />
              )}
            </div>

            <div className="login-heading">
              <h1>
                {status === "loading"
                  ? "Verifying your email"
                  : status === "success"
                    ? "Email verified!"
                    : "Verification unsuccessful"}
              </h1>

              <p role="status" aria-live="polite">
                {message}
              </p>
            </div>

            {status !== "loading" && (
              <Link
                to="/login"
                className="login-button verification-button"
              >
                Go to Sign In
              </Link>
            )}
          </div>

          <p className="login-footer">
            Clarity is designed to support awareness and wellbeing.
          </p>
        </div>
      </section>
    </main>
  );
}

export default VerifyEmail;
