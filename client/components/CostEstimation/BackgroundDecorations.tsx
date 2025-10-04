import React from "react";

interface BackgroundDecorationsProps {
  children: React.ReactNode;
}

export default function BackgroundDecorations({
  children,
}: BackgroundDecorationsProps) {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background with gradient and patterns */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-cyan-50">
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

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
