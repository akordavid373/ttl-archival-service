import React from 'react';
import { SEO } from '../components/common/SEO';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  Clock, 
  Shield, 
  Database,
  ArrowUpRight,
  Archive
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const stats = [
    { label: 'Active Archives', value: '1,284', icon: Archive, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Protection Rate', value: '99.9%', icon: Shield, color: 'text-green-500', bg: 'bg-green-500/10' },
    { label: 'Storage Saved', value: '42.5 GB', icon: Database, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { label: 'Avg TTL Remaining', value: '14 Days', icon: Clock, color: 'text-orange-500', bg: 'bg-orange-500/10' },
  ];

  return (
    <div className="space-y-8">
      <SEO title="Dashboard" description="Overview of your archival status and statistics." />
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold">Welcome back, John</h2>
          <p className="text-gray-500">Here's what's happening with your archives today.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-800 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            Download Report
          </button>
          <button className="px-4 py-2 rounded-xl bg-primary text-white font-medium hover:opacity-90 transition-opacity">
            Quick Archive
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1 }}
            className="p-6 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className={`w-12 h-12 ${stat.bg} ${stat.color} rounded-xl flex items-center justify-center mb-4`}>
              <stat.icon className="w-6 h-6" />
            </div>
            <p className="text-sm font-medium text-gray-500 mb-1">{stat.label}</p>
            <div className="flex items-end justify-between">
              <h3 className="text-2xl font-bold">{stat.value}</h3>
              <div className="flex items-center text-xs font-medium text-green-500 bg-green-500/10 px-2 py-1 rounded-full">
                <ArrowUpRight className="w-3 h-3 mr-1" />
                12%
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold">Archival Activity</h3>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-100 dark:border-gray-800 rounded-xl">
            <p className="text-gray-400">Activity Chart Visualization</p>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
          <h3 className="text-lg font-bold mb-6">Recent Events</h3>
          <div className="space-y-6">
            {[1, 2, 3, 4].map((_, i) => (
              <div key={i} className="flex gap-4">
                <div className="w-2 h-2 mt-2 rounded-full bg-primary shrink-0" />
                <div>
                  <p className="text-sm font-semibold">Archive #8294 Successful</p>
                  <p className="text-xs text-gray-500">2 minutes ago • Mainnet</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
