import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { HiX } from "react-icons/hi";

export default function SidebarMenu({ open, onClose }) {
  const { t, i18n } = useTranslation();
  const direction = i18n.dir();
  const side = direction === "rtl" ? "left-0" : "right-0";

  return (
    <div
      className={`fixed top-0 ${side} h-full w-64 bg-[#f0f9ff] dark:bg-gray-800 shadow-lg z-50 transform transition-transform duration-300 ease-in-out ${
        open
          ? "translate-x-0"
          : direction === "rtl"
          ? "-translate-x-full"
          : "translate-x-full"
      }`}
    >
      {/* Top */}
      <div className="flex justify-between items-center px-4 py-4 border-b border-gray-300 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
          {t("nav.menu")}
        </h2>
        <button onClick={onClose}>
          <HiX className="text-2xl text-gray-700 dark:text-white" />
        </button>
      </div>

      {/* all pages */}
      <div className="p-4 space-y-4">
        <Link
          to="/"
          onClick={onClose}
          className="block text-gray-700 dark:text-gray-200 hover:text-blue-600"
        >
          {t("nav.home")}
        </Link>
        <Link
          to="/conversations"
          onClick={onClose}
          className="block text-gray-700 dark:text-gray-200 hover:text-blue-600"
        >
          {t("nav.conversations")}
        </Link>
        <Link
          to="/chapters"
          onClick={onClose}
          className="block text-gray-700 dark:text-gray-200 hover:text-blue-600"
        >
          {t("nav.chapters")}
        </Link>
        <Link
          to="/profile"
          onClick={onClose}
          className="block text-gray-700 dark:text-gray-200 hover:text-blue-600"
        >
          {t("nav.profile")}
        </Link>
        <Link
          to="/settings"
          onClick={onClose}
          className="block text-gray-700 dark:text-gray-200 hover:text-blue-600"
        >
          {t("nav.settings")}
        </Link>
      </div>
    </div>
  );
}
