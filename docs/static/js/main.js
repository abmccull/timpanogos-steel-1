// Performance and User Engagement Monitoring
class SiteMonitoring {
    constructor() {
        this.scrollDepths = new Set();
        this.pageLoadTime = performance.now();
        this.formStartTime = null;
        this.setupEventListeners();
        this.logPageLoad();
    }

    setupEventListeners() {
        // Scroll depth tracking
        window.addEventListener('scroll', this.handleScroll.bind(this));
        
        // Form monitoring
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
            form.addEventListener('focus', () => this.formStartTime = Date.now(), true);
        });

        // Performance monitoring
        window.addEventListener('load', this.measurePagePerformance.bind(this));
    }

    handleScroll() {
        const scrollPercent = Math.round((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100);
        
        [25, 50, 75, 100].forEach(threshold => {
            if (scrollPercent >= threshold && !this.scrollDepths.has(threshold)) {
                this.scrollDepths.add(threshold);
                this.logEvent('scroll_depth', { depth: threshold });
            }
        });
    }

    async handleFormSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Calculate form completion time
        const completionTime = this.formStartTime ? (Date.now() - this.formStartTime) / 1000 : null;
        
        try {
            const response = await fetch('/submit-form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...data,
                    completionTime,
                    url: window.location.href
                })
            });

            if (response.ok) {
                this.logEvent('form_submission', {
                    success: true,
                    completionTime
                });
                form.reset();
                alert('Thank you for your submission!');
            } else {
                throw new Error('Form submission failed');
            }
        } catch (error) {
            this.logEvent('form_error', {
                error: error.message,
                formData: data
            });
            alert('There was an error submitting the form. Please try again.');
        }
    }

    measurePagePerformance() {
        const timing = performance.getEntriesByType('navigation')[0];
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        
        this.logEvent('page_performance', {
            loadTime,
            domComplete: timing.domComplete,
            domInteractive: timing.domInteractive,
            url: window.location.href
        });
    }

    logPageLoad() {
        const pageData = {
            url: window.location.href,
            title: document.title,
            timestamp: new Date().toISOString()
        };
        this.logEvent('page_view', pageData);
    }

    logEvent(eventName, data) {
        const event = {
            event: eventName,
            timestamp: new Date().toISOString(),
            data
        };
        console.log('Monitoring Event:', event);
        
        // In production, send to your analytics endpoint
        // this.sendToAnalytics(event);
    }
}

// Initialize monitoring
document.addEventListener('DOMContentLoaded', () => {
    window.siteMonitoring = new SiteMonitoring();
});
