"use client";
import { FaBrain, FaChartLine, FaRocket } from "react-icons/fa";

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      {/* Background with gradient and pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-cyan-50">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-20 h-20 bg-blue-500 rounded-full blur-xl"></div>
          <div className="absolute top-32 right-20 w-32 h-32 bg-cyan-400 rounded-full blur-2xl"></div>
          <div className="absolute bottom-20 left-1/4 w-24 h-24 bg-blue-600 rounded-full blur-xl"></div>
        </div>
      </div>

      {/* Floating geometric shapes */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-1/4 w-4 h-4 bg-blue-400 transform rotate-45 animate-pulse"></div>
        <div
          className="absolute top-40 right-1/3 w-6 h-6 bg-cyan-400 rounded-full animate-bounce"
          style={{ animationDelay: "1s" }}
        ></div>
        <div
          className="absolute bottom-32 right-1/4 w-3 h-3 bg-blue-600 transform rotate-45 animate-pulse"
          style={{ animationDelay: "2s" }}
        ></div>
      </div>

      <div className="relative z-10 text-center max-w-5xl mx-auto py-24 px-4">
        {/* Badge */}
        <div
          className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm border border-blue-100 rounded-full px-4 py-2 mb-8"
          style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 10px" }}
        >
          <FaRocket className="text-blue-600" />
          <span
            className="text-sm font-medium text-slate-700"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            Powered by Advanced AI
          </span>
        </div>

        {/* Main heading with gradient text */}
        <h1
          className="font-bold mb-6 bg-gradient-to-r from-slate-900 via-blue-800 to-slate-900 bg-clip-text text-transparent"
          style={{
            fontFamily: "Inter, Poppins, sans-serif",
            fontSize: "clamp(2.5rem, 5vw, 4.5rem)",
            lineHeight: "1.1",
          }}
        >
          AI-Powered Floor Plan Analysis
        </h1>

        {/* Subtitle */}
        <h2
          className="text-slate-600 mb-8 font-semibold"
          style={{
            fontFamily: "Inter, Poppins, sans-serif",
            fontSize: "clamp(1.25rem, 3vw, 1.75rem)",
            lineHeight: "1.4",
          }}
        >
          Transform blueprints into actionable insights
        </h2>

        {/* Description */}
        <p
          className="text-slate-500 max-w-2xl mx-auto mb-10"
          style={{
            fontFamily: "Inter, Poppins, sans-serif",
            fontSize: "18px",
            lineHeight: "1.7",
          }}
        >
          Upload your architectural drawings and get instant cost analysis,
          material breakdowns, and construction insights powered by advanced AI
          technology.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
          <button
            onClick={() => document.getElementById("fileInput")?.click()}
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold px-8 py-4 rounded-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 flex items-center gap-3"
            style={{
              fontFamily: "Inter, Poppins, sans-serif",
              fontSize: "16px",
              boxShadow: "rgba(59, 130, 246, 0.3) 0px 8px 25px",
            }}
          >
            <FaBrain />
            Start Analysis
          </button>
          <button
            className="bg-white/80 backdrop-blur-sm hover:bg-white text-slate-700 font-semibold px-8 py-4 rounded-xl border border-slate-200 transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 flex items-center gap-3"
            style={{
              fontFamily: "Inter, Poppins, sans-serif",
              fontSize: "16px",
              boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 15px",
            }}
          >
            <FaChartLine />
            View Demo
          </button>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            {
              icon: <FaBrain />,
              title: "AI-Powered",
              desc: "Advanced computer vision technology",
            },
            {
              icon: <FaChartLine />,
              title: "Instant Results",
              desc: "Get analysis in seconds",
            },
            {
              icon: <FaRocket />,
              title: "Easy to Use",
              desc: "Just upload and analyze",
            },
          ].map((feature, idx) => (
            <div
              key={idx}
              className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-white/50 transition-all duration-300 hover:bg-white/80 hover:scale-105"
              style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 15px" }}
            >
              <div className="text-blue-600 text-2xl mb-3 flex justify-center">
                {feature.icon}
              </div>
              <h3
                className="font-bold text-slate-800 mb-2"
                style={{
                  fontFamily: "Inter, Poppins, sans-serif",
                  fontSize: "16px",
                }}
              >
                {feature.title}
              </h3>
              <p
                className="text-slate-600 text-sm"
                style={{ fontFamily: "Inter, Poppins, sans-serif" }}
              >
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
