// Gaming Hub - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeComponents();
    setupEventListeners();
    setupAnimations();
    setupImageLazyLoading();
    
    console.log('თამაშების ჰაბი წარმატებულად ინიციალიზება!');
});

/**
 * Initialize all main components
 */
function initializeComponents() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize auto-hide alerts
    initializeAlerts();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize search functionality
    initializeSearch();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Global click handlers
    document.addEventListener('click', handleGlobalClicks);
    
    // Window events
    window.addEventListener('scroll', throttle(handleScroll, 100));
    window.addEventListener('resize', throttle(handleResize, 250));
    
    // Form submissions
    document.addEventListener('submit', handleFormSubmissions);
    
    // Image upload preview
    setupImageUploadPreviews();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup auto-hide alerts
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alert && alert.parentNode) {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            }
        }, 5000);
    });
}

/**
 * Initialize form validations
 */
function initializeFormValidations() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation for specific fields
    setupRealtimeValidation();
}

/**
 * Setup real-time validation
 */
function setupRealtimeValidation() {
    // Username validation
    const usernameFields = document.querySelectorAll('input[name="username"]');
    usernameFields.forEach(field => {
        field.addEventListener('input', debounce(validateUsername, 300));
    });
    
    // Email validation
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        field.addEventListener('input', debounce(validateEmail, 300));
    });
    
    // Password strength validation
    const passwordFields = document.querySelectorAll('input[name="password"], input[name="new_password"]');
    passwordFields.forEach(field => {
        field.addEventListener('input', debounce(validatePassword, 300));
    });
    
    // Confirm password validation
    const confirmPasswordFields = document.querySelectorAll('input[name="password2"], input[name="confirm_password"]');
    confirmPasswordFields.forEach(field => {
        field.addEventListener('input', debounce(validatePasswordConfirm, 300));
    });
}

/**
 * Validate username
 */
function validateUsername(event) {
    const field = event.target;
    const value = field.value;
    const feedback = getOrCreateFeedback(field);
    
    if (value.length === 0) {
        clearValidation(field, feedback);
        return;
    }
    
    if (value.length < 4) {
        setInvalid(field, feedback, 'მომხმარებელის სახელი უნდა იყოს მინიმუმ 4 სიმბოლო');
    } else if (value.length > 20) {
        setInvalid(field, feedback, 'მომხმარებელის სახელი უნდა იყოს 20 სიმბოლოზე ნაკლები');
    } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
        setInvalid(field, feedback, 'მომხმარებელის სახელი შეიძლება შეიცავდეს მხოლოდ ასოებს, რიცხვებს და ვირ-ფარდაღებს');
    } else {
        setValid(field, feedback, 'მომხმარებელის სახელი კარგად!');
    }
}

/**
 * Validate email
 */
function validateEmail(event) {
    const field = event.target;
    const value = field.value;
    const feedback = getOrCreateFeedback(field);
    
    if (value.length === 0) {
        clearValidation(field, feedback);
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
        setInvalid(field, feedback, 'გთხოვთ შეიყვანოთ სწორი ელექტრონული ფოსტა');
    } else {
        setValid(field, feedback, 'ელექტრონული ფოსტა კარგად!');
    }
}

/**
 * Validate password strength
 */
function validatePassword(event) {
    const field = event.target;
    const value = field.value;
    const feedback = getOrCreateFeedback(field);
    
    if (value.length === 0) {
        clearValidation(field, feedback);
        return;
    }
    
    const strength = getPasswordStrength(value);
    const strengthText = ['ძალიან სუსტი', 'სუსტი', 'საშუალო', 'ძლიერი', 'ძალიან ძლიერი'];
    const strengthColors = ['danger', 'warning', 'info', 'success', 'success'];
    
    if (strength < 2) {
        setInvalid(field, feedback, `პაროლი არის ${strengthText[strength]}. გამოიყენეთ ასოების, რიცხვების და სიმბოლოების ნარევი.`);
    } else {
        setValid(field, feedback, `პაროლის სიძლიერე: ${strengthText[strength]}`);
    }
    
    // Update password strength indicator if exists
    updatePasswordStrengthIndicator(field, strength);
}

