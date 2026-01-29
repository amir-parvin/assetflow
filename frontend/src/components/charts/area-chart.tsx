"use client";
import { AreaChart as RechartsArea, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface AreaChartProps {
  data: any[];
  dataKey: string;
  xKey?: string;
  color?: string;
}

export function AreaChart({ data, dataKey, xKey = "period", color = "#171717" }: AreaChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsArea data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11, fontFamily: "monospace" }} stroke="#a3a3a3" />
        <YAxis tick={{ fontSize: 11, fontFamily: "monospace" }} stroke="#a3a3a3" />
        <Tooltip contentStyle={{ border: "1px solid #e5e5e5", borderRadius: 0, fontSize: 12, fontFamily: "monospace" }} />
        <Area type="monotone" dataKey={dataKey} stroke={color} fill={color} fillOpacity={0.05} strokeWidth={1.5} />
      </RechartsArea>
    </ResponsiveContainer>
  );
}
