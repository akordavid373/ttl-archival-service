import React, { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";
import { useTheme } from "./ThemeContext";

interface UserSettings {
  language: string;
  timezone: string;
  email_notifications: boolean;
  push_notifications: boolean;
  in_app_notifications: boolean;
  notification_frequency: string;
  api_enabled: boolean;
  api_key: string | null;
  webhook_url: string | null;
  theme: string;
  accent_color: string;
  full_name: string | null;
  email: string | null;
}

interface SettingsContextType {
  settings: UserSettings | null;
  loading: boolean;
  updateSettings: (newSettings: Partial<UserSettings>) => Promise<void>;
  refreshSettings: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(
  undefined,
);

const API_BASE_URL = "http://localhost:8000/api/v1";

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const { setTheme } = useTheme();

  const refreshSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/settings`);
      setSettings(response.data);

      // Sync theme with settings if it's set to something other than 'system'
      if (
        response.data.theme &&
        ["light", "dark", "system"].includes(response.data.theme)
      ) {
        setTheme(response.data.theme as "light" | "dark" | "system");
      }
    } catch (error) {
      console.error("Failed to fetch settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (newSettings: Partial<UserSettings>) => {
    try {
      const response = await axios.patch(
        `${API_BASE_URL}/settings`,
        newSettings,
      );
      setSettings(response.data);

      if (
        newSettings.theme &&
        ["light", "dark", "system"].includes(newSettings.theme)
      ) {
        setTheme(newSettings.theme as "light" | "dark" | "system");
      }
    } catch (error) {
      console.error("Failed to update settings:", error);
      throw error;
    }
  };

  useEffect(() => {
    refreshSettings();
  }, []);

  return (
    <SettingsContext.Provider
      value={{ settings, loading, updateSettings, refreshSettings }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return context;
}
