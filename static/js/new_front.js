document.addEventListener('DOMContentLoaded', function() {
    // Initialize hero slider
    const heroSwiper = new Swiper('.heroSwiper', {
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
    });

    // Initialize products slider
    const productsSwiper = new Swiper('.productsSwiper', {
        slidesPerView: 4,
        spaceBetween: 20,
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        breakpoints: {
            320: {
                slidesPerView: 1,
            },
            576: {
                slidesPerView: 2,
            },
            768: {
                slidesPerView: 3,
            },
            992: {
                slidesPerView: 4,
            },
        }
    });

    // Mobile menu toggle


    
    const mainNav = document.querySelector('.main-nav');

    


    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const cartCount = document.querySelector('.cart-count');
            let count = parseInt(cartCount.textContent);
            cartCount.textContent = count + 1;
            
            // Animation
            const clone = this.cloneNode(true);
            clone.style.position = 'fixed';
            clone.style.zIndex = '9999';
            clone.style.fontSize = '20px';
            clone.style.transition = 'all 0.5s ease';
            
            const rect = this.getBoundingClientRect();
            clone.style.left = `${rect.left}px`;
            clone.style.top = `${rect.top}px`;
            document.body.appendChild(clone);
            
            const cartRect = document.querySelector('.cart-icon').getBoundingClientRect();
            clone.style.left = `${cartRect.left}px`;
            clone.style.top = `${cartRect.top}px`;
            clone.style.transform = 'scale(0.5)';
            clone.style.opacity = '0';
            
            setTimeout(() => {
                clone.remove();
            }, 500);
            
            // Show notification
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = 'محصول به سبد خرید اضافه شد';
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 3000);
        });
    });

    // Quick view modal
    const quickViewButtons = document.querySelectorAll('.quick-view');
    quickViewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // In a real project, you would fetch product details and show them in a modal
            alert('نمایش سریع محصول - این بخش در نسخه کامل پیاده‌سازی می‌شود');
        });
    });

    // Wishlist functionality
    const wishlistButtons = document.querySelectorAll('.add-to-wishlist');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            this.classList.toggle('active');
            
            if (this.classList.contains('active')) {
                this.innerHTML = '<i class="fas fa-heart"></i>';
                this.style.color = 'var(--danger)';
                // Show notification
                alert('محصول به لیست علاقه‌مندی‌ها اضافه شد');
            } else {
                this.innerHTML = '<i class="far fa-heart"></i>';
                this.style.color = 'inherit';
            }
        });
    });
});

// Notification style
const style = document.createElement('style');
style.textContent = `
.notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: var(--primary);
    color: white;
    padding: 15px 25px;
    border-radius: 5px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    transform: translateY(100px);
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 9999;
}

.notification.show {
    transform: translateY(0);
    opacity: 1;
}

@media (max-width: 768px) {
    .main-nav {
        display: none;
        width: 100%;
        padding: 15px 0;
    }
    
    .main-nav.active {
        display: block;
    }
    
    .main-nav ul {
        flex-direction: column;
    }
    

`;

document.addEventListener('DOMContentLoaded', function() {
        const msSlider = {
            init() {
                this.slides = document.querySelectorAll('.ms-slide');
                this.sliderWrapper = document.querySelector('.ms-slider-wrapper');
                this.prevBtn = document.querySelector('.ms-prev-btn');
                this.nextBtn = document.querySelector('.ms-next-btn');
                this.currentIndex = 0;

                this.createPagination();
                this.setupEvents();
                this.updateSlider();
            },

            createPagination() {
                const pagination = document.querySelector('.ms-pagination');
                pagination.innerHTML = '';

                this.slides.forEach((_, index) => {
                    const dot = document.createElement('div');
                    dot.classList.add('ms-dot');
                    if (index === 0) dot.classList.add('active');
                    dot.addEventListener('click', () => this.goToSlide(index));
                    pagination.appendChild(dot);
                });
            },

            setupEvents() {
                this.prevBtn.addEventListener('click', () => this.prevSlide());
                this.nextBtn.addEventListener('click', () => this.nextSlide());
            },

            prevSlide() {
                this.currentIndex = (this.currentIndex - 1 + this.slides.length) % this.slides.length;
                this.updateSlider();
            },

            nextSlide() {
                this.currentIndex = (this.currentIndex + 1) % this.slides.length;
                this.updateSlider();
            },

            goToSlide(index) {
                this.currentIndex = index;
                this.updateSlider();
            },

            updateSlider() {
                this.sliderWrapper.style.transform = `translateX(-${this.currentIndex * 100}%)`;

                // Update pagination
                document.querySelectorAll('.ms-dot').forEach((dot, index) => {
                    dot.classList.toggle('active', index === this.currentIndex);
                });
            }
        };

        msSlider.init();

        // Auto-rotate slides every 5 seconds
        setInterval(() => msSlider.nextSlide(), 5000);
    });
document.head.appendChild(style);
