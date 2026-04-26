interface PerformanceMetrics {
  fcp: number // First Contentful Paint
  lcp: number // Largest Contentful Paint
  fid: number // First Input Delay
  cls: number // Cumulative Layout Shift
  ttfb: number // Time to First Byte
  loadTime: number
  bundleSize: number
}

interface PerformanceEntry {
  name: string
  value: number
  timestamp: number
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics = {
    fcp: 0,
    lcp: 0,
    fid: 0,
    cls: 0,
    ttfb: 0,
    loadTime: 0,
    bundleSize: 0
  }

  private entries: PerformanceEntry[] = []
  private observers: PerformanceObserver[] = []

  constructor() {
    this.initializeObservers()
    this.measureLoadTime()
  }

  private initializeObservers() {
    // First Contentful Paint
    this.observePerformanceEntry('paint', (entries) => {
      const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint')
      if (fcpEntry) {
        this.metrics.fcp = fcpEntry.startTime
        this.addEntry('FCP', fcpEntry.startTime)
      }
    })

    // Largest Contentful Paint
    this.observePerformanceEntry('largest-contentful-paint', (entries) => {
      const lastEntry = entries[entries.length - 1]
      if (lastEntry) {
        this.metrics.lcp = lastEntry.startTime
        this.addEntry('LCP', lastEntry.startTime)
      }
    })

    // First Input Delay
    this.observePerformanceEntry('first-input', (entries) => {
      const fidEntry = entries[0]
      if (fidEntry && 'processingStart' in fidEntry) {
        this.metrics.fid = fidEntry.processingStart - fidEntry.startTime
        this.addEntry('FID', this.metrics.fid)
      }
    })

    // Cumulative Layout Shift
    let clsValue = 0
    this.observePerformanceEntry('layout-shift', (entries) => {
      for (const entry of entries) {
        if (!entry.hadRecentInput) {
          clsValue += (entry as any).value
        }
      }
      this.metrics.cls = clsValue
      this.addEntry('CLS', clsValue)
    })

    // Time to First Byte
    if (performance.getEntriesByType && performance.getEntriesByType('navigation').length > 0) {
      const navEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      this.metrics.ttfb = navEntry.responseStart - navEntry.requestStart
      this.addEntry('TTFB', this.metrics.ttfb)
    }
  }

  private observePerformanceEntry(type: string, callback: (entries: any[]) => void) {
    if (!('PerformanceObserver' in window)) return

    try {
      const observer = new PerformanceObserver((list) => {
        callback(list.getEntries())
      })
      observer.observe({ type, buffered: true })
      this.observers.push(observer)
    } catch (error) {
      console.warn(`Performance observer for ${type} not supported:`, error)
    }
  }

  private measureLoadTime() {
    window.addEventListener('load', () => {
      const navigationEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      if (navigationEntry) {
        this.metrics.loadTime = navigationEntry.loadEventEnd - navigationEntry.fetchStart
        this.addEntry('LoadTime', this.metrics.loadTime)
      }
    })
  }

