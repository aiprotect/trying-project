        // اسکریپت برای دکمه‌های علاقه‌مندی
        document.querySelectorAll('.wishlist-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const icon = this.querySelector('i');
                icon.classList.toggle('far');
                icon.classList.toggle('fas');
                
                if (icon.classList.contains('fas')) {
                    this.style.animation = 'pulse 0.5s';
                    setTimeout(() => {
                        this.style.animation = '';
                    }, 500);
                }
            });
        });

        // اسکریپت برای نمایش تابعی
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                
                if (this.classList.contains('wishlist-btn')) {
                    tooltip.textContent = 'افزودن به علاقه‌مندی‌ها';
                } else if (this.classList.contains('quick-view-btn')) {
                    tooltip.textContent = 'مشاهده سریع';
                } else if (this.classList.contains('add-to-cart-btn')) {
                    tooltip.textContent = 'افزودن به سبد خرید';
                }
                
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
                tooltip.classList.add('active');
                
                this.addEventListener('mouseleave', () => {
                    tooltip.remove();
                }, { once: true });
            });
        });
