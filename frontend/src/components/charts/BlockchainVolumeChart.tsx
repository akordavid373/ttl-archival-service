import React from 'react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Dot 
} from 'recharts'

const data = [
  { time: '10:00', volume: 45 },
  { time: '11:00', volume: 52 },
  { time: '12:00', volume: 38 },
  { time: '13:00', volume: 65 },
  { time: '14:00', volume: 48 },
  { time: '15:00', volume: 72 },
  { time: '16:00', volume: 51 },
]

export function BlockchainVolumeChart() {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
          <XAxis 
            dataKey="time" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            dy={8}
          />
          <YAxis 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#94a3b8', fontSize: 11 }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.9)', 
              backdropFilter: 'blur(12px)',
              border: '1px solid #e2e8f0',
              borderRadius: '16px',
              padding: '12px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
            }}
          />
          <Line 
            type="stepAfter" 
            dataKey="volume" 
            stroke="#f59e0b" 
            strokeWidth={3}
            dot={{ r: 4, stroke: "#f59e0b", fill: "#fff", strokeWidth: 2 }}
            activeDot={{ r: 6, fill: "#f59e0b", stroke: "#fff", strokeWidth: 2 }}
            animationDuration={1500}
            name="TX Blocks Anchored"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
