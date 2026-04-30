import React, { createContext, useContext, useState } from "react";
import { useHotkeys } from "react-hotkeys-hook";
import { useNavigate } from "react-router-dom";

interface Shortcut {
  key: string;
  description: string;
  action: () => void;
  category: "Navigation" | "Actions" | "View";
}

interface ShortcutContextType {
  shortcuts: Shortcut[];
  isHelpOpen: boolean;
  setHelpOpen: (open: boolean) => void;
}

const ShortcutContext = createContext<ShortcutContextType | undefined>(
  undefined,
);

export const ShortcutProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const navigate = useNavigate();
  const [isHelpOpen, setHelpOpen] = useState(false);

  const shortcuts: Shortcut[] = [
    {
      key: "ctrl+k",
      description: "Command Palette",
      action: () => console.log("Palette"),
      category: "Actions",
    },
    {
      key: "?",
      description: "Show Help",
      action: () => setHelpOpen((prev) => !prev),
      category: "View",
    },
    {
      key: "g d",
      description: "Go to Dashboard",
      action: () => navigate("/"),
      category: "Navigation",
    },
    {
      key: "g p",
      description: "Go to Policies",
      action: () => navigate("/policies"),
      category: "Navigation",
    },
    {
      key: "g a",
      description: "Go to Archives",
      action: () => navigate("/archives"),
      category: "Navigation",
    },
    {
      key: "g b",
      description: "Go to Blockchain",
      action: () => navigate("/blockchain"),
      category: "Navigation",
    },
    {
      key: "g s",
      description: "Go to Settings",
      action: () => navigate("/settings"),
      category: "Navigation",
    },
  ];

  // Register all shortcuts
  shortcuts.forEach((s) => {
    useHotkeys(s.key, (e) => {
      e.preventDefault();
      s.action();
    });
  });

  return (
    <ShortcutContext.Provider value={{ shortcuts, isHelpOpen, setHelpOpen }}>
      {children}
    </ShortcutContext.Provider>
  );
};

export const useShortcuts = () => {
  const context = useContext(ShortcutContext);
  if (!context)
    throw new Error("useShortcuts must be used within ShortcutProvider");
  return context;
};
