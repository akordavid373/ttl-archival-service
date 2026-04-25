import React, { useState, useEffect } from 'react'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Cpu, 
  Database, 
  HardDrive, 
  MemoryStick,
  TrendingDown,
  TrendingUp,
  Users,
  Zap,
  Server,
  Globe,
  RefreshCw
} from 'lucide-react'
import { cn } from '../utils/cn'

interface PerformanceMetrics {
  timestamp: string
  cpuUsage: number
  memoryUsage: number
  diskUsage: number
  apiResponseTime: number
  errorRate: number
  activeUsers: number
  requestsPerSecond: number
  databaseConnections: number
}

interface Alert {
  id: string
  type: 'error' | 'warning' | 'info'
  message: string
  timestamp: string
  resolved?: boolean
}

interface PerformanceDashboardProps {
  className?: string
  refreshInterval?: number
}

export function PerformanceDashboard({ 
  className, 
  refreshInterval = 5000 
}: PerformanceDashboardProps) {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    timestamp: new Date().toISOString(),
    cpuUsage: 45,
    memoryUsage: 62,
    diskUsage: 38,
    apiResponseTime: 120,
    errorRate: 0.02,
    activeUsers: 127,
    requestsPerSecond: 45,
    databaseConnections: 8
  })

  const [historicalData, setHistoricalData] = useState<PerformanceMetrics[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: '1',
      type: 'warning',
      message: 'CPU usage approaching threshold (85%)',
      timestamp: new Date(Date.now() - 300000).toISOString()
    },
    {
      id: '2',
      type: 'error',
      message: 'Database connection pool exhausted',
      timestamp: new Date(Date.now() - 600000).toISOString()
    }
  ])

  const [isRealTime, setIsRealTime] = useState(true)
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h')

  // Simulate real-time data updates
  useEffect(() => {
    if (!isRealTime) return

    const interval = setInterval(() => {
      const newMetrics: PerformanceMetrics = {
        timestamp: new Date().toISOString(),
        cpuUsage: Math.max(0, Math.min(100, metrics.cpuUsage + (Math.random() - 0.5) * 10)),
        memoryUsage: Math.max(0, Math.min(100, metrics.memoryUsage + (Math.random() - 0.5) * 5)),
        diskUsage: Math.max(0, Math.min(100, metrics.diskUsage + (Math.random() - 0.5) * 2)),
        apiResponseTime: Math.max(50, metrics.apiResponseTime + (Math.random() - 0.5) * 20),
        errorRate: Math.max(0, Math.min(0.1, metrics.errorRate + (Math.random() - 0.5) * 0.01)),
        activeUsers: Math.max(0, metrics.activeUsers + Math.floor((Math.random() - 0.5) * 10)),
        requestsPerSecond: Math.max(0, metrics.requestsPerSecond + Math.floor((Math.random() - 0.5) * 5)),
        databaseConnections: Math.max(1, Math.min(20, metrics.databaseConnections + Math.floor((Math.random() - 0.5) * 2)))
      }

      setMetrics(newMetrics)
      setHistoricalData(prev => [...prev.slice(-50), newMetrics])
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [isRealTime, refreshInterval, metrics])

  const getMetricColor = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return 'text-red-500'
    if (value >= thresholds.warning) return 'text-yellow-500'
    return 'text-green-500'
  }

  const getMetricIcon = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) return <AlertTriangle className="h-4 w-4" />
    if (value >= thresholds.warning) return <AlertTriangle className="h-4 w-4" />
    return <CheckCircle className="h-4 w-4" />
  }

  const MetricCard = ({ 
    title, 
    value, 
    unit, 
    icon: Icon, 
    thresholds, 
    trend,
    description 
  }: {
    title: string
    value: number
    unit: string
    icon: any
    thresholds: { warning: number; critical: number }
    trend?: number
    description?: string
  }) => (
    <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn('p-2 rounded-lg bg-accent/50', getMetricColor(value, thresholds))}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-muted-foreground">{title}</h3>
            {description && <p className="text-xs text-muted-foreground/70">{description}</p>}
          </div>
        </div>
        <div className={cn('flex items-center gap-1', getMetricColor(value, thresholds))}>
          {getMetricIcon(value, thresholds)}
          {trend !== undefined && (
            <>
              {trend > 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              <span className="text-xs font-medium">{Math.abs(trend).toFixed(1)}%</span>
            </>
          )}
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className={cn('text-2xl font-bold', getMetricColor(value, thresholds))}>
          {value.toFixed(1)}
        </span>
        <span className="text-sm text-muted-foreground">{unit}</span>
      </div>
    </div>
  )

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Performance Dashboard</h2>
          <p className="text-muted-foreground">Real-time system performance metrics</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsRealTime(!isRealTime)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-xl transition-colors text-sm font-medium',
              isRealTime 
                ? 'bg-primary text-primary-foreground' 
                : 'bg-accent text-accent-foreground'
            )}
          >
            <Activity className={cn('h-4 w-4', isRealTime && 'animate-pulse')} />
            {isRealTime ? 'Live' : 'Paused'}
          </button>
          
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 bg-accent/50 border border-border/40 rounded-xl text-sm"
          >
            <option value="5m">Last 5 minutes</option>
            <option value="1h">Last hour</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
          </select>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="CPU Usage"
          value={metrics.cpuUsage}
          unit="%"
          icon={Cpu}
          thresholds={{ warning: 70, critical: 90 }}
          trend={5.2}
          description="Processor utilization"
        />
        
        <MetricCard
          title="Memory Usage"
          value={metrics.memoryUsage}
          unit="%"
          icon={MemoryStick}
          thresholds={{ warning: 80, critical: 95 }}
          trend={-2.1}
          description="RAM utilization"
        />
        
        <MetricCard
          title="Disk Usage"
          value={metrics.diskUsage}
          unit="%"
          icon={HardDrive}
          thresholds={{ warning: 80, critical: 95 }}
          trend={0.5}
          description="Storage utilization"
        />
        
        <MetricCard
          title="API Response Time"
          value={metrics.apiResponseTime}
          unit="ms"
          icon={Clock}
          thresholds={{ warning: 500, critical: 1000 }}
          trend={-8.3}
          description="Average response time"
        />
        
        <MetricCard
          title="Error Rate"
          value={metrics.errorRate * 100}
          unit="%"
          icon={AlertTriangle}
          thresholds={{ warning: 1, critical: 5 }}
          trend={-15.2}
          description="Failed requests percentage"
        />
        
        <MetricCard
          title="Active Users"
          value={metrics.activeUsers}
          unit=""
          icon={Users}
          thresholds={{ warning: 500, critical: 1000 }}
          trend={12.7}
          description="Concurrent users"
        />
        
        <MetricCard
          title="Requests/sec"
          value={metrics.requestsPerSecond}
          unit="req/s"
          icon={Zap}
          thresholds={{ warning: 100, critical: 200 }}
          trend={3.4}
          description="API request rate"
        />
        
        <MetricCard
          title="DB Connections"
          value={metrics.databaseConnections}
          unit=""
          icon={Database}
          thresholds={{ warning: 15, critical: 19 }}
          trend={-1.2}
          description="Active database connections"
        />
      </div>

      {/* Alerts Section */}
      <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Active Alerts
          </h3>
          <span className="text-sm text-muted-foreground">
            {alerts.filter(a => !a.resolved).length} unresolved
          </span>
        </div>
        
        <div className="space-y-2">
          {alerts.filter(alert => !alert.resolved).map(alert => (
            <div
              key={alert.id}
              className={cn(
                'flex items-center justify-between p-3 rounded-lg border',
                alert.type === 'error' && 'bg-red-50 border-red-200 text-red-800',
                alert.type === 'warning' && 'bg-yellow-50 border-yellow-200 text-yellow-800',
                alert.type === 'info' && 'bg-blue-50 border-blue-200 text-blue-800'
              )}
            >
              <div className="flex items-center gap-3">
                {alert.type === 'error' && <AlertTriangle className="h-4 w-4" />}
                {alert.type === 'warning' && <AlertTriangle className="h-4 w-4" />}
                {alert.type === 'info' && <CheckCircle className="h-4 w-4" />}
                <span className="text-sm font-medium">{alert.message}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs opacity-70">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </span>
                <button
                  onClick={() => {
                    setAlerts(prev => 
                      prev.map(a => a.id === alert.id ? { ...a, resolved: true } : a)
                    )
                  }}
                  className="text-xs px-2 py-1 bg-white/50 rounded hover:bg-white/70 transition-colors"
                >
                  Resolve
                </button>
              </div>
            </div>
          ))}
          
          {alerts.filter(alert => !alert.resolved).length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No active alerts</p>
            </div>
          )}
        </div>
      </div>

      {/* Performance Chart */}
      <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-6">
        <h3 className="font-semibold text-lg mb-4">Performance Trends</h3>
        <div className="h-64 flex items-center justify-center text-muted-foreground">
          <div className="text-center">
            <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Performance chart visualization</p>
            <p className="text-xs opacity-70">Historical data would be displayed here</p>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <Server className="h-5 w-5" />
            System Information
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Server</span>
              <span>ttl-archival-prod-01</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Region</span>
              <span>us-west-2</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Version</span>
              <span>v2.1.4</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Uptime</span>
              <span>14d 7h 23m</span>
            </div>
          </div>
        </div>

        <div className="bg-card/80 backdrop-blur-sm border border-border/40 rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Network Status
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <span className="text-green-500 font-medium">Healthy</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Latency</span>
              <span>23ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Bandwidth</span>
              <span>1.2 Gbps</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Packet Loss</span>
              <span>0.01%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Hook for performance monitoring
export function usePerformanceMonitoring() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/performance/metrics')
      if (!response.ok) throw new Error('Failed to fetch metrics')
      const data = await response.json()
      setMetrics(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }

  const createAlert = async (alert: Omit<Alert, 'id' | 'timestamp'>) => {
    try {
      const response = await fetch('/api/performance/alerts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alert)
      })
      if (!response.ok) throw new Error('Failed to create alert')
      return await response.json()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  return {
    metrics,
    isLoading,
    error,
    fetchMetrics,
    createAlert
  }
}
