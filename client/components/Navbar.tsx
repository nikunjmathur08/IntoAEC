"use client";

import { FaFolderOpen, FaUpload, FaHome, FaUser } from "react-icons/fa";

export default function Navbar() {
  return (
    <nav
      className="sticky top-0 z-50 bg-white/90 backdrop-blur-xl border-b border-white/20"
      style={{
        boxShadow: "rgba(0, 0, 0, 0.1) 0px 8px 32px",
        background:
          "linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.95) 100%)",
      }}
    >
      {/* Floating decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-2 h-2 bg-blue-400 rounded-full opacity-30 animate-pulse"></div>
        <div
          className="absolute top-1 right-1/3 w-1 h-1 bg-cyan-400 rounded-full opacity-40 animate-bounce"
          style={{ animationDelay: "1s" }}
        ></div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center relative z-10">
        {/* Logo with enhanced styling */}
        <a href="#" className="flex items-center gap-3 group">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-cyan-500 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg transform group-hover:scale-105 transition-all duration-300">
            I
          </div>
          <span
            className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-blue-800 bg-clip-text text-transparent"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            Into<span className="text-cyan-500">AEC</span>
          </span>
        </a>

        {/* Navigation items */}
        <div className="hidden md:flex items-center gap-2">
          <a
            href="#"
            className="flex items-center gap-2 text-slate-600 font-medium px-4 py-2 rounded-xl hover:bg-white/60 hover:text-slate-800 transition-all duration-300 transform hover:scale-105"
            style={{
              fontFamily: "Inter, Poppins, sans-serif",
              fontSize: "14px",
            }}
          >
            <FaHome className="text-sm" />
            <span>Dashboard</span>
          </a>
          <a
            href="#"
            className="flex items-center gap-2 text-slate-600 font-medium px-4 py-2 rounded-xl hover:bg-white/60 hover:text-slate-800 transition-all duration-300 transform hover:scale-105"
            style={{
              fontFamily: "Inter, Poppins, sans-serif",
              fontSize: "14px",
            }}
          >
            <FaFolderOpen className="text-sm" />
            <span>Projects</span>
          </a>
        </div>

        {/* CTA Section */}
        <div className="flex items-center gap-3">
          {/* User avatar */}
          <button
            className="w-9 h-9 bg-gradient-to-br from-slate-100 to-slate-200 rounded-full flex items-center justify-center text-slate-600 hover:bg-gradient-to-br hover:from-slate-200 hover:to-slate-300 transition-all duration-300 transform hover:scale-105"
            style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 2px 8px" }}
          >
            <FaUser className="text-xs" />
          </button>

          {/* Upload button */}
          <button
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold px-6 py-3 rounded-xl flex items-center gap-2 transition-all duration-300 transform hover:scale-105 hover:-translate-y-0.5"
            style={{
              fontFamily: "Inter, Poppins, sans-serif",
              fontSize: "14px",
              boxShadow: "rgba(59, 130, 246, 0.3) 0px 8px 25px",
            }}
            onClick={() => document.getElementById("fileInput")?.click()}
          >
            <FaUpload className="text-sm" />
            <span>Upload</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
