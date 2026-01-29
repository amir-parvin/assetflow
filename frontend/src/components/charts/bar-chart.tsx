"use client";
import { BarChart as RechartsBar, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface BarChartProps {
  data: any[];
  bars: { dataKey: string; color: string; name: string }[];
  xKey?: string;
}

export function BarChart({ data, bars, xKey = "period" }: BarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsBar data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11, fontFamily: "monospace" }} stroke="#a3a3a3" />
        <YAxis tick={{ fontSize: 11, fontFamily: "monospace" }} stroke="#a3a3a3" />
        <Tooltip contentStyle={{ border: "1px solid #e5e5e5", borderRadius: 0, fontSize: 12, fontFamily: "monospace" }} />
        <Legend wrapperStyle={{ fontSize: 11, fontFamily: "monospace" }} />
        {bars.map((b) => (
          <Bar key={b.dataKey} dataKey={b.dataKey} fill={b.color} name={b.name} radius={0} />
        ))}
      </RechartsBar>
    </ResponsiveContainer>
  );
}
