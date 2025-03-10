// Form handling and analytics tracking
class FormHandler {
    constructor() {
        this.forms = document.querySelectorAll('.cta-form');
        this.initializeForms();
        this.initializeSmoothScrolling();
    }

    initializeForms() {
        this.forms.forEach(form => {
            form.addEventListener('submit', (event) => this.handleSubmit(event));
        });
    }

    async handleSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const section = form.dataset.section;
        const button = form.querySelector('button[type="submit"]');

        try {
            // Track form submission attempt
            this.trackEvent('form_attempt', {
                event_category: 'Lead',
                event_label: section
            });

            // Get form data
            const formData = new FormData(form);

            // Disable button and show loading state
            button.disabled = true;
            button.textContent = 'Sending...';

            // Submit form
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                mode: 'no-cors'
            });

            // Track successful submission
            this.trackEvent('form_submission', {
                event_category: 'Lead',
                event_label: section,
                value: 1
            });

            // Show success message
            button.textContent = 'Thank You!';

            // Reset form after delay
            setTimeout(() => {
                form.reset();
                button.textContent = 'Get Your Free Quote';
                button.disabled = false;
            }, 3000);

        } catch (error) {
            // Log error to Sentry
            Sentry.captureException(error);

            // Track error
            this.trackEvent('form_error', {
                event_category: 'Error',
                event_label: `${section}: ${error.message}`
            });

            // Show error message
            button.textContent = 'Get Your Free Quote';
            button.disabled = false;
            alert('An error occurred. Please try again later.');
        }
    }

    initializeSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (event) => this.handleSmoothScroll(event));
        });
    }

    handleSmoothScroll(event) {
        event.preventDefault();
        const anchor = event.target;
        const targetId = anchor.getAttribute('href').substring(1);
        const target = document.getElementById(targetId);

        if (target) {
            // Smooth scroll to target
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            // Track navigation
            this.trackEvent('navigation', {
                event_category: 'User Interaction',
                event_label: targetId
            });
        }
    }

    trackEvent(eventName, params) {
        // Google Analytics tracking
        if (typeof gtag === 'function') {
            gtag('event', eventName, params);
        }
    }
}

// Header behavior
class HeaderManager {
    constructor() {
        this.header = document.querySelector('header');
        this.lastScroll = 0;
        this.initializeHeaderBehavior();
    }

    initializeHeaderBehavior() {
        window.addEventListener('scroll', () => this.handleScroll());
    }

    handleScroll() {
        const currentScroll = window.pageYOffset;
        
        // Add/remove sticky class based on scroll position
        if (currentScroll > 100) {
            this.header.classList.add('sticky');
        } else {
            this.header.classList.remove('sticky');
        }

        // Hide/show header based on scroll direction
        if (currentScroll > this.lastScroll && currentScroll > 200) {
            this.header.classList.add('header-hidden');
        } else {
            this.header.classList.remove('header-hidden');
        }

        this.lastScroll = currentScroll;
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.initializeMonitoring();
    }

    initializeMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => this.measurePageLoad());

        // Monitor form interaction times
        document.querySelectorAll('.cta-form').forEach(form => {
            form.addEventListener('focusin', () => this.startFormTimer(form));
            form.addEventListener('submit', () => this.measureFormCompletion(form));
        });
    }

    measurePageLoad() {
        if (window.performance) {
            const timing = window.performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;

            this.trackPerformance('page_load', {
                value: loadTime,
                metric_id: 'page_load_time'
            });
        }
    }

    startFormTimer(form) {
        form.dataset.startTime = Date.now();
    }

    measureFormCompletion(form) {
        if (form.dataset.startTime) {
            const completionTime = Date.now() - parseInt(form.dataset.startTime);
            
            this.trackPerformance('form_completion', {
                value: completionTime,
                metric_id: 'form_completion_time',
                form_section: form.dataset.section
            });
        }
    }

    trackPerformance(metricName, params) {
        // Send to Google Analytics
        if (typeof gtag === 'function') {
            gtag('event', 'performance', {
                event_category: 'Performance',
                event_label: metricName,
                ...params
            });
        }

        // Log to console in development
        if (process.env.NODE_ENV === 'development') {
            console.log(`Performance metric - ${metricName}:`, params);
        }
    }
}

// Initialize all components when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize form handling
    const formHandler = new FormHandler();
    
    // Initialize header behavior
    const headerManager = new HeaderManager();
    
    // Initialize performance monitoring
    const performanceMonitor = new PerformanceMonitor();
    
    // Log initialization
    console.log('Timpanogos Steel website initialized');
});
