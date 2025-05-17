import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { FaFacebookF, FaLinkedinIn, FaEnvelope, FaCheckCircle } from "react-icons/fa";
import heroImg from "../assets/heroimg.png"; 

const Home = () => {
  const { t } = useTranslation();

  return (
    <div className="text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900">

      {/* Hero Section */}
      <section className="flex flex-col lg:flex-row items-center justify-between px-6 md:px-16 py-12 gap-10">
        <div className="lg:w-1/2 space-y-6">
          <h1 className="text-4xl md:text-5xl font-bold leading-tight">
            {t("home.title")}
          </h1>
          <p className="text-lg">{t("home.intro")}</p>
          <Link
            to="/login"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition"
          >
            {t("home.loginNow")}
          </Link>
        </div>
        <div className="lg:w-1/2">
          <img src={heroImg} alt="EduLite Illustration" className="w-full max-w-md mx-auto" />
        </div>
      </section>

      {/* About and Features */}
      <section className="bg-gray-50 dark:bg-gray-800 px-6 md:px-16 py-12 space-y-10">
        <div>
          <h2 className="text-3xl font-semibold mb-4">About EduLite</h2>
          <p className="text-gray-600 dark:text-gray-300 max-w-3xl">
            {t("home.about")}
          </p>
        </div>
        <div>
          <h2 className="text-2xl font-semibold mb-6">{t("home.featuresTitle")}</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {Object.entries(t("home.features", { returnObjects: true })).map(([key, value]) => (
              <div key={key} className="flex items-center gap-3 text-lg">
                <FaCheckCircle className="text-blue-600" />
                <span>{value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Open Source Section */}
      <section className="bg-blue-50 dark:bg-blue-900 px-6 md:px-16 py-12 space-y-6 text-center">
        <h2 className="text-2xl font-semibold">{t("home.openSourceTitle")}</h2>
        <p className="max-w-2xl mx-auto text-gray-700 dark:text-gray-200">
          {t("home.openSourceText")}
        </p>
        <a
          href="https://github.com/ibrahim-sisar/EduLite/blob/main/README.md"
          target="_blank"
          rel="noreferrer"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition"
        >
          {t("home.joinGithub")}
        </a>
      </section>

      {/* Footer */}
      <footer className="bg-gray-100 dark:bg-gray-800 px-6 md:px-16 py-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-600 dark:text-gray-300">
        <p>© 2025 EduLite. All rights reserved.</p>
        <div className="flex items-center gap-4 text-lg">
          <a href="#" className="hover:text-blue-600"><FaLinkedinIn /></a>
          <a href="#" className="hover:text-blue-600"><FaFacebookF /></a>
          <a href="#" className="hover:text-blue-600"><FaEnvelope /></a>
        </div>
      </footer>
    </div>
  );
};

export default Home;
