import { EstimationRow } from "./estimationData";

export const calculateTotalCost = (data: EstimationRow[]): number => {
  return data.reduce((sum, row) => sum + row.totalCost, 0);
};

export const updateRowTotalCost = (
  row: EstimationRow,
  newUnitCost: number
): EstimationRow => {
  const newTotalCost = row.length * row.quantity * newUnitCost;
  return { ...row, unitCost: newUnitCost, totalCost: newTotalCost };
};

export const updateEstimationData = (
  data: EstimationRow[],
  id: number,
  newUnitCost: number
): EstimationRow[] => {
  return data.map((row) => {
    if (row.id === id) {
      return updateRowTotalCost(row, newUnitCost);
    }
    return row;
  });
};
