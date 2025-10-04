"use client";

import React from "react";
import { FaArrowLeft, FaDownload, FaPrint } from "react-icons/fa";

interface EstimationHeaderProps {
  onBack?: () => void;
  onExport?: () => void;
}

export default function EstimationHeader({
  onBack,
  onExport,
}: EstimationHeaderProps) {
  return (
    <div className="max-w-7xl mx-auto mb-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-slate-600 hover:text-blue-600 transition-colors duration-300 mb-4"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            <FaArrowLeft />
            <span>Back to Analysis</span>
          </button>
          <h1
            className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-slate-900 to-blue-800 bg-clip-text text-transparent"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            Cost Estimation Report
          </h1>
          <p
            className="text-slate-600 mt-2"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            Detailed breakdown of construction costs
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onExport}
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold px-4 py-2 rounded-xl transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
            style={{
              fontFamily: "Inter, Poppins, sans-serif",
              boxShadow: "rgba(59, 130, 246, 0.3) 0px 8px 25px",
            }}
          >
            <FaDownload className="text-sm" />
            Export as JSON
          </button>
        </div>
      </div>
    </div>
  );
}
