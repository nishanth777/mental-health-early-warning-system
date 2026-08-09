import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import api from "../services/api";

interface User {
  full_name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  /*
   * Fetch the currently authenticated user's profile.
   */
  const fetchProfile = useCallback(async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setUser(null);
      return;
    }

    try {
      const response = await api.get("/auth/profile", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setUser(response.data);
    } catch (error) {
      console.error("Authentication check failed:", error);

      localStorage.removeItem("access_token");
      setUser(null);
    }
  }, []);

  /*
   * Called after a successful login.
   */
  const login = useCallback(
    async (token: string) => {
      localStorage.setItem("access_token", token);

      try {
        const response = await api.get("/auth/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setUser(response.data);
      } catch (error) {
        console.error("Login verification failed:", error);

        localStorage.removeItem("access_token");
        setUser(null);

        throw error;
      }
    },
    []
  );

  /*
   * Logout
   */
  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setUser(null);
  }, []);

  /*
   * Check existing session when the application starts.
   */
  useEffect(() => {
    const checkAuthentication = async () => {
      setLoading(true);

      await fetchProfile();

      setLoading(false);
    };

    checkAuthentication();
  }, [fetchProfile]);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside an AuthProvider"
    );
  }

  return context;
}