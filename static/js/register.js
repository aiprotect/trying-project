    // افکت‌های تعاملی
    document.querySelectorAll('.input-group input').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentNode.querySelector('i').style.color = '#4361ee';
            this.style.paddingRight = '50px';
        });

        input.addEventListener('blur', function() {
            if (this.value === '') {
                this.parentNode.querySelector('i').style.color = '#999';
            }
        });
    });
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const termsCheckbox = document.getElementById('terms');

    if (form) {
        form.addEventListener('submit', function(e) {
            if (!termsCheckbox.checked) {
                e.preventDefault();

                Swal.fire({
                    title: 'توجه!',
                    text: 'برای ادامه، لطفاً با قوانین و شرایط موافقت کنید',
                    icon: 'warning',
                    iconColor: '#f8bb86',
                    confirmButtonText: 'متوجه شدم',
                    confirmButtonColor: '#6a11cb',
                    background: '#fff',
                    backdrop: `
                        rgba(0,0,0,0.4)
                        url("https://i.gifer.com/origin/b4/b4d657e7ef262b88eb5f7ac021edda87.gif")
                        center top
                        no-repeat
                    `,
                    customClass: {
                        title: 'swal-title',
                        confirmButton: 'swal-button'
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        termsCheckbox.focus();
                    }
                });
            }
        });
    }
});