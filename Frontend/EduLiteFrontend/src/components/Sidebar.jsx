import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  HiX,
  HiHome,
  HiInformationCircle,
  HiChatAlt2,
  HiBookOpen,
  HiUser,
  HiCog,
} from "react-icons/hi";

export default function SidebarMenu({ open, onClose }) {
  const { t, i18n } = useTranslation();
  const direction = i18n.dir();
  const side = direction === "rtl" ? "left-0" : "right-0";

  const menuItems = [
    { to: "/", label: t("nav.home"), icon: HiHome },
    { to: "/about", label: t("nav.about"), icon: HiInformationCircle },
    { to: "/conversations", label: t("nav.conversations"), icon: HiChatAlt2 },
    { to: "/chapters", label: t("nav.chapters"), icon: HiBookOpen },
    { to: "/profile", label: t("nav.profile"), icon: HiUser },
    { to: "/settings", label: t("nav.settings"), icon: HiCog },
  ];

  return (
    <>
      {/* Backdrop for all screens */}
      {open && (
        <div
          className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
          onClick={onClose}
        />
      )}

      {/* Sidebar - Works for BOTH mobile and desktop */}
      <div
        className={`fixed top-0 ${side} h-full w-80 max-w-full
           bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl
           border-l border-gray-200/20 dark:border-gray-700/20
           shadow-2xl z-50 transform transition-transform duration-300 ease-out
           ${open ? "translate-x-0" : direction === "rtl" ? "-translate-x-full" : "translate-x-full"}`}
      >
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200/30 dark:border-gray-700/30">
          <h2 className="text-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {t("nav.menu")}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition"
            aria-label={t("sidebar.closeMenu")}
          >
            <HiX className="text-xl text-gray-600 dark:text-gray-300" />
          </button>
        </div>

        {/* Menu Items */}
        <div className="px-4 py-6">
          <nav className="space-y-2">
            {menuItems.map((item, index) => {
              const IconComponent = item.icon;
              return (
                <Link
                  key={index}
                  to={item.to}
                  onClick={onClose}
                  className="group flex items-center gap-4 px-4 py-3 rounded-xl hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-blue-900/20 dark:hover:to-purple-900/20 transition"
                >
                  <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 group-hover:bg-gradient-to-r group-hover:from-blue-500 group-hover:to-purple-500 transition">
                    <IconComponent className="text-lg text-gray-600 dark:text-gray-300 group-hover:text-white" />
                  </div>
                  <span className="font-medium text-gray-700 dark:text-gray-200 group-hover:text-blue-700 dark:group-hover:text-blue-300">
                    {item.label}
                  </span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-gray-200/30 dark:border-gray-700/30">
          <div className="text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400 font-light">
              {t("sidebar.version")}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              {t("sidebar.description")}
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
