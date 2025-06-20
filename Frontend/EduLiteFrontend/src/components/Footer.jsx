import { useTranslation } from "react-i18next";
import {
  FaFacebookF,
  FaLinkedinIn,
  FaEnvelope,
  FaHeart,
  FaGithub,
} from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";

const Footer = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.dir() === "rtl";

  return (
    <footer className="relative bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-black border-t border-gray-200/50 dark:border-gray-800/50">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        {/* Main Footer Content */}
        <div className="py-16 md:py-20">
          <div
            className={`grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center ${
              isRTL ? "lg:grid-flow-col-dense" : ""
            }`}
          >
            {/* Brand & Mission */}
            <div
              className={`text-center ${
                isRTL ? "lg:text-right lg:order-2" : "lg:text-left lg:order-1"
              }`}
            >
              <div className="mb-6">
                <h3 className="text-2xl md:text-3xl font-light bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
                  EduLite
                </h3>
                <p
                  className={`text-gray-600 dark:text-gray-300 text-lg font-light leading-relaxed max-w-md ${
                    isRTL ? "mx-auto lg:mr-0" : "mx-auto lg:mx-0"
                  }`}
                >
                  {t("footer.mission")}
                </p>
              </div>

              {/* Mission Statement */}
              <div
                className={`inline-flex items-center gap-2 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-full px-4 py-2 border border-gray-200/50 dark:border-gray-700/50 ${
                  isRTL ? "flex-row-reverse" : ""
                }`}
              >
                <FaHeart className="text-red-500 text-sm animate-pulse" />
                <span className="text-gray-700 dark:text-gray-300 text-sm font-medium">
                  {t("footer.madeWithPassion")}
                </span>
                <FaHeart
                  className="text-red-500 text-sm animate-pulse"
                  style={{ animationDelay: "0.5s" }}
                />
              </div>
            </div>

            {/* Connect Section */}
            <div
              className={`text-center ${
                isRTL ? "lg:text-left lg:order-1" : "lg:text-right lg:order-2"
              }`}
            >
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
                {t("footer.stayConnected")}
              </h4>

              {/* Social Links */}
              <div
                className={`flex items-center gap-3 mb-8 flex-wrap ${
                  isRTL
                    ? "justify-center lg:justify-start"
                    : "justify-center lg:justify-end"
                }`}
              >
                <a
                  href="https://github.com/ibrahim-sisar/EduLite"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group relative w-12 h-12 bg-white dark:bg-gray-800 hover:bg-gradient-to-r hover:from-gray-700 hover:to-gray-900 rounded-xl shadow-sm hover:shadow-lg border border-gray-200 dark:border-gray-700 hover:border-transparent transition-all duration-300 flex items-center justify-center"
                  aria-label={t("footer.socialLabels.github")}
                >
                  <FaGithub className="text-gray-600 dark:text-gray-300 group-hover:text-white text-lg transition-colors duration-300" />
                  <div className="absolute inset-0 bg-gradient-to-r from-gray-700/10 to-gray-900/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </a>

                <a
                  href="#"
                  className="group relative w-12 h-12 bg-white dark:bg-gray-800 hover:bg-gradient-to-r hover:from-black hover:to-gray-800 rounded-xl shadow-sm hover:shadow-lg border border-gray-200 dark:border-gray-700 hover:border-transparent transition-all duration-300 flex items-center justify-center"
                  aria-label={t("footer.socialLabels.twitter")}
                >
                  <FaXTwitter className="text-gray-600 dark:text-gray-300 group-hover:text-white text-lg transition-colors duration-300" />
                  <div className="absolute inset-0 bg-gradient-to-r from-black/10 to-gray-800/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </a>

                <a
                  href="#"
                  className="group relative w-12 h-12 bg-white dark:bg-gray-800 hover:bg-gradient-to-r hover:from-blue-500 hover:to-blue-600 rounded-xl shadow-sm hover:shadow-lg border border-gray-200 dark:border-gray-700 hover:border-transparent transition-all duration-300 flex items-center justify-center"
                  aria-label={t("footer.socialLabels.linkedin")}
                >
                  <FaLinkedinIn className="text-gray-600 dark:text-gray-300 group-hover:text-white text-lg transition-colors duration-300" />
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-blue-600/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </a>

                <a
                  href="#"
                  className="group relative w-12 h-12 bg-white dark:bg-gray-800 hover:bg-gradient-to-r hover:from-blue-600 hover:to-blue-700 rounded-xl shadow-sm hover:shadow-lg border border-gray-200 dark:border-gray-700 hover:border-transparent transition-all duration-300 flex items-center justify-center"
                  aria-label={t("footer.socialLabels.facebook")}
                >
                  <FaFacebookF className="text-gray-600 dark:text-gray-300 group-hover:text-white text-lg transition-colors duration-300" />
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-blue-700/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </a>

                <a
                  href="#"
                  className="group relative w-12 h-12 bg-white dark:bg-gray-800 hover:bg-gradient-to-r hover:from-purple-500 hover:to-purple-600 rounded-xl shadow-sm hover:shadow-lg border border-gray-200 dark:border-gray-700 hover:border-transparent transition-all duration-300 flex items-center justify-center"
                  aria-label={t("footer.socialLabels.email")}
                >
                  <FaEnvelope className="text-gray-600 dark:text-gray-300 group-hover:text-white text-lg transition-colors duration-300" />
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-purple-600/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </a>
              </div>

              {/* Newsletter Signup */}
              <div
                className={`max-w-sm mx-auto ${
                  isRTL ? "lg:mx-0 lg:mr-auto" : "lg:mx-0 lg:ml-auto"
                }`}
              >
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  {t("footer.newsletter.description")}
                </p>
                <div
                  className={`flex rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300 ${
                    isRTL ? "flex-row-reverse" : ""
                  }`}
                >
                  <input
                    type="email"
                    placeholder={t("footer.newsletter.placeholder")}
                    className={`flex-1 px-4 py-3 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none ${
                      isRTL ? "text-right" : "text-left"
                    }`}
                    dir={isRTL ? "rtl" : "ltr"}
                  />
                  <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white text-sm font-medium transition-all duration-300 hover:shadow-lg">
                    {t("footer.newsletter.subscribe")}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="py-6 border-t border-gray-200/50 dark:border-gray-800/50">
          <div
            className={`flex flex-col md:flex-row items-center gap-4 ${
              isRTL ? "md:flex-row-reverse justify-between" : "justify-between"
            }`}
          >
            {/* Copyright */}
            <div
              className={`text-center ${
                isRTL ? "md:text-right" : "md:text-left"
              }`}
            >
              <p className="text-gray-500 dark:text-gray-400 text-sm font-light">
                {t("footer.copyright", { year: new Date().getFullYear() })}
              </p>
            </div>

            {/* Links */}
            <div
              className={`flex items-center gap-6 text-sm ${
                isRTL ? "flex-row-reverse" : ""
              }`}
            >
              <a
                href="#"
                className="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
              >
                {t("footer.links.privacy")}
              </a>
              <a
                href="#"
                className="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
              >
                {t("footer.links.terms")}
              </a>
              <a
                href="#"
                className="text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
              >
                {t("footer.links.support")}
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-transparent to-purple-500/5 pointer-events-none"></div>
    </footer>
  );
};

export default Footer;
