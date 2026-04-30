import React from "react";
import { useTranslation } from "react-i18next";
import { useLanguage } from "../context/LanguageContext";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Globe } from "lucide-react";

export const LanguageSwitcher: React.FC = () => {
  const { t } = useTranslation();
  const { currentLanguage, changeLanguage, availableLanguages } = useLanguage();

  const handleLanguageChange = (language: string) => {
    changeLanguage(language as keyof typeof availableLanguages);
  };

  return (
    <div className="flex items-center space-x-2">
      <Globe className="h-4 w-4 text-muted-foreground" />
      <Select value={currentLanguage} onValueChange={handleLanguageChange}>
        <SelectTrigger className="w-[140px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {Object.entries(availableLanguages).map(([code, language]) => (
            <SelectItem key={code} value={code}>
              <span className="flex items-center space-x-2">
                <span>{language.name}</span>
                {language.dir === "rtl" && (
                  <span className="text-xs text-muted-foreground">(RTL)</span>
                )}
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
