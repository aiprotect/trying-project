document.addEventListener('DOMContentLoaded', function() {
    // Initialize particles.js
    particlesJS('particles-js', {
        particles: {
            number: { value: 80, density: { enable: true, value_area: 800 } },
            color: { value: "#ffffff" },
            shape: { type: "circle" },
            opacity: { value: 0.3, random: true },
            size: { value: 3, random: true },
            line_linked: { enable: true, distance: 150, color: "#ffffff", opacity: 0.2, width: 1 },
            move: { enable: true, speed: 1, direction: "none", random: true }
        },
        interactivity: {
            detect_on: "canvas",
            events: {
                onhover: { enable: true, mode: "grab" },
                onclick: { enable: true, mode: "push" },
                resize: true
            }
        }
    });

    // Show notifications from Django messages
    {% if messages %}
        {% for message in messages %}
            showNotification('{{ message.tags }}', '{{ message|escapejs }}');
        {% endfor %}
    {% endif %}

    // Add error classes to form fields
    document.querySelectorAll('.error-message').forEach(errorElement => {
        const inputId = errorElement.previousElementSibling.id;
        const input = document.getElementById(inputId);
        if (input) {
            input.classList.add('is-invalid');
            
            // Remove error on input
            input.addEventListener('input', function() {
                if (this.value.trim() !== '') {
                    this.classList.remove('is-invalid');
                    const errorDiv = this.nextElementSibling;
                    if (errorDiv && errorDiv.classList.contains('error-message')) {
                        errorDiv.style.display = 'none';
                    }
                }
            });
        }
    });

    // Form submission handling
    const form = document.querySelector('.contact-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // You can add additional client-side validation here
        });
    }
});

// Notification function
function showNotification(type, message) {
    const container = document.createElement('div');
    container.className = 'notification-container';
    document.body.appendChild(container);
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    let icon;
    switch(type) {
        case 'success':
            icon = '<i class="fas fa-check-circle"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-exclamation-circle"></i>';
            break;
        default:
            icon = '<i class="fas fa-info-circle"></i>';
    }
    
    notification.innerHTML = `${icon} ${message}`;
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
            if (container.children.length === 0) {
                container.remove();
            }
        }, 500);
    }, 5000);
}