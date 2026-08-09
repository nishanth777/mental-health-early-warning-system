import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000",
  headers: {
    "Content-Type": "application/json",
  },
});

/*
 * Attach the JWT automatically to every protected request.
 */
api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/*
 * Handle expired/invalid JWT tokens centrally.
 */
api.interceptors.response.use(
  (response) => {
    return response;
  },

  (error) => {
    if (error.response?.status === 401) {
      const message =
        error.response?.data?.msg ||
        error.response?.data?.error ||
        "";

      if (
        message.toLowerCase().includes("token") ||
        message.toLowerCase().includes("expired") ||
        message.toLowerCase().includes("jwt")
      ) {
        console.log(
          "JWT expired or invalid. Logging out."
        );

        localStorage.removeItem(
          "access_token"
        );

        /*
         * Only redirect if we are not already
         * on the login page.
         */
        if (
          window.location.pathname !== "/login"
        ) {
          window.location.href = "/login";
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;