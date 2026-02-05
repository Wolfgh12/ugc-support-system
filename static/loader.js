/**
 * UGC Global Page Loader - Standardized < 2s Timing Fix
 */

const getLoader = () => document.getElementById('global-loader');

window.hideLoader = () => {
    const loader = getLoader();
    if (loader) {
        // 0.6s CSS transition for a professional smooth exit
        loader.style.transition = 'opacity 0.6s ease';
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
        }, 600);
    }
};

window.showLoader = () => {
    const loader = getLoader();
    if (loader) {
        loader.style.setProperty('display', 'flex', 'important');
        loader.style.opacity = '1';
    }
};

// INITIAL TRIGGER: 1.2s Hold + 0.6s Fade = 1.8s Total (Under 2s Limit)
document.addEventListener('DOMContentLoaded', () => {
    const loader = getLoader();
    if (loader) {
        // We use window 'load' to ensure images/assets are ready
        window.addEventListener('load', () => {
            // Wait 1.2 seconds, then trigger the fade
            // This ensures the user sees the branding but isn't delayed
            setTimeout(window.hideLoader, 1200);
        });

        // Safety Fallback: If 'load' takes too long, force hide at 1.9s
        setTimeout(() => {
            if (loader.style.display !== 'none') {
                window.hideLoader();
            }
        }, 1900);
    }
});

// GLOBAL FORM SUBMISSION (Login, Search, etc.)
document.addEventListener('submit', (e) => {
    // Show loader immediately to mask the processing/redirect time
    if (e.target && e.target.id !== 'enquiryForm' && e.target.id !== 'replyForm') {
        window.showLoader();
    }
});