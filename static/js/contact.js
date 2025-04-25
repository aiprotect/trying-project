
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('main-contact-form');
    const fileInput = document.getElementById('image_profile');
    const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

    // تابع اعتبارسنجی ایمیل
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // تابع نمایش خطا
    function showError(message) {
        Swal.fire({
            title: 'خطا!',
            text: message,
            icon: 'error',
            confirmButtonText: 'متوجه شدم',
            confirmButtonColor: 'var(--primary-color)'
        });
    }

    // مدیریت انتخاب فایل
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const file = this.files[0];
                
                if (!validImageTypes.includes(file.type)) {
                    showError('لطفاً فقط تصاویر (JPG, PNG, GIF, WEBP) انتخاب کنید');
                    this.value = '';
                }
            }
        });
    }

    // مدیریت ارسال فرم
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // دریافت مقادیر فرم
            const email = contactForm.querySelector('[name="email"]').value.trim();
            const fullName = contactForm.querySelector('[name="full_name"]').value.trim();
            const subject = contactForm.querySelector('[name="subject"]').value.trim();
            const message = contactForm.querySelector('[name="message"]').value.trim();

            // اعتبارسنجی فیلدهای ضروری
            if (!email || !fullName || !subject || !message) {
                showError('لطفاً تمام فیلدهای ضروری را پر کنید');
                return;
            }

            // اعتبارسنجی ایمیل
            if (!isValidEmail(email)) {
                showError('لطفاً یک آدرس ایمیل معتبر وارد کنید');
                return;
            }

            // اعتبارسنجی فایل اگر انتخاب شده باشد
            if (fileInput.files.length > 0 && !validImageTypes.includes(fileInput.files[0].type)) {
                showError('لطفاً فقط تصاویر معتبر انتخاب کنید');
                return;
            }

            // غیرفعال کردن دکمه ارسال
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> در حال ارسال...';
            submitBtn.disabled = true;

            // آماده‌سازی داده‌های فرم
            const formData = new FormData(contactForm);

            // ارسال درخواست
            fetch(contactForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: 'پیام ارسال شد!',
                        text: 'پیام شما با موفقیت ارسال شد. به زودی با شما تماس خواهیم گرفت.',
                        icon: 'success',
                        confirmButtonText: 'متوجه شدم',
                        confirmButtonColor: 'var(--primary-color)'
                    }).then(() => {
                        // ریدایرکت به صفحه اصلی
                        window.location.href = "/";
                    });
                } else {
                    let errorMessage = 'خطا در ارسال پیام';
                    if (data.errors) {
                        errorMessage = Object.values(data.errors).join('\n');
                    }
                    showError(errorMessage);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('مشکلی در ارتباط با سرور پیش آمد. لطفاً مجدداً تلاش کنید.');
            })
            .finally(() => {
                // فعال کردن مجدد دکمه ارسال
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            });
        });
    }
});
