import React from "react";
import EstimationTableRow from "./EstimationTableRow";

interface EstimationRow {
  id: number;
  elementType: string;
  material: string;
  length: number;
  quantity: number;
  unitCost: number;
  totalCost: number;
  category: string;
  unitCostOptions: { label: string; value: number }[];
}

interface EstimationTableProps {
  data: EstimationRow[];
  onUnitCostChange: (id: number, newUnitCost: number) => void;
}

export default function EstimationTable({
  data,
  onUnitCostChange,
}: EstimationTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr
            className="text-white font-bold rounded-t-xl"
            style={{ backgroundColor: "#00CCCC" }}
          >
            <th
              className="p-4 text-left rounded-tl-xl"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Element Type
            </th>
            <th
              className="p-4 text-left"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Material
            </th>
            <th
              className="p-4 text-left"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Length (m)
            </th>
            <th
              className="p-4 text-left"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Quantity
            </th>
            <th
              className="p-4 text-left"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Unit Cost (₹)
            </th>
            <th
              className="p-4 text-left"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Total Cost (₹)
            </th>
            <th
              className="p-4 text-left rounded-tr-xl"
              style={{ fontFamily: "Inter, Poppins, sans-serif" }}
            >
              Category
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <EstimationTableRow
              key={row.id}
              row={row}
              index={index}
              onUnitCostChange={onUnitCostChange}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
