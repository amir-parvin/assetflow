"use client";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#171717", "#525252", "#a3a3a3", "#E5C07B", "#737373", "#404040", "#d4d4d4", "#262626"];

interface DonutChartProps {
  data: { name: string; value: number }[];
}

export function DonutChart({ data }: DonutChartProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="value" nameKey="name" strokeWidth={0}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ border: "1px solid #e5e5e5", borderRadius: 0, fontSize: 12, fontFamily: "monospace" }}
          formatter={(val) => `$${Number(val).toLocaleString()}`}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
