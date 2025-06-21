import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { HiBell, HiMenuAlt2, HiX } from "react-icons/hi";
import { FaUserCircle } from "react-icons/fa";
import DarkModeToggle from "./DarkModeToggle";
import LanguageSwitcher from "./LanguageSwitcher";
import logo from "../assets/EdTech_Logo.webp";
import SidebarMenu from "./Sidebar";

export default function Navbar({ isLoggedIn, onLogout }) {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Helper function to check if current path matches the nav item
  const isActiveRoute = (path) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  return (
    <>
      <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/20 dark:border-gray-700/20 fixed top-0 left-0 w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          {/* Main Navbar */}
          <div className="flex items-center justify-between py-4 lg:grid lg:grid-cols-3">
            {/* Left Section - Logo + Name */}
            <div className="flex items-center gap-3 lg:justify-start">
              <div className="relative group">
                <img
                  src={logo}
                  alt="EduLite Logo"
                  className="h-8 w-8 sm:h-9 sm:w-9 rounded-lg"
                />
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-300"></div>
              </div>
              <Link
                to="/"
                className="text-lg sm:text-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
              >
                EduLite
              </Link>
            </div>

            {/* Center Section - Desktop Navigation */}
            <div className="hidden lg:flex items-center justify-center gap-2">
              <Link
                to="/"
                className={`relative px-4 py-2 rounded-full font-medium transition-all duration-300 ${
                  isActiveRoute("/")
                    ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                    : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                }`}
              >
                {t("nav.home")}
              </Link>
              <Link
                to="/about"
                className={`relative px-4 py-2 rounded-full font-medium transition-all duration-300 ${
                  isActiveRoute("/about")
                    ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                    : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                }`}
              >
                {t("nav.about")}
              </Link>
              <Link
                to="/conversations"
                className={`relative px-4 py-2 rounded-full font-medium transition-all duration-300 ${
                  isActiveRoute("/conversations")
                    ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                    : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                }`}
              >
                {t("nav.conversations")}
              </Link>
              <Link
                to="/chapters"
                className={`relative px-4 py-2 rounded-full font-medium transition-all duration-300 ${
                  isActiveRoute("/chapters")
                    ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                    : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                }`}
              >
                {t("nav.chapters")}
              </Link>
            </div>

            {/* Right Section - Actions */}
            <div className="flex items-center gap-1 sm:gap-2 lg:justify-end">
              {/* Desktop Actions - Hidden on small screens */}
              <div className="hidden lg:flex items-center gap-1">
                {/* Notifications */}
                <Link
                  to="/notifications"
                  title={t("notifications")}
                  className="relative p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200 group"
                >
                  <HiBell className="text-xl text-gray-600 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                </Link>

                {/* Login/Logout */}
                {isLoggedIn ? (
                  <button
                    onClick={onLogout}
                    className="px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-all duration-200"
                  >
                    {t("nav.logout")}
                  </button>
                ) : (
                  <Link
                    to="/login"
                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-all duration-200"
                  >
                    {t("nav.login")}
                  </Link>
                )}
              </div>

              {/* Control Center - Compact on mobile, full on desktop */}
              <div className="flex items-center gap-0.5 sm:gap-1 bg-gray-100/50 dark:bg-gray-800/50 rounded-full p-0.5 sm:p-1 backdrop-blur-sm">
                {/* Language Switcher */}
                <div className="p-1.5 sm:p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200">
                  <LanguageSwitcher />
                </div>

                {/* Dark Mode Toggle */}
                <div className="p-1.5 sm:p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200">
                  <DarkModeToggle />
                </div>

                {/* Mobile Menu Button - Visible on small screens */}
                <button
                  onClick={() => setMobileMenuOpen(true)}
                  className="lg:hidden p-1.5 sm:p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200 group"
                  title={t("menu")}
                >
                  <HiMenuAlt2 className="text-lg sm:text-xl text-gray-700 dark:text-gray-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                </button>

                {/* Sidebar Menu Button - Always visible for secondary nav */}
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="hidden lg:block p-2 rounded-full hover:bg-white/60 dark:hover:bg-gray-700/60 transition-all duration-200 group"
                  title={t("menu")}
                >
                  <HiMenuAlt2 className="text-xl text-gray-700 dark:text-gray-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Menu Overlay */}
        {mobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-sm">
            <div className="absolute inset-y-0 right-0 w-full max-w-sm bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl border-l border-gray-200/50 dark:border-gray-700/50">
              {/* Mobile Menu Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200/50 dark:border-gray-700/50">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Menu
                </h2>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200"
                >
                  <HiX className="text-xl text-gray-500 dark:text-gray-400" />
                </button>
              </div>

              {/* Mobile Navigation Links */}
              <div className="px-6 py-4 space-y-2">
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-4 py-3 rounded-xl font-medium transition-all duration-300 ${
                    isActiveRoute("/")
                      ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                      : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                  }`}
                >
                  {t("nav.home")}
                </Link>
                <Link
                  to="/about"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-4 py-3 rounded-xl font-medium transition-all duration-300 ${
                    isActiveRoute("/about")
                      ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                      : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                  }`}
                >
                  {t("nav.about")}
                </Link>
                <Link
                  to="/conversations"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-4 py-3 rounded-xl font-medium transition-all duration-300 ${
                    isActiveRoute("/conversations")
                      ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                      : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                  }`}
                >
                  {t("nav.conversations")}
                </Link>
                <Link
                  to="/chapters"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-4 py-3 rounded-xl font-medium transition-all duration-300 ${
                    isActiveRoute("/chapters")
                      ? "text-white bg-blue-600 shadow-lg shadow-blue-600/25"
                      : "text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50"
                  }`}
                >
                  {t("nav.chapters")}
                </Link>
              </div>

              {/* Mobile Actions */}
              <div className="px-6 py-4 border-t border-gray-200/50 dark:border-gray-700/50 space-y-3">
                {/* Notifications */}
                <Link
                  to="/notifications"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-200 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 transition-all duration-200"
                >
                  <HiBell className="text-xl" />
                  <span className="font-medium">{t("notifications")}</span>
                </Link>

                {/* Login/Logout */}
                {isLoggedIn ? (
                  <button
                    onClick={() => {
                      onLogout();
                      setMobileMenuOpen(false);
                    }}
                    className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200"
                  >
                    <FaUserCircle className="text-xl" />
                    <span className="font-medium">{t("nav.logout")}</span>
                  </button>
                ) : (
                  <Link
                    to="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-200 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 transition-all duration-200"
                  >
                    <FaUserCircle className="text-xl" />
                    <span className="font-medium">{t("nav.login")}</span>
                  </Link>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Sidebar Menu */}
      <SidebarMenu open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
    </>
  );
}
