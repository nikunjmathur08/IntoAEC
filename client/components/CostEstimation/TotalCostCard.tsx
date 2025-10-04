import React from "react";

interface TotalCostCardProps {
  totalCost: number;
}

export default function TotalCostCard({ totalCost }: TotalCostCardProps) {
  return (
    <div className="mt-8 flex justify-end">
      <div
        className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-6 border border-blue-100"
        style={{ boxShadow: "rgba(0, 204, 204, 0.2) 0px 8px 25px" }}
      >
        <div className="flex items-center gap-4">
          <span
            className="text-slate-700 font-medium text-lg"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            Total Estimated Cost
          </span>
          <span
            className="font-bold text-2xl bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent"
            style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          >
            ₹{totalCost.toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
}
