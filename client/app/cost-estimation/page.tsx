"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import BackgroundDecorations from "@/components/CostEstimation/BackgroundDecorations";
import EstimationHeader from "@/components/CostEstimation/EstimationHeader";
import EstimationTable from "@/components/CostEstimation/EstimationTable";
import TotalCostCard from "@/components/CostEstimation/TotalCostCard";
import { EstimationRow, mockEstimationData } from "@/lib/estimationData";
import {
  calculateTotalCost,
  updateEstimationData,
} from "@/lib/estimationUtils";

export default function CostEstimationPage() {
  const router = useRouter();
  const [estimationData, setEstimationData] =
    useState<EstimationRow[]>(mockEstimationData);

  const handleUnitCostChange = (id: number, newUnitCost: number) => {
    const updatedData = updateEstimationData(estimationData, id, newUnitCost);
    setEstimationData(updatedData);
  };

  const handleBack = () => {
    router.back();
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExport = () => {
    // Create the JSON data to export
    const exportData = {
      reportTitle: "Cost Estimation Report",
      generatedDate: new Date().toISOString(),
      totalEstimatedCost: totalEstimatedCost,
      currency: "INR",
      items: estimationData.map((row) => ({
        id: row.id,
        elementType: row.elementType,
        material: row.material,
        length: row.length,
        quantity: row.quantity,
        unitCost: row.unitCost,
        totalCost: row.totalCost,
        category: row.category,
      })),
      summary: {
        totalItems: estimationData.length,
        totalCost: totalEstimatedCost,
        categories: [...new Set(estimationData.map((row) => row.category))],
      },
    };

    // Create and download the JSON file
    const jsonString = JSON.stringify(exportData, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    // Create a temporary link element and trigger download
    const link = document.createElement("a");
    link.href = url;
    link.download = `cost-estimation-report-${
      new Date().toISOString().split("T")[0]
    }.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up the URL object
    URL.revokeObjectURL(url);
  };

  const totalEstimatedCost = calculateTotalCost(estimationData);

  return (
    <BackgroundDecorations>
      <div className="p-6 md:p-10">
        <EstimationHeader onBack={handleBack} onExport={handleExport} />

        <div className="max-w-7xl mx-auto">
          <div
            className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 border border-white/50"
            style={{ boxShadow: "rgba(0, 0, 0, 0.1) 0px 8px 30px" }}
          >
            <EstimationTable
              data={estimationData}
              onUnitCostChange={handleUnitCostChange}
            />

            <TotalCostCard totalCost={totalEstimatedCost} />
          </div>
        </div>
      </div>
    </BackgroundDecorations>
  );
}
