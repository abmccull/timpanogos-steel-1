// Monitoring and Analytics Module
class MonitoringService {
    constructor() {
        this.initialized = false;
        this.GA_TRACKING_ID = window.GA_TRACKING_ID;
        this.SENTRY_DSN = window.SENTRY_DSN;
        this.formStartTimes = new Map();
        this.pageLoadStartTime = performance.now();
    }

    init() {
        if (this.initialized) return;
        
        // Initialize Google Analytics
        this.initGoogleAnalytics();
        
        // Initialize Sentry
        this.initSentry();
        
        // Set up performance monitoring
        this.initPerformanceMonitoring();
        
        // Set up form monitoring
        this.initFormMonitoring();

        // Set up engagement monitoring
        this.initEngagementMonitoring();
        
        this.initialized = true;
    }

    initGoogleAnalytics() {
        // Google Analytics 4 setup
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${this.GA_TRACKING_ID}`;
        document.head.appendChild(script);

        window.dataLayer = window.dataLayer || [];
        function gtag() {
            window.dataLayer.push(arguments);
        }
        gtag('js', new Date());
        gtag('config', this.GA_TRACKING_ID, {
            send_page_view: true,
            page_title: document.title,
            page_location: window.location.href
        });

        // Track custom events
        this.trackPageLoad();
    }

    initSentry() {
        Sentry.init({
            dsn: this.SENTRY_DSN,
            integrations: [
                new Sentry.BrowserTracing({
                    tracePropagationTargets: ["localhost", "timpanogos-steel.com"],
                }),
                new Sentry.Replay({
                    maskAllText: false,
                    maskAllInputs: true
                })
            ],
            tracesSampleRate: 1.0,
            replaysSessionSampleRate: 0.1,
            replaysOnErrorSampleRate: 1.0,
            environment: window.location.hostname === 'localhost' ? 'development' : 'production'
        });
    }

    initPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            if (window.performance) {
                const timing = window.performance.timing;
                const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
                this.trackPerformanceMetric('page_load_time', pageLoadTime);

                // Send to CloudWatch
                this.sendCustomMetric('PageLoadTime', pageLoadTime, 'Milliseconds');
            }
        });

        // Monitor resource loading
        if (window.PerformanceObserver) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.initiatorType === 'resource') {
                        this.trackResourceTiming(entry);
                    }
                }
            });
            observer.observe({ entryTypes: ['resource'] });
        }
    }

    initFormMonitoring() {
        document.querySelectorAll('form').forEach(form => {
            // Track form start
            form.addEventListener('focusin', () => {
                if (!this.formStartTimes.has(form.id)) {
                    this.formStartTimes.set(form.id, performance.now());
                    this.trackEvent('form_interaction', 'start', form.id);
                }
            });

            // Track form abandonment
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'hidden' && this.formStartTimes.has(form.id)) {
                    const startTime = this.formStartTimes.get(form.id);
                    const abandonmentTime = performance.now() - startTime;
                    this.trackFormAbandonment(form.id, abandonmentTime);
                }
            });

            // Track form submission
            form.addEventListener('submit', () => {
                if (this.formStartTimes.has(form.id)) {
                    const startTime = this.formStartTimes.get(form.id);
                    const completionTime = performance.now() - startTime;
                    this.trackFormCompletion(form.id, completionTime);
                    this.formStartTimes.delete(form.id);
                }
            });
        });
    }

    initEngagementMonitoring() {
        let scrollDepth = 0;
        let timeOnPage = 0;
        const startTime = Date.now();

        // Track scroll depth
        window.addEventListener('scroll', () => {
            const newDepth = Math.floor((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100);
            if (newDepth > scrollDepth) {
                scrollDepth = newDepth;
                if (scrollDepth % 25 === 0) { // Track at 25%, 50%, 75%, 100%
                    this.trackEvent('engagement', 'scroll_depth', `${scrollDepth}%`);
                }
            }
        });

        // Track time on page
        const trackTime = () => {
            timeOnPage = Math.floor((Date.now() - startTime) / 1000);
            if (timeOnPage % 30 === 0) { // Track every 30 seconds
                this.trackEvent('engagement', 'time_on_page', null, timeOnPage);
            }
        };
        setInterval(trackTime, 1000);

        // Track bounce rate
        window.addEventListener('beforeunload', () => {
            if (timeOnPage < 30) { // Less than 30 seconds considered a bounce
                this.sendCustomMetric('BounceRate', 1, 'Count');
            }
        });

        // Track city page views
        if (window.location.pathname.includes('steel-buildings-')) {
            this.sendCustomMetric('CityPageViews', 1, 'Count');
        }
    }

    trackPageLoad() {
        const pageData = {
            page_title: document.title,
            page_location: window.location.href,
            page_path: window.location.pathname,
            city_page: window.location.pathname.includes('steel-buildings-')
        };
        gtag('event', 'page_view', pageData);
    }

    trackEvent(category, action, label = null, value = null) {
        const eventData = {
            event_category: category,
            event_label: label,
            value: value
        };
        gtag('event', action, eventData);
    }

    trackPerformanceMetric(name, value) {
        this.trackEvent('performance', name, null, value);
        
        Sentry.addBreadcrumb({
            category: 'performance',
            message: `${name}: ${value}ms`,
            level: 'info'
        });
    }

    trackResourceTiming(entry) {
        if (entry.duration > 1000) { // Track slow resource loads (>1s)
            this.trackEvent('performance', 'slow_resource', entry.name, entry.duration);
            
            Sentry.addBreadcrumb({
                category: 'performance',
                message: `Slow resource load: ${entry.name} (${entry.duration}ms)`,
                level: 'warning'
            });
        }
    }

    trackFormCompletion(formId, duration) {
        this.trackEvent('form', 'completion', formId, duration);
        this.sendCustomMetric('FormCompletionTime', duration / 1000, 'Seconds');
        this.sendCustomMetric('FormSubmissions', 1, 'Count');
    }

    trackFormAbandonment(formId, duration) {
        this.trackEvent('form', 'abandonment', formId, duration);
        this.sendCustomMetric('FormAbandonment', 1, 'Count');
    }

    trackError(error, context = {}) {
        // Track in Google Analytics
        this.trackEvent('error', error.name, error.message);
        
        // Track in Sentry with enhanced context
        Sentry.withScope(scope => {
            scope.setExtra('page_url', window.location.href);
            scope.setExtra('user_agent', navigator.userAgent);
            scope.setExtra('viewport', {
                width: window.innerWidth,
                height: window.innerHeight
            });
            scope.setExtra('custom_context', context);
            Sentry.captureException(error);
        });
    }

    async sendCustomMetric(name, value, unit = 'Count') {
        try {
            const response = await fetch('/api/metrics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    MetricName: name,
                    Value: value,
                    Unit: unit,
                    Timestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send metric');
            }
        } catch (error) {
            this.trackError(error, {
                metric_name: name,
                metric_value: value,
                metric_unit: unit
            });
        }
    }
}

// Initialize monitoring service
const monitoring = new MonitoringService();
document.addEventListener('DOMContentLoaded', () => monitoring.init());

// Export for use in other modules
export default monitoring;
