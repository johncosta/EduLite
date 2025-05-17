 import { useEffect, useState } from "react";
import { HiOutlineMoon, HiOutlineSun } from "react-icons/hi";

export default function DarkModeToggle() {
  const [isDark, setIsDark] = useState(() =>
    window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDark]);

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="text-xl text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-yellow-400 transition"
      aria-label="Toggle dark mode"
    >
      {isDark ? <HiOutlineSun /> : <HiOutlineMoon />}
    </button>
  );
}
