import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

type DomainChartProps = {
  title: string;
  data?: {
    labels: string[];
    correct: number[];
    incorrect: number[];
  };
};

export function DomainChart({ title, data }: DomainChartProps) {
  if (!data || data.labels.length === 0) {
    return <p className="text-sm text-slate-500">No domain data available.</p>;
  }

  return (
    <div className="rounded-md border border-slate-200 bg-white p-4 shadow-soft">
      <h3 className="mb-3 text-base font-semibold">{title}</h3>
      <Bar
        data={{
          labels: data.labels,
          datasets: [
            { label: "Correct", data: data.correct, backgroundColor: "#0f766e" },
            { label: "Incorrect", data: data.incorrect, backgroundColor: "#c2410c" }
          ]
        }}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          scales: { x: { stacked: true }, y: { stacked: true, ticks: { precision: 0 } } }
        }}
        height={260}
      />
    </div>
  );
}