/**
 * Validate password confirmation
 */
function validatePasswordConfirm(event) {
    const field = event.target;
    const value = field.value;
    const feedback = getOrCreateFeedback(field);
    
    const passwordField = field.form.querySelector('input[name="password"], input[name="new_password"]');
    if (!passwordField) return;
    
    if (value.length === 0) {
        clearValidation(field, feedback);
        return;
    }
    
    if (value !== passwordField.value) {
        setInvalid(field, feedback, 'პაროლები არ ერთმანეთ');
    } else {
        setValid(field, feedback, 'პაროლები ერთმანეთ!');
    }
}

/**
 * Get password strength score (0-4)
 */
function getPasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    // Reduce score for common patterns
    if (/(.)\1{2,}/.test(password)) score--; // Repeated characters
    if (/^(12345|password|qwerty|abc)/i.test(password)) score--; // Common patterns
    
    return Math.max(0, Math.min(4, score));
}

/**
 * Update password strength indicator
 */
function updatePasswordStrengthIndicator(field, strength) {
    let indicator = field.parentNode.querySelector('.password-strength');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'password-strength mt-1';
        field.parentNode.appendChild(indicator);
    }
    
    const strengthColors = ['bg-danger', 'bg-warning', 'bg-info', 'bg-success', 'bg-success'];
    const strengthText = ['ძალიან სუსტი', 'სუსტი', 'საშუალო', 'ძლიერი', 'ძალიან ძლიერი'];
    
    indicator.innerHTML = `
        <div class="progress" style="height: 4px;">
            <div class="progress-bar ${strengthColors[strength]}" 
                 style="width: ${(strength + 1) * 20}%" 
                 role="progressbar"></div>
        </div>
        <small class="text-muted">${strengthText[strength]}</small>
    `;
}

/**
 * Validation helper functions
 */
function getOrCreateFeedback(field) {
    let feedback = field.parentNode.querySelector('.feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'feedback small mt-1';
        field.parentNode.appendChild(feedback);
    }
    return feedback;
}

function setValid(field, feedback, message) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    feedback.className = 'feedback small mt-1 text-success';
    feedback.textContent = message;
}

function setInvalid(field, feedback, message) {
    field.classList.remove('is-valid');
    field.classList.add('is-invalid');
    feedback.className = 'feedback small mt-1 text-danger';
    feedback.textContent = message;
}

function clearValidation(field, feedback) {
    field.classList.remove('is-valid', 'is-invalid');
    feedback.textContent = '';
}

/**
 * Setup image upload previews
 */
function setupImageUploadPreviews() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                previewImage(file, input);
            }
        });
    });
}

/**
 * Preview uploaded image
 */
function previewImage(file, input) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        let preview = input.parentNode.querySelector('.image-preview');
        
        if (!preview) {
            preview = document.createElement('div');
            preview.className = 'image-preview mt-2';
            input.parentNode.appendChild(preview);
        }
        
        preview.innerHTML = `
            <img src="${e.target.result}" alt="Preview" 
                 class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
            <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="removeImagePreview(this)">
                <i class="fas fa-times"></i>
            </button>
        `;
    };
    
    reader.readAsDataURL(file);
}

/**
 * Remove image preview
 */
function removeImagePreview(button) {
    const preview = button.closest('.image-preview');
    const input = preview.parentNode.querySelector('input[type="file"]');
    
    preview.remove();
    input.value = '';
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input, #userSearch, input[name="search"]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
}

/**
 * Handle search input
 */
