import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

// Import translation files
import enTranslations from '../locales/en.json'
import arTranslations from '../locales/ar.json'
import heTranslations from '../locales/he.json'
import esTranslations from '../locales/es.json'
import frTranslations from '../locales/fr.json'

export const supportedLanguages = {
  en: { name: 'English', dir: 'ltr' },
  ar: { name: 'العربية', dir: 'rtl' },
  he: { name: 'עברית', dir: 'rtl' },
  es: { name: 'Español', dir: 'ltr' },
  fr: { name: 'Français', dir: 'ltr' }
}

export type SupportedLanguage = keyof typeof supportedLanguages

const resources = {
  en: { translation: enTranslations },
  ar: { translation: arTranslations },
  he: { translation: heTranslations },
  es: { translation: esTranslations },
  fr: { translation: frTranslations }
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: import.meta.env.DEV,
    
    interpolation: {
      escapeValue: false
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage']
    }
  })

export default i18n
