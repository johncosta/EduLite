 import { useTranslation } from "react-i18next";
import { HiOutlineTranslate } from "react-icons/hi";

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === "en" ? "ar" : "en";
    i18n.changeLanguage(newLang);
    document.dir = newLang === "ar" ? "rtl" : "ltr";
  };

  return (
    <button
      onClick={toggleLanguage}
      className="text-xl text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-yellow-400 transition"
      aria-label="Toggle language"
    >
      <HiOutlineTranslate />
    </button>
  );
}
