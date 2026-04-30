import React from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const data = [
  { subject: "TTL Efficiency", A: 120, B: 110, fullMark: 150 },
  { subject: "Cost Reduction", A: 98, B: 130, fullMark: 150 },
  { subject: "Security", A: 130, B: 130, fullMark: 150 },
  { subject: "Data Integrity", A: 140, B: 140, fullMark: 150 },
  { subject: "Recovery Speed", A: 85, B: 90, fullMark: 150 },
];

export function PolicyMetricsChart() {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#64748b", fontSize: 11, fontWeight: "bold" }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 150]}
            tick={{ fill: "#64748b", fontSize: 10 }}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(255, 255, 255, 0.8)",
              backdropFilter: "blur(8px)",
              border: "1px solid #e2e8f0",
              borderRadius: "12px",
            }}
          />
          <Radar
            name="Manual Controls"
            dataKey="B"
            stroke="#94a3b8"
            fill="#94a3b8"
            fillOpacity={0.1}
          />
          <Radar
            name="Automated Policies"
            dataKey="A"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.3}
            dot={true}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
