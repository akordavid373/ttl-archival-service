import { useEffect } from 'react';

// Types for Analytics
export interface AnalyticsEvent {
  category: string;
  action: string;
  label?: string;
  value?: number;
  metadata?: Record<string, any>;
}

class AnalyticsService {
  private static instance: AnalyticsService;
  private isInitialized: boolean = false;
  private trackingId: string | null = null;

  private constructor() {}

  public static getInstance(): AnalyticsService {
    if (!AnalyticsService.instance) {
      AnalyticsService.instance = new AnalyticsService();
    }
    return AnalyticsService.instance;
  }

  public init(trackingId: string) {
    if (this.isInitialized) return;
    
    this.trackingId = trackingId;
    // Mock Google Analytics Initialization
    console.log(`[Analytics] Initializing with ID: ${trackingId}`);
    
    // Check for GDPR/CCPA compliance (mock check)
    const consent = localStorage.getItem('analytics-consent');
    if (consent === 'granted') {
      this.isInitialized = true;
      this.loadGAScript();
    }
  }

  private loadGAScript() {
    console.log('[Analytics] Loading GA script...');
    // Real implementation would inject <script> tags here
  }

  public trackEvent(event: AnalyticsEvent) {
    if (!this.isInitialized) {
      console.warn('[Analytics] Not initialized or consent not granted. Queuing event:', event);
      return;
    }
    console.log(`[Analytics] Tracking Event: ${event.category} - ${event.action}`, event);
    // window.gtag('event', event.action, { ... });
  }

  public trackPageView(path: string) {
    if (!this.isInitialized) return;
    console.log(`[Analytics] Page View: ${path}`);
    // window.gtag('config', this.trackingId, { 'page_path': path });
  }

  public setConsent(granted: boolean) {
    localStorage.setItem('analytics-consent', granted ? 'granted' : 'denied');
    if (granted && !this.isInitialized && this.trackingId) {
      this.init(this.trackingId);
    }
  }
}

export const analytics = AnalyticsService.getInstance();

export const useTracking = () => {
  const trackEvent = (event: AnalyticsEvent) => {
    analytics.trackEvent(event);
  };

  const trackClick = (label: string, metadata?: Record<string, any>) => {
    trackEvent({ category: 'User Interaction', action: 'Click', label, metadata });
  };

  return { trackEvent, trackClick };
};
