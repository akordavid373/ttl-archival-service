import React, { useEffect, useState, useRef } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import html2canvas from "html2canvas";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

type DataPoint = {
  name: string;
  value: number;
};

export const ChartDashboard = () => {
  const [data, setData] = useState<DataPoint[]>([]);
  const ref = useRef<HTMLDivElement>(null);

  // 🔄 Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setData((prev) => {
        const next = [
          ...prev.slice(-9),
          {
            name: new Date().toLocaleTimeString(),
            value: Math.floor(Math.random() * 100),
          },
        ];
        return next;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // 📥 Export as image
  const exportChart = async () => {
    if (!ref.current) return;

    const canvas = await html2canvas(ref.current);
    const link = document.createElement("a");
    link.download = "dashboard.png";
    link.href = canvas.toDataURL();
    link.click();
  };

  return (
    <div>
      <button onClick={exportChart}>Export Dashboard</button>

      <div ref={ref} style={{ display: "grid", gap: 20 }}>
        {/* 📈 Line Chart */}
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>

        {/* 📊 Bar Chart */}
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>

        {/* 🥧 Pie Chart */}
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Tooltip />
            <Legend />
            <Pie
              data={data.slice(-5)}
              dataKey="value"
              nameKey="name"
              outerRadius={100}
            >
              {data.slice(-5).map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* 🌊 Area Chart */}
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#ffc658"
              fill="#ffc658"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
