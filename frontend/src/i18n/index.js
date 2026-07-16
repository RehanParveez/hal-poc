import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import ur from './locales/ur.json'

const STORAGE_KEY = 'hal_locale'
const savedLocale = localStorage.getItem(STORAGE_KEY)
const defaultLocale = savedLocale || import.meta.env.VITE_DEFAULT_LANG || 'ur'

export const i18n = createI18n({
  legacy: false,
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: { en, ur },
})

export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
  document.documentElement.setAttribute('dir', locale === 'ur' ? 'rtl' : 'ltr')
  document.documentElement.setAttribute('lang', locale)
}

setLocale(defaultLocale)