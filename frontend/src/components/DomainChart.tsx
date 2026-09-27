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
    totals: number[];
    pct_correct: number[];
    pct_incorrect: number[];
  };
};

export function DomainChart({ title, data }: DomainChartProps) {
  if (!data || data.labels.length === 0) {
    return <p className="text-sm text-slate-500">No domain data available.</p>;
  }

  const counts = [data.correct, data.incorrect];

  return (
    <div className="min-w-0 rounded-md border border-slate-200 bg-white p-4 shadow-soft">
      <h3 className="mb-3 text-base font-semibold">{title}</h3>
      <div className="relative w-full" style={{ height: data.labels.length * 48 + 64 }}>
        <Bar
          data={{
            labels: data.labels,
            datasets: [
              { label: "Correct", data: data.pct_correct, backgroundColor: "#0f766e" },
              { label: "Incorrect", data: data.pct_incorrect, backgroundColor: "#c2410c" }
            ]
          }}
          options={{
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            datasets: { bar: { borderColor: "#ffffff", borderWidth: { left: 1, right: 1 }, borderSkipped: false, maxBarThickness: 28 } },
            scales: {
              x: {
                stacked: true,
                min: 0,
                max: 100,
                ticks: { stepSize: 25, callback: (value) => `${value}%` },
                grid: { color: "#e2e8f0" }
              },
              y: { stacked: true, grid: { display: false } }
            },
            plugins: {
              legend: { position: "bottom" },
              tooltip: {
                callbacks: {
                  label: (ctx) =>
                    `${ctx.dataset.label}: ${ctx.parsed.x}% (${counts[ctx.datasetIndex][ctx.dataIndex]}/${data.totals[ctx.dataIndex]})`
                }
              }
            }
          }}
        />
      </div>
    </div>
  );
}