function handleSearch(event) {
    const query = event.target.value.toLowerCase();
    const targetSelector = event.target.dataset.searchTarget || '.searchable-item';
    const items = document.querySelectorAll(targetSelector);
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const isVisible = text.includes(query);
        
        item.style.display = isVisible ? '' : 'none';
        
        // Add highlight effect
        if (query && isVisible) {
            highlightSearchTerm(item, query);
        } else {
            removeHighlight(item);
        }
    });
    
    // Show/hide no results message
    toggleNoResultsMessage(items, query);
}

/**
 * Highlight search term in text
 */
function highlightSearchTerm(element, term) {
    if (!term) return;
    
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    const textNodes = [];
    let node;
    
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    
    textNodes.forEach(textNode => {
        const text = textNode.textContent;
        const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
        
        if (regex.test(text)) {
            const highlightedHTML = text.replace(regex, '<mark>$1</mark>');
            const wrapper = document.createElement('span');
            wrapper.innerHTML = highlightedHTML;
            textNode.parentNode.replaceChild(wrapper, textNode);
        }
    });
}

/**
 * Remove search highlights
 */
function removeHighlight(element) {
    const marks = element.querySelectorAll('mark');
    marks.forEach(mark => {
        mark.outerHTML = mark.innerHTML;
    });
}

/**
 * Toggle no results message
 */
function toggleNoResultsMessage(items, query) {
    if (!query) return;
    
    const visibleItems = Array.from(items).filter(item => item.style.display !== 'none');
    const container = items[0]?.closest('.search-container') || document.body;
    
    let noResultsMsg = container.querySelector('.no-results-message');
    
    if (visibleItems.length === 0) {
        if (!noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.className = 'no-results-message text-center py-4';
            noResultsMsg.innerHTML = `
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">შედეგები ვერ მოიძებნა</h5>
                <p class="text-muted">სცადეთ შესცვალოთ საძიებო თერმინები</p>
            `;
            container.appendChild(noResultsMsg);
        }
        noResultsMsg.style.display = 'block';
    } else if (noResultsMsg) {
        noResultsMsg.style.display = 'none';
    }
}

/**
 * Setup animations
 */
function setupAnimations() {
    // Animate elements when they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.card, .game-card, .alert');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Setup lazy loading for images
 */
function setupImageLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        imageObserver.observe(img);
    });
}

/**
 * Handle global clicks
 */
function handleGlobalClicks(event) {
    const target = event.target;
    
    // Handle reaction buttons
    if (target.closest('.reaction-btn')) {
        handleReactionClick(event);
    }
    
    // Handle share buttons
    if (target.closest('.share-btn')) {
        handleShareClick(event);
    }
    
    // Handle copy-to-clipboard
    if (target.closest('.copy-btn')) {
        handleCopyClick(event);
    }
    
    // Handle external links
    if (target.closest('a[href^="http"]') && !target.closest('a[href*="' + window.location.hostname + '"]')) {
        handleExternalLink(event);
    }
}

/**
 * Handle reaction button clicks
 */
function handleReactionClick(event) {
    const button = event.target.closest('.reaction-btn');
    if (!button) return;
    
    event.preventDefault();
    
    // Add visual feedback
    button.classList.add('clicked');
    setTimeout(() => button.classList.remove('clicked'), 200);
    
    // Continue with the original link
    setTimeout(() => {
        window.location.href = button.href;
    }, 300);
}

/**
 * Handle share button clicks
 */
function handleShareClick(event) {
    event.preventDefault();
    
    const button = event.target.closest('.share-btn');
    const url = button.dataset.url || window.location.href;
    const title = button.dataset.title || document.title;
    const text = button.dataset.text || '';
    
    if (navigator.share) {
        navigator.share({
            title: title,
            text: text,
            url: url
        }).catch(err => {
            console.log('Error sharing:', err);
            fallbackShare(url);
        });
    } else {
        fallbackShare(url);
    }
}

/**
 * Fallback share functionality
 */
