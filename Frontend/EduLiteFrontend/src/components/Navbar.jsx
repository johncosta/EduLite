import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { HiBell, HiMenuAlt2 } from "react-icons/hi";
import { FaUserCircle } from "react-icons/fa";
import DarkModeToggle from "./DarkModeToggle";
import LanguageSwitcher from "./LanguageSwitcher";
import logo from "../assets/EdTech_Logo.webp";
import SidebarMenu from "./Sidebar";    

export default function Navbar({ isLoggedIn, onLogout }) {
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      <nav className="bg-[#e0f2fe] dark:bg-gray-900 shadow-md fixed top-0 left-0 w-full z-50 px-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center py-3">
          {/* Logo + Name */}
          <div className="flex items-center gap-3">
            <img src={logo} alt="EduLite Logo" className="h-10 w-10" />
            <Link
              to="/"
              className="text-xl font-bold text-blue-700 dark:text-white"
            >
              EduLite
            </Link>
          </div>

          {/*   Buttons */}
          <div className="flex items-center gap-4">
            {/* Large screen */}
            <div className="hidden md:block">
              <Link
                to="/notifications"
                title={t("notifications")}
                className="text-gray-600 dark:text-gray-300 hover:text-blue-600"
              >
                <HiBell className="text-2xl" />
              </Link>
            </div>

            {/* Login / Logout */}
            {isLoggedIn ? (
              <button
                onClick={onLogout}
                className="text-sm text-red-500 hover:underline"
              >
                {t("nav.logout")}
              </button>
            ) : (
              <Link
                to="/login"
                className="text-gray-700 dark:text-gray-200 hover:text-blue-600 transition text-sm"
              >
                {t("nav.login")}
              </Link>
            )}

            {/* Language / Dark mode */}
            <LanguageSwitcher />
            <DarkModeToggle />

            {/* Sidebar Menu Button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-700 dark:text-gray-200 hover:text-blue-600"
              title={t("menu")}
            >
              <HiMenuAlt2 className="text-2xl" />
            </button>
          </div>
        </div>
      </nav>

      {/* Sidebar Menu  */}
      <SidebarMenu open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
    </>
  );
}
