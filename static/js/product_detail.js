
// تغییر تب‌ها
const tabHeaders = document.querySelectorAll('.tab-header');
tabHeaders.forEach(header => {
    header.addEventListener('click', () => {
        // حذف کلاس active از همه تب‌ها
        document.querySelector('.tab-header.active').classList.remove('active');
        document.querySelector('.tab-content.active').classList.remove('active');
        
        // اضافه کردن کلاس active به تب انتخاب شده
        header.classList.add('active');
        const tabId = header.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// تغییر تصاویر گالری
const thumbnails = document.querySelectorAll('.thumbnail');
const mainImage = document.querySelector('.main-image');

thumbnails.forEach(thumb => {
    thumb.addEventListener('click', () => {
        // حذف کلاس active از همه تصاویر کوچک
        document.querySelector('.thumbnail.active').classList.remove('active');
        
        // اضافه کردن کلاس active به تصویر انتخاب شده
        thumb.classList.add('active');
        
        // تغییر تصویر اصلی
        const imgSrc = thumb.querySelector('img').getAttribute('src');
        mainImage.setAttribute('src', imgSrc);
    });
});

// تغییر تعداد محصول
const decreaseBtn = document.getElementById('decrease-qty');
const increaseBtn = document.getElementById('increase-qty');
const qtyInput = document.querySelector('.qty-input');

decreaseBtn.addEventListener('click', (e) => {
    e.preventDefault();
    let currentVal = parseInt(qtyInput.value);
    if(currentVal > 1) {
        qtyInput.value = currentVal - 1;
    }
});

increaseBtn.addEventListener('click', (e) => {
    e.preventDefault();
    let currentVal = parseInt(qtyInput.value);
    if(currentVal < 10) {
        qtyInput.value = currentVal + 1;
    }
});

// زوم تصویر
const zoomBtn = document.getElementById('zoom-btn');
const zoomOverlay = document.querySelector('.zoom-overlay');
const closeZoom = document.querySelector('.close-zoom');
const zoomedImage = document.querySelector('.zoomed-image');

zoomBtn.addEventListener('click', () => {
    const imgSrc = mainImage.getAttribute('src');
    zoomedImage.setAttribute('src', imgSrc);
    zoomOverlay.classList.add('active');
});

closeZoom.addEventListener('click', () => {
    zoomOverlay.classList.remove('active');
});

zoomOverlay.addEventListener('click', (e) => {
    if(e.target === zoomOverlay) {
        zoomOverlay.classList.remove('active');
    }
});

// منوی موبایل
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const nav = document.querySelector('.nav');

mobileMenuBtn.addEventListener('click', () => {
    nav.style.display = nav.style.display === 'block' ? 'none' : 'block';
});
