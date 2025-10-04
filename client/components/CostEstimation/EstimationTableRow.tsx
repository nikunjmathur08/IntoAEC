import React from "react";

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

interface EstimationTableRowProps {
  row: EstimationRow;
  index: number;
  onUnitCostChange: (id: number, newUnitCost: number) => void;
}

export default function EstimationTableRow({
  row,
  index,
  onUnitCostChange,
}: EstimationTableRowProps) {
  return (
    <tr
      className={`border-b border-slate-100 hover:bg-blue-50/50 transition-colors duration-200 ${
        index % 2 === 0 ? "bg-slate-50/30" : "bg-white/50"
      }`}
    >
      <td
        className="p-4 font-medium text-slate-800"
        style={{ fontFamily: "Inter, Poppins, sans-serif" }}
      >
        {row.elementType}
      </td>
      <td
        className="p-4 text-slate-600"
        style={{ fontFamily: "Inter, Poppins, sans-serif" }}
      >
        {row.material}
      </td>
      <td
        className="p-4 text-slate-600"
        style={{ fontFamily: "Inter, Poppins, sans-serif" }}
      >
        {row.length}
      </td>
      <td
        className="p-4 text-slate-600"
        style={{ fontFamily: "Inter, Poppins, sans-serif" }}
      >
        {row.quantity}
      </td>
      <td className="p-4">
        <select
          className="p-2 border border-slate-200 rounded-lg bg-white hover:border-blue-400 focus:border-blue-500 focus:outline-none transition-colors duration-200 text-black"
          style={{ fontFamily: "Inter, Poppins, sans-serif" }}
          value={row.unitCost}
          onChange={(e) => onUnitCostChange(row.id, Number(e.target.value))}
        >
          {row.unitCostOptions.map((option, idx) => (
            <option key={idx} value={option.value} className="text-black">
              {option.label}
            </option>
          ))}
        </select>
      </td>
      <td
        className="p-4 font-semibold text-blue-700"
        style={{ fontFamily: "Inter, Poppins, sans-serif" }}
      >
        ₹{row.totalCost.toLocaleString()}
      </td>
      <td className="p-4">
        <span
          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
          style={{ fontFamily: "Inter, Poppins, sans-serif" }}
        >
          {row.category}
        </span>
      </td>
    </tr>
  );
}
