import React from 'react';
import { useTranslation } from 'react-i18next';
import { SEO } from '../components/common/SEO';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  Clock, 
  AlertTriangle, 
  Trash2, 
  Download, 
  RefreshCw,
  ArrowUpRight
} from 'lucide-react'
import { StorageUsageChart } from '../components/charts/StorageUsageChart'
import { ArchiveTrendsChart } from '../components/charts/ArchiveTrendsChart'
import RetentionSankey from '../components/charts/RetentionSankey'
import { cn } from '../lib/utils'

export function Dashboard() {
  const [isRefreshing, setIsRefreshing] = useState(false)

export const Dashboard: React.FC = () => {
  const { t } = useTranslation()

  const stats = [
    { label: t('dashboard.activePolicies'), value: '1,284', icon: Archive, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: t('dashboard.statistics'), value: '99.9%', icon: Shield, color: 'text-green-500', bg: 'bg-green-500/10' },
    { label: t('dashboard.storageUsed'), value: '42.5 GB', icon: Database, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { label: t('dashboard.lastSync'), value: '14 Days', icon: Clock, color: 'text-orange-500', bg: 'bg-orange-500/10' },
  ];

  return (
    <div className="space-y-8">
      <SEO title="Dashboard" description="Overview of your archival status and statistics." />
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold">{t('dashboard.welcome')}</h2>
          <p className="text-gray-500">{t('dashboard.overview')}</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-800 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            {t('common.refresh')} {t('dashboard.title')}
          </button>
          <button className="px-4 py-2 rounded-xl bg-primary text-white font-medium hover:opacity-90 transition-opacity">
            {t('common.add')} {t('archives.title')}
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
            <h3 className="text-lg font-bold">{t('dashboard.recentActivity')}</h3>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-100 dark:border-gray-800 rounded-xl">
            <p className="text-gray-400">{t('dashboard.statistics')}</p>
          </div>
        </div>
      </div>

      <div className="p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative overflow-hidden group">
        <div className="flex items-center justify-between mb-8">
          <h3 className="font-bold text-xl flex items-center gap-3">
            <Activity className="h-6 w-6 text-indigo-500" />
            Data Retention Lifecycle
          </h3>
          <p className="text-xs text-muted-foreground">Visualizing data flow through archival tiers</p>
        </div>
        <RetentionSankey />
      </div>

      <div className="p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative overflow-hidden group">
        <h3 className="font-bold text-lg mb-6 flex items-center gap-3 relative z-10">
          <Clock className="h-5 w-5 text-amber-500" />
          Recently Expired
        </h3>
        <div className="space-y-4 relative z-10">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center gap-4 p-3 rounded-xl hover:bg-accent/50 transition-colors cursor-pointer border border-transparent hover:border-border/40">
              <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center text-amber-500 shrink-0">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold truncate group-hover:text-primary transition-colors">user_logs_2024_03_2{i}.sql</p>
                <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  2 hours ago · 14.2 MB
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
