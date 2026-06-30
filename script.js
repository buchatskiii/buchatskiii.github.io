// ===== BURGER MENU =====
const burger = document.getElementById('burger');
const navLinks = document.querySelector('.nav-links');

burger.addEventListener('click', () => {
    burger.classList.toggle('active');
    navLinks.classList.toggle('active');
});

document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        burger.classList.remove('active');
        navLinks.classList.remove('active');
    });
});

// ===== FAQ ACCORDION =====
const faqItems = document.querySelectorAll('.faq-item');

faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    question.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        faqItems.forEach(i => i.classList.remove('active'));
        if (!isActive) {
            item.classList.add('active');
        }
    });
});

// ===== COUNTER ANIMATION =====
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000;
        const step = Math.ceil(target / (duration / 16));
        let current = 0;
        const updateCounter = () => {
            current += step;
            if (current >= target) {
                counter.textContent = target;
                return;
            }
            counter.textContent = current;
            requestAnimationFrame(updateCounter);
        };
        updateCounter();
    });
}

const heroSection = document.querySelector('.hero');
let countersAnimated = false;

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !countersAnimated) {
            countersAnimated = true;
            animateCounters();
        }
    });
}, { threshold: 0.3 });

observer.observe(heroSection);

// ===== SMOOTH SCROLL =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const headerOffset = 80;
            const elementPosition = target.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ===== STICKY NAVBAR =====
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    if (currentScroll > 100) {
        navbar.style.background = 'rgba(45, 52, 54, 0.95)';
        navbar.style.backdropFilter = 'blur(10px)';
        navbar.style.padding = '12px 0';
        navbar.style.borderRadius = '0 0 16px 16px';
    } else {
        navbar.style.background = 'transparent';
        navbar.style.backdropFilter = 'none';
        navbar.style.padding = '20px 0';
    }
});

// ===== SCROLL REVEAL =====
const revealElements = document.querySelectorAll('.section');
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

revealElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    revealObserver.observe(el);
});

// ===== PHONE MASK =====
const phoneInput = document.getElementById('phone');
if (phoneInput) {
    phoneInput.addEventListener('input', function(e) {
        let value = this.value.replace(/\D/g, '');
        if (value.length === 0) {
            this.value = '';
            return;
        }
        if (value.length <= 1) {
            this.value = '+7';
        } else if (value.length <= 4) {
            this.value = '+7 (' + value.substring(1, 4);
        } else if (value.length <= 7) {
            this.value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7);
        } else if (value.length <= 9) {
            this.value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7, 9);
        } else if (value.length <= 11) {
            this.value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7, 9) + '-' + value.substring(9, 11);
        } else {
            this.value = '+7 (' + value.substring(1, 4) + ') ' + value.substring(4, 7) + '-' + value.substring(7, 9) + '-' + value.substring(9, 11);
        }
    });
}

// ===== VIDEO AUTOPLAY =====
const aboutVideo = document.getElementById('aboutVideo');
const videoOverlay = document.getElementById('videoPlayOverlay');
let videoPlayed = false;

if (aboutVideo) {
    const videoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !videoPlayed) {
                aboutVideo.play().then(() => {
                    if (videoOverlay) videoOverlay.classList.add('hidden');
                    videoPlayed = true;
                }).catch(() => {});
            } else if (!entry.isIntersecting && !aboutVideo.paused) {
                aboutVideo.pause();
            }
        });
    }, { threshold: 0.5 });

    videoObserver.observe(aboutVideo);

    if (videoOverlay) {
        videoOverlay.addEventListener('click', () => {
            aboutVideo.play();
            videoOverlay.classList.add('hidden');
            videoPlayed = true;
        });
    }

    aboutVideo.addEventListener('click', () => {
        if (aboutVideo.paused) {
            aboutVideo.play();
        } else {
            aboutVideo.pause();
        }
    });

    aboutVideo.addEventListener('ended', () => {
        if (videoOverlay) videoOverlay.classList.remove('hidden');
        videoPlayed = false;
    });
}

// ===== FORM SUBMISSION TO TELEGRAM =====
const BOT_TOKEN = '8907288687:AAFZ7z0Fl3Rp_MwRCQsKNuznJxp3kFfiXW4';
const CHAT_ID = '745673632';

const form = document.getElementById('contactForm');
const submitBtn = document.getElementById('submitBtn');
const formSuccess = document.getElementById('formSuccess');

if (form) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const privacyCheckbox = document.getElementById('privacy');
        if (!privacyCheckbox || !privacyCheckbox.checked) {
            alert('Пожалуйста, примите согласие на обработку персональных данных');
            return;
        }

        const name = document.getElementById('name').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const email = document.getElementById('email').value.trim();
        const goal = document.getElementById('goal').value;
        const message = document.getElementById('message').value.trim();

        if (!name || !phone || !email) {
            alert('Пожалуйста, заполните все обязательные поля');
            return;
        }

        submitBtn.disabled = true;
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoader = submitBtn.querySelector('.btn-loader');
        if (btnText) btnText.textContent = 'Отправка...';
        if (btnLoader) btnLoader.style.display = 'inline';

        const goalLabels = {
            'ege': 'Подготовка к ЕГЭ',
            'oge': 'Подготовка к ОГЭ',
            'ielts': 'IELTS / TOEFL',
            'general': 'Общий английский',
            'other': 'Другое'
        };

        const text = '📩 <b>Новая заявка с сайта!</b>\n\n' +
            '👤 <b>Имя:</b> ' + name + '\n' +
            '📞 <b>Телефон:</b> ' + phone + '\n' +
            '📧 <b>Email:</b> ' + email + '\n' +
            '🎯 <b>Цель:</b> ' + (goalLabels[goal] || 'Не указана') + '\n' +
            '💬 <b>Комментарий:</b> ' + (message || 'Нет') + '\n\n' +
            '🕐 ' + new Date().toLocaleString('ru-RU');

        try {
            const response = await fetch('https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: CHAT_ID,
                    text: text,
                    parse_mode: 'HTML'
                })
            });

            const result = await response.json();

            if (result.ok) {
                form.style.display = 'none';
                if (formSuccess) formSuccess.style.display = 'block';
            } else {
                throw new Error(result.description || 'Ошибка отправки');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('❌ Не удалось отправить заявку. Пожалуйста, попробуйте позже или свяжитесь напрямую через Telegram @englishtutortest_bot');
        } finally {
            submitBtn.disabled = false;
            if (btnText) btnText.textContent = 'Отправить заявку';
            if (btnLoader) btnLoader.style.display = 'none';
        }
    });
}
