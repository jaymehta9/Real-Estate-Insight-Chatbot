import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from "recharts";

function TrendChart({ chart }) {
  if (!chart || !chart.length) return null;

  const years = Array.from(
    new Set(
      chart
        .flatMap(s => s.points || [])
        .map(p => p.year)
        .filter(Boolean)
    )
  ).sort((a, b) => a - b);

  const data = years.map(year => {
    const row = { year };
    chart.forEach(series => {
      const point = (series.points || []).find(p => p.year === year);
      if (point) {
        row[series.name + "_price"] = point.price;
        row[series.name + "_demand"] = point.demand;
      }
    });
    return row;
  });

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h2 className="section-title">Price and demand trend</h2>
        <p className="section-subtitle">
          Overlay of average yearly price and demand for selected localities.
        </p>
      </div>
      <div className="chart-body">
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip />
            <Legend />
            {chart.map(series => (
              <Line
                key={series.name + "_price"}
                type="monotone"
                dataKey={series.name + "_price"}
                name={series.name + " price"}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default TrendChart;
