// Luxury Digital Interface - AutoBios
// Smooth interactions and fluid animations

class LuxuryInterface {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.startAnimations();
    }

    init() {
        // Initialize time display
        this.updateTime();
        setInterval(() => this.updateTime(), 1000);

        // Initialize smooth scrolling
        this.setupSmoothScrolling();

        // Initialize hover effects
        this.setupHoverEffects();

        // Initialize loading states
        this.setupLoadingStates();

        // Initialize tooltips
        this.setupTooltips();
    }

    updateTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            timeElement.textContent = timeString;
        }
    }

    setupEventListeners() {
        // Navigation items
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.handleNavClick(e);
            });
        });

        // Tool items
        const toolItems = document.querySelectorAll('.tool-item');
        toolItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.handleToolClick(e);
            });
        });

        // Action buttons
        const actionButtons = document.querySelectorAll('.action-button');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleActionClick(e);
            });
        });

        // Card actions
        const cardActions = document.querySelectorAll('.card-action');
        cardActions.forEach(action => {
            action.addEventListener('click', (e) => {
                this.handleCardAction(e);
            });
        });

        // Toggle switches
        const toggles = document.querySelectorAll('.toggle-input');
        toggles.forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this.handleToggleChange(e);
            });
        });

        // Panel buttons
        const panelButtons = document.querySelectorAll('.panel-button');
        panelButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.handlePanelButton(e);
            });
        });

        // Recent items
        const recentItems = document.querySelectorAll('.recent-item');
        recentItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.handleRecentClick(e);
            });
        });
    }

    setupSmoothScrolling() {
        // Add smooth scrolling to all internal links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    setupHoverEffects() {
        // Enhanced hover effects for cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.animateCardHover(card, true);
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateCardHover(card, false);
            });
        });

        // Enhanced hover effects for buttons
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                this.animateButtonHover(button, true);
            });
            
            button.addEventListener('mouseleave', () => {
                this.animateButtonHover(button, false);
            });
        });
    }

    setupLoadingStates() {
        // Simulate loading for action buttons
        const actionButtons = document.querySelectorAll('.action-button');
        actionButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.showLoadingState(button);
            });
        });
    }

    setupTooltips() {
        // Add subtle tooltips to interactive elements
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            this.createTooltip(element);
        });
    }

    startAnimations() {
        // Staggered animation for cards on load
        this.animateCardsOnLoad();
        
        // Continuous subtle animations
        this.startContinuousAnimations();
    }

    animateCardsOnLoad() {
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    startContinuousAnimations() {
        // Subtle floating animation for status indicator
        const statusIndicator = document.querySelector('.status-indicator.online');
        if (statusIndicator) {
            setInterval(() => {
                statusIndicator.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    statusIndicator.style.transform = 'scale(1)';
                }, 200);
            }, 3000);
        }

        // Subtle pulse for progress bars
        const progressBars = document.querySelectorAll('.progress-fill');
        progressBars.forEach(bar => {
            setInterval(() => {
                bar.style.opacity = '0.8';
                setTimeout(() => {
                    bar.style.opacity = '1';
                }, 500);
            }, 2000);
        });
    }

    handleNavClick(e) {
        const clickedItem = e.currentTarget;
        
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to clicked item
        clickedItem.classList.add('active');
        
        // Add ripple effect
        this.createRippleEffect(clickedItem, e);
        
        // Show loading state briefly
        this.showBriefLoading();
    }

    handleToolClick(e) {
        const toolItem = e.currentTarget;
        
        // Add selection effect
        document.querySelectorAll('.tool-item').forEach(item => {
            item.classList.remove('selected');
        });
        toolItem.classList.add('selected');
        
        // Create ripple effect
        this.createRippleEffect(toolItem, e);
        
        // Simulate tool activation
        this.simulateToolActivation(toolItem);
    }

    handleActionClick(e) {
        const actionButton = e.currentTarget;
        
        // Create ripple effect
        this.createRippleEffect(actionButton, e);
        
        // Show loading state
        this.showLoadingState(actionButton);
        
        // Simulate action execution
        setTimeout(() => {
            this.hideLoadingState(actionButton);
            this.showSuccessFeedback(actionButton);
        }, 1500);
    }

    handleCardAction(e) {
        const cardAction = e.currentTarget;
        
        // Rotate icon
        cardAction.style.transform = 'rotate(180deg)';
        setTimeout(() => {
            cardAction.style.transform = 'rotate(0deg)';
        }, 300);
        
        // Create ripple effect
        this.createRippleEffect(cardAction, e);
    }

    handleToggleChange(e) {
        const toggle = e.currentTarget;
        const label = toggle.nextElementSibling;
        
        // Add smooth transition
        label.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        // Create feedback animation
        if (toggle.checked) {
            this.animateToggleOn(label);
        } else {
            this.animateToggleOff(label);
        }
    }

    handlePanelButton(e) {
        const panelButton = e.currentTarget;
        
        // Scale animation
        panelButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            panelButton.style.transform = 'scale(1)';
        }, 150);
        
        // Create ripple effect
        this.createRippleEffect(panelButton, e);
    }

    handleRecentClick(e) {
        const recentItem = e.currentTarget;
        
        // Highlight effect
        recentItem.style.background = 'var(--color-accent-light)';
        setTimeout(() => {
            recentItem.style.background = '';
        }, 300);
        
        // Create ripple effect
        this.createRippleEffect(recentItem, e);
    }

    animateCardHover(card, isEntering) {
        if (isEntering) {
            card.style.transform = 'translateY(-4px) scale(1.02)';
            card.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.12)';
        } else {
            card.style.transform = 'translateY(0) scale(1)';
            card.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.04)';
        }
    }

    animateButtonHover(button, isEntering) {
        if (isEntering) {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.08)';
        } else {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = 'none';
        }
    }

    createRippleEffect(element, event) {
        const ripple = document.createElement('div');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(212, 175, 55, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
            z-index: 1000;
        `;
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    showLoadingState(element) {
        element.classList.add('loading');
        element.style.pointerEvents = 'none';
    }

    hideLoadingState(element) {
        element.classList.remove('loading');
        element.style.pointerEvents = 'auto';
    }

    showBriefLoading() {
        const statusText = document.querySelector('.status-text');
        if (statusText) {
            const originalText = statusText.textContent;
            statusText.textContent = 'Processing...';
            statusText.style.color = 'var(--color-accent)';
            
            setTimeout(() => {
                statusText.textContent = originalText;
                statusText.style.color = '';
            }, 1000);
        }
    }

    showSuccessFeedback(element) {
        const originalContent = element.innerHTML;
        element.innerHTML = '<div class="success-icon">✓</div>';
        element.style.color = 'var(--color-accent)';
        
        setTimeout(() => {
            element.innerHTML = originalContent;
            element.style.color = '';
        }, 1500);
    }

    simulateToolActivation(toolItem) {
        const toolIcon = toolItem.querySelector('.tool-icon');
        toolIcon.style.background = 'var(--color-accent-light)';
        toolIcon.style.borderColor = 'var(--color-accent)';
        
        setTimeout(() => {
            toolIcon.style.background = '';
            toolIcon.style.borderColor = '';
        }, 2000);
    }

    animateToggleOn(label) {
        const slider = label.querySelector('.toggle-slider');
        slider.style.transform = 'translateX(24px) scale(1.1)';
        setTimeout(() => {
            slider.style.transform = 'translateX(24px) scale(1)';
        }, 150);
    }

    animateToggleOff(label) {
        const slider = label.querySelector('.toggle-slider');
        slider.style.transform = 'translateX(0) scale(0.9)';
        setTimeout(() => {
            slider.style.transform = 'translateX(0) scale(1)';
        }, 150);
    }

    createTooltip(element) {
        const tooltipText = element.getAttribute('data-tooltip');
        if (!tooltipText) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        tooltip.style.cssText = `
            position: absolute;
            background: var(--color-text-primary);
            color: var(--color-surface);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            z-index: 1000;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(tooltip);
        
        element.addEventListener('mouseenter', () => {
            const rect = element.getBoundingClientRect();
            tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            tooltip.style.opacity = '1';
        });
        
        element.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
        });
    }
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .tool-item.selected {
        background: var(--color-accent-light);
        border-color: var(--color-accent);
    }
    
    .success-icon {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .tooltip {
        font-family: var(--font-family);
    }
`;
document.head.appendChild(style);

// Initialize the luxury interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LuxuryInterface();
});

// Add smooth page transitions
window.addEventListener('beforeunload', () => {
    document.body.style.opacity = '0';
    document.body.style.transform = 'scale(0.98)';
});

// Add keyboard navigation support
document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-navigation');
});

// Add CSS for keyboard navigation
const keyboardStyle = document.createElement('style');
keyboardStyle.textContent = `
    .keyboard-navigation *:focus {
        outline: 2px solid var(--color-accent) !important;
        outline-offset: 2px !important;
    }
`;
document.head.appendChild(keyboardStyle);