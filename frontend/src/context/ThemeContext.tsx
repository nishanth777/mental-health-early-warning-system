import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

interface ThemeContextType {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext =
  createContext<ThemeContextType | undefined>(
    undefined
  );

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({
  children,
}: ThemeProviderProps) {
  const [darkMode, setDarkMode] =
    useState<boolean>(() => {
      return (
        localStorage.getItem(
          "clarity_dark_mode"
        ) === "true"
      );
    });

  /*
   * Apply theme globally whenever
   * darkMode changes.
   */
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add(
        "dark-mode"
      );

      localStorage.setItem(
        "clarity_dark_mode",
        "true"
      );
    } else {
      document.documentElement.classList.remove(
        "dark-mode"
      );

      localStorage.setItem(
        "clarity_dark_mode",
        "false"
      );
    }
  }, [darkMode]);

  const toggleDarkMode =
    useCallback(() => {
      setDarkMode(
        (current) => !current
      );
    }, []);

  return (
    <ThemeContext.Provider
      value={{
        darkMode,
        toggleDarkMode,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context =
    useContext(ThemeContext);

  if (!context) {
    throw new Error(
      "useTheme must be used inside ThemeProvider"
    );
  }

  return context;
}