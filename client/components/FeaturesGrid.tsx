import {
  FaBrain,
  FaCalculator,
  FaChartBar,
  FaRulerCombined,
  FaLayerGroup,
  FaShareAlt,
  FaCloud,
  FaLock,
  FaCogs,
  FaUsers,
  FaMobileAlt,
  FaHistory,
  FaSearch,
  FaBolt,
  FaHeadset,
} from "react-icons/fa";

const features = [
  {
    icon: <FaBrain />,
    title: "AI Analysis",
    desc: "Computer vision identifies rooms, walls, and more.",
  },
  {
    icon: <FaCalculator />,
    title: "Cost Estimation",
    desc: "Get material and cost breakdowns instantly.",
  },
  {
    icon: <FaChartBar />,
    title: "Smart Insights",
    desc: "Optimize design and reduce project costs.",
  },
  {
    icon: <FaRulerCombined />,
    title: "Auto Measurements",
    desc: "Extract room sizes and areas automatically.",
  },
  {
    icon: <FaLayerGroup />,
    title: "Layer Detection",
    desc: "Detects walls, doors, windows, furniture, etc.",
  },
  {
    icon: <FaCloud />,
    title: "Cloud Storage",
    desc: "Access all your files securely from anywhere.",
  },
];

export default function FeaturesGrid() {
  return (
    <section className="relative py-20 px-6 overflow-hidden">
      {/* Background with gradient and patterns */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-20 left-10 w-32 h-32 bg-blue-500 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-10 w-40 h-40 bg-cyan-400 rounded-full blur-3xl"></div>
        </div>
      </div>

      {/* Floating decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-32 left-1/4 w-3 h-3 bg-blue-400 rounded-full opacity-30 animate-pulse"></div>
        <div
          className="absolute top-64 right-1/4 w-2 h-2 bg-cyan-400 rounded-full opacity-40 animate-bounce"
          style={{ animationDelay: "2s" }}
        ></div>
        <div
          className="absolute bottom-32 left-1/3 w-4 h-4 bg-blue-600 transform rotate-45 opacity-20 animate-pulse"
          style={{ animationDelay: "1s" }}
        ></div>
      </div>

      <div className="relative z-10 max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div
            className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm border border-blue-100 rounded-full px-4 py-2 mb-6"
            style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 4px 10px" }}
          >
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
            <span
              className="text-sm font-medium text-slate-700"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Powerful Features
            </span>
          </div>
          <h2
            className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-900 to-blue-800 bg-clip-text text-transparent mb-4"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            Everything you need for AI analysis
          </h2>
          <p
            className="text-slate-600 max-w-2xl mx-auto"
            style={{
              fontFamily: "Inter, Poppins, sans-serif",
              fontSize: "16px",
            }}
          >
            Our advanced AI technology provides comprehensive analysis of your
            architectural drawings
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="group bg-white/70 backdrop-blur-sm text-slate-800 font-medium rounded-2xl p-8 transition-all duration-500 hover:-translate-y-3 hover:bg-white/90 cursor-pointer border border-white/50"
              style={{
                boxShadow: "rgba(0, 0, 0, 0.1) 0px 8px 30px",
                fontFamily: "Inter, Poppins, sans-serif",
              }}
            >
              {/* Icon with enhanced styling */}
              <div className="relative mb-6">
                <div
                  className="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl transition-all duration-500 group-hover:scale-110 group-hover:rotate-6"
                  style={{
                    backgroundColor: "#0066CC",
                    boxShadow: "rgba(0, 102, 204, 0.3) 0px 8px 25px",
                  }}
                >
                  {feature.icon}
                </div>
                {/* Glow effect */}
                <div
                  className="absolute inset-0 w-16 h-16 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity duration-500"
                  style={{ backgroundColor: "#0066CC", filter: "blur(10px)" }}
                ></div>
              </div>

              {/* Content */}
              <h3
                className="font-bold text-slate-800 mb-3 group-hover:text-blue-800 transition-colors duration-300"
                style={{
                  fontSize: "20px",
                  lineHeight: "1.4",
                }}
              >
                {feature.title}
              </h3>
              <p
                className="text-slate-600 group-hover:text-slate-700 transition-colors duration-300"
                style={{
                  fontSize: "15px",
                  lineHeight: "1.6",
                  fontWeight: "500",
                }}
              >
                {feature.desc}
              </p>

              {/* Hover indicator */}
              <div className="mt-6 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-x-2 group-hover:translate-x-0">
                <div className="w-1 h-1 bg-blue-600 rounded-full"></div>
                <div className="w-2 h-1 bg-blue-600 rounded-full"></div>
                <div className="w-4 h-1 bg-blue-600 rounded-full"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
