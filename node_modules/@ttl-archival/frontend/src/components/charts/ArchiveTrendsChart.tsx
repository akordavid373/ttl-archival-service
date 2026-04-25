import React from 'react'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts'

const data = [
  { day: 'Mon', count: 124 },
  { day: 'Tue', count: 180 },
  { day: 'Wed', count: 90 },
  { day: 'Thu', count: 210 },
  { day: 'Fri', count: 155 },
  { day: 'Sat', count: 60 },
  { day: 'Sun', count: 45 },
]

export function ArchiveTrendsChart() {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
          <XAxis 
            dataKey="day" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#64748b', fontSize: 12 }}
            dy={10}
          />
          <YAxis 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#64748b', fontSize: 12 }}
          />
          <Tooltip 
            cursor={{ fill: 'rgba(59, 130, 246, 0.05)' }}
            contentStyle={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.8)', 
              backdropFilter: 'blur(8px)',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '12px'
            }}
          />
          <Bar 
            dataKey="count" 
            radius={[8, 8, 0, 0]} 
            name="Archives Created"
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={index === 3 ? '#3b82f6' : '#93c5fd'} 
                className="transition-colors hover:fill-blue-600 cursor-pointer"
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
