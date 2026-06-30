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
(function() {
    const TOKEN = '8907288687:AAFZ7z0Fl3Rp_MwRCQsKNuznJxp3kFfiXW4';
    const CHAT = '745673632';
    const API = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage';

    const form = document.getElementById('contactForm');
    if (!form) return;

    const successBlock = document.getElementById('formSuccess');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', function(evt) {
        evt.preventDefault();

        const agree = document.getElementById('privacy');
        if (!agree || !agree.checked) {
            alert('Необходимо дать согласие на обработку персональных данных');
            return;
        }

        const name = document.getElementById('name').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const email = document.getElementById('email').value.trim();
        const goal = document.getElementById('goal').value;
        const comment = document.getElementById('message').value.trim();

        if (name === '' || phone === '' || email === '') {
            alert('Заполните имя, телефон и email');
            return;
        }

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Отправляем...';
        }

        const goalNames = {
            'ege': 'ЕГЭ',
            'oge': 'ОГЭ',
            'ielts': 'IELTS/TOEFL',
            'general': 'Общий английский',
            'other': 'Другое'
        };

        const now = new Date();
        const dateStr = now.toLocaleDateString('ru-RU') + ' ' + now.toLocaleTimeString('ru-RU');

        const msg = '<b>📩 Новая заявка</b>\n\n' +
            '👤 <b>Имя:</b> ' + name + '\n' +
            '📞 <b>Телефон:</b> ' + phone + '\n' +
            '📧 <b>Email:</b> ' + email + '\n' +
            '🎯 <b>Цель:</b> ' + (goalNames[goal] || 'Не указана') + '\n' +
            '💬 <b>Комментарий:</b> ' + (comment || '—') + '\n\n' +
            '🕐 ' + dateStr;

        var xhr = new XMLHttpRequest();
        xhr.open('POST', API, true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onload = function() {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Отправить заявку';
            }

            if (xhr.status === 200) {
                var resp = JSON.parse(xhr.responseText);
                if (resp.ok) {
                    form.style.display = 'none';
                    if (successBlock) successBlock.style.display = 'block';
                } else {
                    alert('Ошибка отправки. Попробуйте позже или напишите в Telegram @englishtutortest_bot');
                }
            } else {
                alert('Ошибка соединения. Попробуйте позже или напишите в Telegram @englishtutortest_bot');
            }
        };

        xhr.onerror = function() {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Отправить заявку';
            }
            alert('Ошибка соединения. Попробуйте позже или напишите в Telegram @englishtutortest_bot');
        };

        var data = JSON.stringify({
            chat_id: CHAT,
            text: msg,
            parse_mode: 'HTML'
        });

        xhr.send(data);
    });
})();
