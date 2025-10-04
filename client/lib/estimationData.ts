export interface EstimationRow {
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

export const mockEstimationData: EstimationRow[] = [
  {
    id: 1,
    elementType: "Wall",
    material: "Brick",
    length: 3.5,
    quantity: 4,
    unitCost: 500,
    totalCost: 7000,
    category: "Structural",
    unitCostOptions: [
      { label: "500 Rs / m²", value: 500 },
      { label: "600 Rs / m²", value: 600 },
      { label: "700 Rs / m²", value: 700 },
    ],
  },
  {
    id: 2,
    elementType: "Door",
    material: "Teak",
    length: 2.0,
    quantity: 5,
    unitCost: 4000,
    totalCost: 40000,
    category: "Woodwork",
    unitCostOptions: [
      { label: "4000 Rs / unit", value: 4000 },
      { label: "4500 Rs / unit", value: 4500 },
      { label: "5000 Rs / unit", value: 5000 },
    ],
  },
  {
    id: 3,
    elementType: "Window",
    material: "UPVC",
    length: 1.5,
    quantity: 3,
    unitCost: 3000,
    totalCost: 13500,
    category: "Fittings",
    unitCostOptions: [
      { label: "3000 Rs / m²", value: 3000 },
      { label: "3500 Rs / m²", value: 3500 },
      { label: "4000 Rs / m²", value: 4000 },
    ],
  },
  {
    id: 4,
    elementType: "Ceiling",
    material: "POP",
    length: 5.0,
    quantity: 1,
    unitCost: 1000,
    totalCost: 5000,
    category: "Interior",
    unitCostOptions: [
      { label: "1000 Rs / m²", value: 1000 },
      { label: "1200 Rs / m²", value: 1200 },
      { label: "1500 Rs / m²", value: 1500 },
    ],
  },
  {
    id: 5,
    elementType: "Door Frame",
    material: "Sal Wood",
    length: 2.0,
    quantity: 5,
    unitCost: 2500,
    totalCost: 25000,
    category: "Woodwork",
    unitCostOptions: [
      { label: "2500 Rs / unit", value: 2500 },
      { label: "3000 Rs / unit", value: 3000 },
      { label: "3500 Rs / unit", value: 3500 },
    ],
  },
  {
    id: 6,
    elementType: "Tile Flooring",
    material: "Ceramic",
    length: 20.0,
    quantity: 1,
    unitCost: 85,
    totalCost: 1700,
    category: "Finishing",
    unitCostOptions: [
      { label: "85 Rs / m²", value: 85 },
      { label: "95 Rs / m²", value: 95 },
      { label: "110 Rs / m²", value: 110 },
    ],
  },
];