  public addEntry(name: string, value: number) {
    this.entries.push({
      name,
      value,
      timestamp: Date.now()
    })
  }

  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics }
  }

  public getEntries(): PerformanceEntry[] {
    return [...this.entries]
  }

  public measureBundleSize() {
    // Measure bundle size using performance API
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[]
    const jsResources = resources.filter(resource => 
      resource.name.endsWith('.js') || resource.name.endsWith('.mjs')
    )
    
    const totalSize = jsResources.reduce((total, resource) => {
      return total + (resource.encodedBodySize || resource.transferSize || 0)
    }, 0)

    this.metrics.bundleSize = totalSize
    this.addEntry('BundleSize', totalSize)
  }

  public measureComponentRender(componentName: string, renderFunction: () => void) {
    const startTime = performance.now()
    renderFunction()
    const endTime = performance.now()
    
    const renderTime = endTime - startTime
    this.addEntry(`${componentName}_render`, renderTime)
    
    return renderTime
  }

  public measureAsyncOperation<T>(
    operationName: string,
    operation: () => Promise<T>
  ): Promise<T> {
    const startTime = performance.now()
    
    return operation()
      .then((result) => {
        const endTime = performance.now()
        const duration = endTime - startTime
        this.addEntry(operationName, duration)
        return result
      })
      .catch((error) => {
        const endTime = performance.now()
        const duration = endTime - startTime
        this.addEntry(`${operationName}_error`, duration)
        throw error
      })
  }

  public createPerformanceMark(name: string) {
    performance.mark(name)
  }

  public createPerformanceMeasure(name: string, startMark: string, endMark: string) {
    try {
      performance.measure(name, startMark, endMark)
      const measure = performance.getEntriesByName(name, 'measure')[0]
      if (measure) {
        this.addEntry(name, measure.duration)
      }
    } catch (error) {
      console.warn(`Performance measure ${name} failed:`, error)
    }
  }

  public getPerformanceScore(): number {
    const weights = {
      fcp: 0.25,
      lcp: 0.30,
      fid: 0.20,
      cls: 0.15,
      ttfb: 0.10
    }

    const scores = {
      fcp: this.getFCPScore(this.metrics.fcp),
      lcp: this.getLCPScore(this.metrics.lcp),
      fid: this.getFIDScore(this.metrics.fid),
      cls: this.getCLSScore(this.metrics.cls),
      ttfb: this.getTTFBScore(this.metrics.ttfb)
    }

    return Object.entries(weights).reduce((total, [metric, weight]) => {
      return total + (scores[metric as keyof typeof scores] * weight)
    }, 0)
  }

  private getFCPScore(fcp: number): number {
    if (fcp < 1800) return 100
    if (fcp < 3000) return 80
    if (fcp < 4000) return 60
    return 40
  }

  private getLCPScore(lcp: number): number {
    if (lcp < 2500) return 100
    if (lcp < 4000) return 80
    if (lcp < 6000) return 60
    return 40
  }

  private getFIDScore(fid: number): number {
    if (fid < 100) return 100
    if (fid < 300) return 80
    if (fid < 500) return 60
    return 40
  }

  private getCLSScore(cls: number): number {
    if (cls < 0.1) return 100
    if (cls < 0.25) return 80
    if (cls < 0.5) return 60
    return 40
  }

  private getTTFBScore(ttfb: number): number {
    if (ttfb < 800) return 100
    if (ttfb < 1800) return 80
    if (ttfb < 3000) return 60
    return 40
  }

  public logMetrics() {
    console.group('Performance Metrics')
    console.log('FCP:', this.metrics.fcp + 'ms')
    console.log('LCP:', this.metrics.lcp + 'ms')
    console.log('FID:', this.metrics.fid + 'ms')
    console.log('CLS:', this.metrics.cls)
    console.log('TTFB:', this.metrics.ttfb + 'ms')
    console.log('Load Time:', this.metrics.loadTime + 'ms')
    console.log('Bundle Size:', (this.metrics.bundleSize / 1024).toFixed(2) + 'KB')
    console.log('Performance Score:', this.getPerformanceScore().toFixed(2) + '/100')
    console.groupEnd()
  }

  public destroy() {
    this.observers.forEach(observer => observer.disconnect())
    this.observers = []
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor()

// Export utility functions
export function measurePerformance<T>(
  name: string,
  fn: () => T
): T {
  const start = performance.now()
  const result = fn()
  const end = performance.now()
  performanceMonitor.addEntry(name, end - start)
  return result
}

export async function measureAsyncPerformance<T>(
  name: string,
  fn: () => Promise<T>
): Promise<T> {
  return performanceMonitor.measureAsyncOperation(name, fn)
}

export function createPerformanceMark(name: string) {
  performanceMonitor.createPerformanceMark(name)
}

export function createPerformanceMeasure(name: string, startMark: string, endMark: string) {
  performanceMonitor.createPerformanceMeasure(name, startMark, endMark)
}
