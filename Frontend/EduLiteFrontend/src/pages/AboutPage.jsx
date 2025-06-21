import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import {
  FaHeart,
  FaGlobe,
  FaUsers,
  FaLightbulb,
  FaArrowLeft,
  FaArrowRight,
  FaRocket,
  FaComments,
  FaBookOpen,
  FaShieldAlt,
  FaGraduationCap,
  FaCode,
  FaHandsHelping,
} from "react-icons/fa";

const AboutPage = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === "ar";

  return (
    <div
      className={`text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900 min-h-screen overflow-hidden ${
        isRTL ? "rtl" : "ltr"
      }`}
    >
      {/* Apple-Style Hero Section - Mobile Responsive */}
      <section
        className="relative min-h-screen flex items-center justify-center px-4 sm:px-6 md:px-16 overflow-hidden pt-20"
        style={{ minHeight: "calc(100vh - 0px)" }}
      >
        <div className="max-w-6xl mx-auto w-full">
          {/* Hero Content */}
          <div className="text-center">
            {/* Floating Icon - Properly Responsive */}
            <div className="mb-8 sm:mb-12 md:mb-8 mt-6 md:mt-12 lg:mt-16">
              <div className="inline-flex items-center justify-center w-24 h-24 sm:w-24 sm:h-24 md:w-28 md:h-28 lg:w-36 lg:h-36 bg-gray-100 dark:bg-gray-800 rounded-2xl sm:rounded-3xl mb-6 sm:mb-8 shadow-lg dark:shadow-gray-900/20 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/30">
                <FaGraduationCap className="text-gray-600 dark:text-gray-400 text-6xl sm:text-6xl md:text-6xl lg:text-8xl fill-black dark:fill-white" />
              </div>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-6xl md:text-7xl lg:text-9xl font-light text-gray-900 dark:text-white mb-6 sm:mb-8 md:mb-12 tracking-tight leading-tight sm:leading-none">
              {t("about.title")}
            </h1>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl md:text-3xl lg:text-4xl text-gray-500 dark:text-gray-400 font-light leading-relaxed max-w-2xl sm:max-w-4xl lg:max-w-5xl mx-auto mb-10 sm:mb-16 md:mb-20 px-2">
              {t("about.subtitle")}
            </p>

            {/* Feature Pills - Fixed RTL alignment */}
            <div className="flex flex-col sm:flex-row flex-wrap justify-center gap-3 sm:gap-4 md:gap-6 mb-12 sm:mb-16 md:mb-20 px-2">
              <div className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 rounded-full px-4 sm:px-6 py-2 sm:py-3 border border-gray-100 dark:border-gray-800">
                <FaUsers
                  className={`text-white text-sm sm:text-lg ${
                    isRTL ? "ml-2 sm:ml-3" : "mr-2 sm:mr-3"
                  }`}
                />
                <span className="text-white font-light text-sm sm:text-base">
                  {t("about.heroFeature1")}
                </span>
              </div>
              <div className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 rounded-full px-4 sm:px-6 py-2 sm:py-3 border border-gray-100 dark:border-gray-800">
                <FaGlobe
                  className={`text-white text-sm sm:text-lg ${
                    isRTL ? "ml-2 sm:ml-3" : "mr-2 sm:mr-3"
                  }`}
                />
                <span className="text-white font-light text-sm sm:text-base">
                  {t("about.heroFeature2")}
                </span>
              </div>
              <div className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 rounded-full px-4 sm:px-6 py-2 sm:py-3 border border-gray-100 dark:border-gray-800">
                <FaRocket
                  className={`text-white text-sm sm:text-lg ${
                    isRTL ? "ml-2 sm:ml-3" : "mr-2 sm:mr-3"
                  }`}
                />
                <span className="text-white font-light text-sm sm:text-base">
                  {t("about.heroFeature3")}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Hero Story Section - Apple Style */}
      <section className="relative px-6 md:px-12 py-28 bg-white dark:bg-black">
        <div className="max-w-6xl mx-auto">
          {/* Minimalist Header */}
          <div className="text-center mb-32">
            <div className="mb-12">
              <div className="inline-flex items-center justify-center w-28 h-28 md:w-32 md:h-32 rounded-full bg-amber-100 dark:bg-gray-900 mb-8">
                <FaLightbulb className="text-gray-600 dark:text-gray-400 text-5xl md:text-6xl fill-amber-400" />
              </div>
            </div>
            <h2 className="text-6xl md:text-8xl font-light text-gray-900 dark:text-white mb-8 tracking-tight">
              {t("about.storyTitle")}
            </h2>
            <p className="text-2xl md:text-3xl text-gray-500 dark:text-gray-400 font-light max-w-4xl mx-auto leading-relaxed">
              {t("about.storySubtitle")}
            </p>
          </div>

          {/* Apple-style Timeline */}
          <div className="space-y-32">
            {/* 2020 - Pandemic */}
            <div className="relative">
              <div className="max-w-4xl mx-auto">
                <div className="grid md:grid-cols-2 gap-16 items-center">
                  <div
                    className={`${
                      isRTL ? "order-1 md:order-2" : "order-2 md:order-1"
                    }`}
                  >
                    <div className="inline-block px-4 py-2 bg-red-50 dark:bg-red-900/20 rounded-full mb-8">
                      <span className="text-red-600 dark:text-red-400 text-sm font-medium">
                        {t("about.timeline.pandemic.year")}
                      </span>
                    </div>
                    <h3 className="text-4xl md:text-5xl font-light text-gray-900 dark:text-white mb-8 leading-tight">
                      {t("about.timeline.pandemic.title")}
                    </h3>
                    <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed font-light">
                      {t("about.timeline.pandemic.description")}
                    </p>
                  </div>
                  <div
                    className={`${
                      isRTL ? "order-2 md:order-1" : "order-1 md:order-2"
                    }`}
                  >
                    <div className="relative">
                      <div className="w-full h-80 bg-gradient-to-br from-red-100 to-red-200 dark:from-red-900/20 dark:to-red-800/20 rounded-3xl flex items-center justify-center backdrop-blur-sm">
                        <div className="w-32 h-32 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-2xl">
                          <FaGraduationCap className="text-4xl text-red-500" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Connector Line */}
            <div className="flex justify-center">
              <div className="w-px h-24 bg-gradient-to-b from-gray-200 to-gray-100 dark:from-gray-700 dark:to-gray-800"></div>
            </div>

            {/* 2023 - Gaza */}
            <div className="relative">
              <div className="max-w-4xl mx-auto">
                <div className="grid md:grid-cols-2 gap-16 items-center">
                  <div>
                    <div className="relative">
                      <div className="w-full h-80 bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 rounded-3xl flex items-center justify-center backdrop-blur-sm">
                        <div className="w-32 h-32 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-2xl">
                          <FaHeart className="text-4xl text-blue-500" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="inline-block px-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-full mb-8">
                      <span className="text-blue-600 dark:text-blue-400 text-sm font-medium">
                        {t("about.timeline.gaza.year")}
                      </span>
                    </div>
                    <h3 className="text-4xl md:text-5xl font-light text-gray-900 dark:text-white mb-8 leading-tight">
                      {t("about.timeline.gaza.title")}
                    </h3>
                    <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed font-light mb-8">
                      {t("about.timeline.gaza.description")}
                    </p>

                    {/* Apple-style Quote Block */}
                    <div className="relative p-8 bg-gray-50 dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800">
                      <div
                        className={`absolute -top-2 w-4 h-4 bg-amber-400 rounded-full ${
                          isRTL ? "-right-2" : "-left-2"
                        }`}
                      ></div>
                      <blockquote className="text-2xl text-gray-800 dark:text-gray-200 font-light italic leading-relaxed">
                        "{t("about.educationQuote")}"
                      </blockquote>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Connector Line */}
            <div className="flex justify-center">
              <div className="w-px h-24 bg-gradient-to-b from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700"></div>
            </div>

            {/* Solution */}
            <div className="relative">
              <div className="max-w-4xl mx-auto">
                <div className="grid md:grid-cols-2 gap-16 items-center">
                  <div
                    className={`${
                      isRTL ? "order-1 md:order-2" : "order-2 md:order-1"
                    }`}
                  >
                    <div className="inline-block px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-full mb-8">
                      <span className="text-green-600 dark:text-green-400 text-sm font-medium">
                        {t("about.timeline.solution.year")}
                      </span>
                    </div>
                    <h3 className="text-4xl md:text-5xl font-light text-gray-900 dark:text-white mb-8 leading-tight">
                      {t("about.timeline.solution.title")}
                    </h3>
                    <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed font-light">
                      {t("about.timeline.solution.description")}
                    </p>
                  </div>
                  <div
                    className={`${
                      isRTL ? "order-2 md:order-1" : "order-1 md:order-2"
                    }`}
                  >
                    <div className="relative">
                      <div className="w-full h-80 bg-gradient-to-br from-green-100 to-green-200 dark:from-green-900/20 dark:to-green-800/20 rounded-3xl flex items-center justify-center backdrop-blur-sm">
                        <div className="w-32 h-32 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-2xl">
                          <FaRocket className="text-4xl text-green-500" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Apple-style Bottom CTA */}
          <div className="text-center mt-32 pt-32 border-t border-gray-100 dark:border-gray-800">
            <h3 className="text-3xl md:text-4xl font-light text-gray-900 dark:text-white mb-8">
              {t("about.readyToJoin")}
            </h3>
            <p className="text-xl text-gray-500 dark:text-gray-400 font-light mb-12 max-w-2xl mx-auto">
              {t("about.experienceEducation")}
            </p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-12 py-4 rounded-full text-lg font-medium transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl">
              {t("about.getStarted")}
            </button>
          </div>
        </div>
      </section>

      {/* Apple-Style Mission Section */}
      <section className="relative px-6 md:px-12 py-32 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          {/* Mission Header */}
          <div className="text-center mb-24">
            <h2 className="text-6xl md:text-7xl font-light text-gray-900 dark:text-white mb-8 tracking-tight">
              {t("about.missionTitle")}
            </h2>
            <p className="text-2xl text-gray-500 dark:text-gray-400 font-light max-w-3xl mx-auto leading-relaxed">
              {t("about.missionSubtitle")}
            </p>
          </div>

          {/* Mission Cards - Apple Style */}
          <div className="space-y-20">
            {/* Mission 1 - Community Building */}
            <div className="relative">
              <div className="max-w-5xl mx-auto">
                <div className="bg-white dark:bg-black rounded-3xl overflow-hidden shadow-sm border border-gray-100 dark:border-gray-800">
                  <div className="grid md:grid-cols-2">
                    {/* Content */}
                    <div className="p-12 md:p-16 flex flex-col justify-center">
                      <div className="mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-2xl mb-6">
                          <FaUsers className="text-blue-600 dark:text-blue-400 text-2xl" />
                        </div>
                        <h3 className="text-4xl md:text-5xl font-light text-gray-900 dark:text-white mb-6 leading-tight">
                          {t("about.mission.community.title")}
                        </h3>
                      </div>
                      <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed font-light">
                        {t("about.mission.community.description")}
                      </p>
                    </div>

                    {/* Visual */}
                    <div className="relative h-80 md:h-auto">
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-100 via-blue-50 to-purple-100 dark:from-blue-900/20 dark:via-blue-800/10 dark:to-purple-900/20">
                        <div className="absolute inset-0 flex items-center justify-center">
                          {/* Floating Community Elements */}
                          <div className="relative w-48 h-48">
                            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-12 h-12 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center">
                              <FaUsers className="text-blue-500 text-lg" />
                            </div>
                            <div className="absolute top-16 left-8 w-10 h-10 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center">
                              <FaUsers className="text-blue-400 text-sm" />
                            </div>
                            <div className="absolute top-16 right-8 w-10 h-10 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center">
                              <FaUsers className="text-blue-400 text-sm" />
                            </div>
                            <div className="absolute bottom-8 left-1/4 w-8 h-8 bg-white dark:bg-gray-800 rounded-full shadow-md flex items-center justify-center">
                              <FaUsers className="text-blue-300 text-xs" />
                            </div>
                            <div className="absolute bottom-8 right-1/4 w-8 h-8 bg-white dark:bg-gray-800 rounded-full shadow-md flex items-center justify-center">
                              <FaUsers className="text-blue-300 text-xs" />
                            </div>
                            {/* Connection Lines */}
                            <div className="absolute top-6 left-1/2 w-px h-8 bg-blue-200 dark:bg-blue-700 transform -translate-x-1/2"></div>
                            <div className="absolute top-12 left-1/2 w-16 h-px bg-blue-200 dark:bg-blue-700 transform -translate-x-1/2 rotate-45"></div>
                            <div className="absolute top-12 left-1/2 w-16 h-px bg-blue-200 dark:bg-blue-700 transform -translate-x-1/2 -rotate-45"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Mission 2 - Global Accessibility */}
            <div className="relative">
              <div className="max-w-5xl mx-auto">
                <div className="bg-white dark:bg-black rounded-3xl overflow-hidden shadow-sm border border-gray-100 dark:border-gray-800">
                  <div className="grid md:grid-cols-2">
                    {/* Visual */}
                    <div
                      className={`relative h-80 md:h-auto ${
                        isRTL ? "order-1 md:order-2" : "order-2 md:order-1"
                      }`}
                    >
                      <div className="absolute inset-0 bg-gradient-to-br from-green-100 via-green-50 to-teal-100 dark:from-green-900/20 dark:via-green-800/10 dark:to-teal-900/20">
                        <div className="absolute inset-0 flex items-center justify-center">
                          {/* Globe with Connection Points */}
                          <div className="relative w-48 h-48">
                            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 bg-white dark:bg-gray-800 rounded-full shadow-lg flex items-center justify-center">
                              <FaGlobe className="text-green-500 text-3xl" />
                            </div>
                            {/* Orbiting Elements */}
                            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 w-8 h-8 bg-white dark:bg-gray-800 rounded-full shadow-md flex items-center justify-center">
                              <FaGraduationCap className="text-green-400 text-sm" />
                            </div>
                            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-8 h-8 bg-white dark:bg-gray-800 rounded-full shadow-md flex items-center justify-center">
                              <FaGraduationCap className="text-green-400 text-sm" />
                            </div>
                            <div className="absolute top-1/2 left-4 transform -translate-y-1/2 w-8 h-8 bg-white dark:bg-gray-800 rounded-full shadow-md flex items-center justify-center">
                              <FaGraduationCap className="text-green-400 text-sm" />
                            </div>
                            <div className="absolute top-1/2 right-4 transform -translate-y-1/2 w-8 h-8 bg-white dark:bg-gray-800 rounded-full shadow-md flex items-center justify-center">
                              <FaGraduationCap className="text-green-400 text-sm" />
                            </div>
                            {/* Orbital Lines */}
                            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-40 h-40 border border-green-200 dark:border-green-700 rounded-full opacity-30"></div>
                            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 border border-green-300 dark:border-green-600 rounded-full opacity-40"></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Content */}
                    <div
                      className={`p-12 md:p-16 flex flex-col justify-center ${
                        isRTL ? "order-2 md:order-1" : "order-1 md:order-2"
                      }`}
                    >
                      <div className="mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-2xl mb-6">
                          <FaGlobe className="text-green-600 dark:text-green-400 text-2xl" />
                        </div>
                        <h3 className="text-4xl md:text-5xl font-light text-gray-900 dark:text-white mb-6 leading-tight">
                          {t("about.mission.access.title")}
                        </h3>
                      </div>
                      <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed font-light">
                        {t("about.mission.access.description")}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Mission Statement */}
          <div className="text-center mt-32 pt-20">
            <div className="max-w-4xl mx-auto">
              <p className="text-3xl md:text-4xl font-light text-gray-800 dark:text-gray-200 leading-relaxed mb-12">
                "{t("about.bridgeQuote")}"
              </p>
              <p className="text-xl text-gray-500 dark:text-gray-400 font-light leading-relaxed">
                {t("about.bridgeDescription")}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Apple-Style Features Section */}
      <section className="relative px-6 md:px-12 py-32 bg-white dark:bg-black">
        <div className="max-w-7xl mx-auto">
          {/* Features Header */}
          <div className="text-center mb-24">
            <h2 className="text-6xl md:text-7xl font-light text-gray-900 dark:text-white mb-8 tracking-tight">
              {t("about.featuresTitle")}
            </h2>
            <p className="text-2xl text-gray-500 dark:text-gray-400 font-light max-w-4xl mx-auto leading-relaxed">
              {t("about.featuresSubtitle")}
            </p>
          </div>

          {/* Features Grid - Apple Style */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-20">
            {/* Feature 1 - Interactive Learning */}
            <div className="group">
              <div className="bg-gray-50 dark:bg-gray-900 rounded-3xl overflow-hidden h-full border border-gray-100 dark:border-gray-800 hover:shadow-lg transition-all duration-500">
                <div className="p-12">
                  {/* Icon Header */}
                  <div className="mb-8">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-orange-100 to-red-100 dark:from-orange-900/30 dark:to-red-900/30 rounded-2xl mb-6">
                      <FaRocket className="text-orange-500 text-3xl" />
                    </div>
                    <h3 className="text-3xl md:text-4xl font-light text-gray-900 dark:text-white mb-4 leading-tight">
                      {t("about.features.interactive.title")}
                    </h3>
                  </div>

                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed font-light mb-8">
                    {t("about.features.interactive.description")}
                  </p>

                  {/* Visual Element */}
                  <div className="relative h-40 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/10 dark:to-red-900/10 rounded-2xl flex items-center justify-center">
                    <div className="relative">
                      {/* Animated Elements */}
                      <div className="flex space-x-4">
                        <div className="w-12 h-12 bg-white dark:bg-gray-800 rounded-xl shadow-lg flex items-center justify-center transform hover:scale-110 transition-transform duration-300">
                          <FaRocket className="text-orange-500 text-lg" />
                        </div>
                        <div
                          className="w-12 h-12 bg-white dark:bg-gray-800 rounded-xl shadow-lg flex items-center justify-center transform hover:scale-110 transition-transform duration-300"
                          style={{ animationDelay: "0.1s" }}
                        >
                          <FaBookOpen className="text-orange-400 text-lg" />
                        </div>
                        <div
                          className="w-12 h-12 bg-white dark:bg-gray-800 rounded-xl shadow-lg flex items-center justify-center transform hover:scale-110 transition-transform duration-300"
                          style={{ animationDelay: "0.2s" }}
                        >
                          <FaGraduationCap className="text-orange-400 text-lg" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Feature 2 - Real-time Collaboration */}
            <div className="group">
              <div className="bg-gray-50 dark:bg-gray-900 rounded-3xl overflow-hidden h-full border border-gray-100 dark:border-gray-800 hover:shadow-lg transition-all duration-500">
                <div className="p-12">
                  {/* Icon Header */}
                  <div className="mb-8">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-2xl mb-6">
                      <FaComments className="text-blue-500 text-3xl" />
                    </div>
                    <h3 className="text-3xl md:text-4xl font-light text-gray-900 dark:text-white mb-4 leading-tight">
                      {t("about.features.collaboration.title")}
                    </h3>
                  </div>

                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed font-light mb-8">
                    {t("about.features.collaboration.description")}
                  </p>

                  {/* Visual Element */}
                  <div className="relative h-40 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/10 dark:to-purple-900/10 rounded-2xl flex items-center justify-center">
                    <div className="relative w-full">
                      {/* Chat Bubbles */}
                      <div className="space-y-3">
                        <div
                          className={`flex ${
                            isRTL ? "justify-end" : "justify-start"
                          }`}
                        >
                          <div className="bg-white dark:bg-gray-800 rounded-2xl px-4 py-2 shadow-sm max-w-32">
                            <div className="flex items-center space-x-2">
                              <FaUsers className="text-blue-400 text-sm" />
                              <div className="w-12 h-2 bg-gray-200 dark:bg-gray-600 rounded"></div>
                            </div>
                          </div>
                        </div>
                        <div
                          className={`flex ${
                            isRTL ? "justify-start" : "justify-end"
                          }`}
                        >
                          <div className="bg-blue-500 rounded-2xl px-4 py-2 shadow-sm max-w-32">
                            <div className="flex items-center space-x-2">
                              <div className="w-16 h-2 bg-blue-300 rounded"></div>
                              <FaComments className="text-white text-sm" />
                            </div>
                          </div>
                        </div>
                        <div
                          className={`flex ${
                            isRTL ? "justify-end" : "justify-start"
                          }`}
                        >
                          <div className="bg-white dark:bg-gray-800 rounded-2xl px-4 py-2 shadow-sm max-w-28">
                            <div className="flex items-center space-x-2">
                              <FaHeart className="text-red-400 text-sm" />
                              <div className="w-8 h-2 bg-gray-200 dark:bg-gray-600 rounded"></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Feature 3 - Rich Content Library */}
            <div className="group">
              <div className="bg-gray-50 dark:bg-gray-900 rounded-3xl overflow-hidden h-full border border-gray-100 dark:border-gray-800 hover:shadow-lg transition-all duration-500">
                <div className="p-12">
                  {/* Icon Header */}
                  <div className="mb-8">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-100 to-teal-100 dark:from-green-900/30 dark:to-teal-900/30 rounded-2xl mb-6">
                      <FaBookOpen className="text-green-500 text-3xl" />
                    </div>
                    <h3 className="text-3xl md:text-4xl font-light text-gray-900 dark:text-white mb-4 leading-tight">
                      {t("about.features.content.title")}
                    </h3>
                  </div>

                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed font-light mb-8">
                    {t("about.features.content.description")}
                  </p>

                  {/* Visual Element */}
                  <div className="relative h-40 bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/10 dark:to-teal-900/10 rounded-2xl flex items-center justify-center">
                    <div className="relative">
                      {/* Book Stack */}
                      <div className="flex items-end space-x-2">
                        <div className="w-8 h-20 bg-green-400 rounded-t-lg shadow-lg transform rotate-2"></div>
                        <div className="w-8 h-24 bg-green-500 rounded-t-lg shadow-lg flex items-center justify-center">
                          <FaBookOpen className="text-white text-sm" />
                        </div>
                        <div className="w-8 h-16 bg-green-300 rounded-t-lg shadow-lg transform -rotate-1"></div>
                        <div className="w-8 h-28 bg-teal-500 rounded-t-lg shadow-lg transform rotate-1"></div>
                        <div className="w-8 h-18 bg-teal-400 rounded-t-lg shadow-lg"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Feature 4 - Safe Learning Environment */}
            <div className="group">
              <div className="bg-gray-50 dark:bg-gray-900 rounded-3xl overflow-hidden h-full border border-gray-100 dark:border-gray-800 hover:shadow-lg transition-all duration-500">
                <div className="p-12">
                  {/* Icon Header */}
                  <div className="mb-8">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-2xl mb-6">
                      <FaShieldAlt className="text-purple-500 text-3xl" />
                    </div>
                    <h3 className="text-3xl md:text-4xl font-light text-gray-900 dark:text-white mb-4 leading-tight">
                      {t("about.features.safety.title")}
                    </h3>
                  </div>

                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed font-light mb-8">
                    {t("about.features.safety.description")}
                  </p>

                  {/* Visual Element */}
                  <div className="relative h-40 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/10 dark:to-pink-900/10 rounded-2xl flex items-center justify-center">
                    <div className="relative">
                      {/* Shield with Protection Elements */}
                      <div className="relative">
                        <div className="w-20 h-24 bg-white dark:bg-gray-800 rounded-t-full rounded-b-lg shadow-lg flex items-center justify-center">
                          <FaShieldAlt className="text-purple-500 text-2xl" />
                        </div>
                        {/* Floating Protection Icons */}
                        <div className="absolute -top-2 -left-6 w-6 h-6 bg-purple-100 dark:bg-purple-900/50 rounded-full flex items-center justify-center">
                          <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                        </div>
                        <div className="absolute top-4 -right-6 w-6 h-6 bg-pink-100 dark:bg-pink-900/50 rounded-full flex items-center justify-center">
                          <div className="w-2 h-2 bg-pink-400 rounded-full"></div>
                        </div>
                        <div className="absolute bottom-2 -left-4 w-6 h-6 bg-purple-100 dark:bg-purple-900/50 rounded-full flex items-center justify-center">
                          <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                        </div>
                        <div className="absolute bottom-4 -right-4 w-6 h-6 bg-pink-100 dark:bg-pink-900/50 rounded-full flex items-center justify-center">
                          <div className="w-2 h-2 bg-pink-400 rounded-full"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Statement */}
          <div className="text-center pt-16 border-t border-gray-100 dark:border-gray-800">
            <div className="max-w-4xl mx-auto">
              <p className="text-2xl md:text-3xl font-light text-gray-800 dark:text-gray-200 leading-relaxed mb-8">
                "{t("about.technologyQuote")}"
              </p>
              <p className="text-lg text-gray-500 dark:text-gray-400 font-light leading-relaxed">
                {t("about.technologyDescription")}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Community Section - Apple Style */}
      <section className="relative px-6 md:px-12 py-32 bg-gray-50 dark:bg-gray-900">
        {/* Subtle Background Pattern */}
        <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 via-transparent to-pink-500/5 pointer-events-none"></div>

        <div className="relative max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-20">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-red-500 to-pink-500 rounded-3xl mb-12 shadow-xl">
              <FaHeart className="text-white text-3xl" />
            </div>
            <h2 className="text-6xl md:text-7xl font-light text-gray-900 dark:text-white mb-8 tracking-tight">
              {t("about.communityTitle")}
            </h2>
            <p className="text-2xl text-gray-500 dark:text-gray-400 font-light max-w-4xl mx-auto leading-relaxed">
              {t("about.communitySubtitle")}
            </p>
          </div>

          {/* Content Cards */}
          <div className="space-y-8">
            {/* Main Description Card */}
            <div className="bg-white dark:bg-black rounded-3xl p-12 md:p-16 shadow-sm border border-gray-100 dark:border-gray-800">
              <p className="text-xl md:text-2xl text-gray-700 dark:text-gray-300 leading-relaxed font-light mb-8 text-center">
                {t("about.communityDescription")}
              </p>
              <p className="text-lg text-gray-500 dark:text-gray-400 leading-relaxed font-light italic text-center">
                {t("about.communityOrigin")}
              </p>
            </div>

            {/* CTA Card */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl p-12 md:p-16 text-white shadow-xl">
              <div className="text-center">
                <h3 className="text-3xl md:text-4xl font-light mb-6">
                  {t("about.joinTitle")}
                </h3>
                <p className="text-xl opacity-90 leading-relaxed mb-12 max-w-3xl mx-auto">
                  {t("about.joinDescription")}
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <a
                    href="https://github.com/ibrahim-sisar/EduLite"
                    target="_blank"
                    rel="noreferrer"
                    className="bg-white text-blue-600 px-10 py-4 rounded-full text-lg font-medium hover:bg-gray-100 transition-all duration-300 hover:scale-105 shadow-lg flex items-center justify-center group"
                  >
                    {t("about.contributeButton")}
                    {isRTL ? (
                      <FaArrowRight
                        className={`${
                          isRTL ? "mr-3" : "ml-3"
                        } text-sm group-hover:${
                          isRTL ? "translate-x-1" : "-translate-x-1"
                        } transition-transform duration-300`}
                      />
                    ) : (
                      <FaArrowLeft
                        className={`${
                          isRTL ? "mr-3" : "ml-3"
                        } text-sm group-hover:${
                          isRTL ? "translate-x-1" : "-translate-x-1"
                        } transition-transform duration-300 rotate-180`}
                      />
                    )}
                  </a>
                  <Link
                    to="/"
                    className="bg-white/10 backdrop-blur-sm text-white px-10 py-4 rounded-full text-lg font-medium hover:bg-white/20 transition-all duration-300 hover:scale-105 border border-white/20"
                  >
                    {t("about.backToHomeButton")}
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final Quote Section - Apple Style */}
      <section className="relative px-6 md:px-12 py-32 bg-white dark:bg-black">
        <div className="max-w-5xl mx-auto text-center">
          {/* Quote Card */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded-3xl p-12 md:p-20 border border-gray-100 dark:border-gray-800">
            <div className="mb-8">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mx-auto mb-8 flex items-center justify-center">
                <span className="text-white text-2xl font-light">"</span>
              </div>
            </div>
            <blockquote className="text-3xl md:text-4xl font-light text-gray-800 dark:text-gray-200 leading-relaxed italic mb-8">
              {t("about.finalQuote")}
            </blockquote>
            <div className="text-lg text-gray-500 dark:text-gray-400 font-light">
              {t("about.teamSignature")}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
