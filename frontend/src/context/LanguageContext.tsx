import React, { createContext, useContext, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { SupportedLanguage, supportedLanguages } from "../utils/i18n";

interface LanguageContextType {
  currentLanguage: SupportedLanguage;
  changeLanguage: (language: SupportedLanguage) => void;
  isRTL: boolean;
  availableLanguages: typeof supportedLanguages;
}

const LanguageContext = createContext<LanguageContextType | undefined>(
  undefined,
);

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { i18n } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState<SupportedLanguage>(
    (i18n.language as SupportedLanguage) || "en",
  );

  const isRTL = supportedLanguages[currentLanguage]?.dir === "rtl";

  const changeLanguage = (language: SupportedLanguage) => {
    i18n.changeLanguage(language);
    setCurrentLanguage(language);

    // Store language preference in localStorage
    localStorage.setItem("language", language);

    // Update document direction for RTL support
    document.documentElement.dir = supportedLanguages[language].dir;
    document.documentElement.lang = language;
  };

  useEffect(() => {
    // Set initial language from localStorage or browser preference
    const savedLanguage = localStorage.getItem("language") as SupportedLanguage;
    const browserLanguage = navigator.language.split(
      "-",
    )[0] as SupportedLanguage;

    const initialLanguage =
      savedLanguage ||
      (browserLanguage in supportedLanguages ? browserLanguage : "en");

    if (initialLanguage !== currentLanguage) {
      changeLanguage(initialLanguage);
    } else {
      // Set document direction on initial load
      document.documentElement.dir = supportedLanguages[currentLanguage].dir;
      document.documentElement.lang = currentLanguage;
    }
  }, []);

  useEffect(() => {
    // Update current language when i18n language changes
    const newLanguage = i18n.language as SupportedLanguage;
    if (newLanguage !== currentLanguage && newLanguage in supportedLanguages) {
      setCurrentLanguage(newLanguage);
      document.documentElement.dir = supportedLanguages[newLanguage].dir;
      document.documentElement.lang = newLanguage;
    }
  }, [i18n.language, currentLanguage]);

  const value: LanguageContextType = {
    currentLanguage,
    changeLanguage,
    isRTL,
    availableLanguages: supportedLanguages,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};