function fallbackShare(url) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(() => {
            showToast('Link copied to clipboard!', 'success');
        }).catch(() => {
            showShareModal(url);
        });
    } else {
        showShareModal(url);
    }
}

/**
 * Show share modal
 */
function showShareModal(url) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">გაიარე ეს გვერდი</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="input-group">
                        <input type="text" class="form-control" value="${url}" readonly>
                        <button class="btn btn-primary" onclick="copyToClipboard('${url}')">კოპირება</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

/**
 * Handle copy-to-clipboard
 */
function handleCopyClick(event) {
    event.preventDefault();
    
    const button = event.target.closest('.copy-btn');
    const text = button.dataset.copy || button.textContent;
    
    copyToClipboard(text);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('კოპირებულია კლიპბორდში!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

/**
 * Fallback copy to clipboard
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('კოპირება ვერ მოხერხდა. გთხოვთ ხელით დაკოპირეთ.', 'danger');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Handle external links
 */
function handleExternalLink(event) {
    const link = event.target.closest('a');
    if (link.dataset.external !== 'false') {
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
    }
}

/**
 * Handle form submissions
 */
function handleFormSubmissions(event) {
    const form = event.target;
    
    // Add loading state to submit buttons
    const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
    submitButtons.forEach(button => {
        button.disabled = true;
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>დამუშავება...';
        
        // Reset after 5 seconds in case of errors
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalHTML;
        }, 5000);
    });
}

/**
 * Handle scroll events
 */
function handleScroll() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Show/hide scroll-to-top button
    toggleScrollToTopButton(scrollTop);
    
    // Update navbar on scroll
    updateNavbarOnScroll(scrollTop);
}

/**
 * Toggle scroll-to-top button
 */
function toggleScrollToTopButton(scrollTop) {
    let scrollBtn = document.getElementById('scrollToTop');
    
    if (!scrollBtn) {
        scrollBtn = document.createElement('button');
        scrollBtn.id = 'scrollToTop';
        scrollBtn.className = 'btn btn-primary position-fixed';
        scrollBtn.style.cssText = 'bottom: 2rem; right: 2rem; z-index: 1000; border-radius: 50%; width: 3rem; height: 3rem; display: none;';
        scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollBtn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
        document.body.appendChild(scrollBtn);
    }
    
    if (scrollTop > 300) {
        scrollBtn.style.display = 'block';
    } else {
        scrollBtn.style.display = 'none';
    }
}

/**
 * Update navbar appearance on scroll
 */
function updateNavbarOnScroll(scrollTop) {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    if (scrollTop > 50) {
        navbar.classList.add('navbar-scrolled');
    } else {
        navbar.classList.remove('navbar-scrolled');
    }
}

/**
 * Handle window resize
 */
function handleResize() {
    // Update mobile menu if needed
    updateMobileMenu();
    
    // Recalculate any responsive elements
    updateResponsiveElements();
}

/**
 * Update mobile menu
 */
function updateMobileMenu() {
    const isMobile = window.innerWidth < 768;
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        navbar.classList.toggle('mobile', isMobile);
    }
}

/**
 * Update responsive elements
 */
function updateResponsiveElements() {
    // Update any elements that need size recalculation
    const cards = document.querySelectorAll('.card-columns, .masonry');
    cards.forEach(card => {
        // Trigger reflow for masonry layouts if using any
        card.style.height = 'auto';
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    let toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Utility functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Performance monitoring
 */
function logPerformance() {
    if (performance && performance.timing) {
        const timing = performance.timing;
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        console.log(`Page load time: ${loadTime}ms`);
    }
}

// Log performance when page is fully loaded
window.addEventListener('load', logPerformance);

// Service Worker registration for PWA (if needed in future)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment to register service worker
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('SW registered'))
        //     .catch(error => console.log('SW registration failed'));
    });
}

// Export functions for global use
window.GamingHub = {
    showToast,
    copyToClipboard,
    removeImagePreview,
    // Add any other functions that need to be globally accessible
};
