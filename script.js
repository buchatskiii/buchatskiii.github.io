// ===== BURGER MENU =====
const burger = document.getElementById('burger');
const navLinks = document.querySelector('.nav-links');

burger.addEventListener('click', () => {
    burger.classList.toggle('active');
    navLinks.classList.toggle('active');
});

// Close menu on link click
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
        
        // Close all
        faqItems.forEach(i => i.classList.remove('active'));
        
        // Toggle current
        if (!isActive) {
            item.classList.add('active');
        }
    });
});

// ===== COUNTER ANIMATION =====
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number [data-target]');
    
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

// Trigger counter animation when hero is in view
const heroSection = document.querySelector('.hero');
let countersAnimated = false;

const observerOptions = {
    threshold: 0.3
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !countersAnimated) {
            countersAnimated = true;
            animateCounters();
        }
    });
}, observerOptions);

observer.observe(heroSection);

// ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
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

// ===== FORM HANDLING - Прямая отправка в Telegram =====
const contactForm = document.getElementById('contactForm');

// Telegram Bot Configuration
const TELEGRAM_BOT_TOKEN = '8907288687:AAHRBarHQyV1cBXYLIpRR4ji_b2-Pw31jxg';
const TELEGRAM_CHAT_ID = '745673632';

contactForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Get form data
    const formData = new FormData(this);
    const data = Object.fromEntries(formData);
    
    // Simple validation
    const name = data.name?.trim();
    const phone = data.phone?.trim();
    const email = data.email?.trim();
    const privacy = data.privacy;
    
    if (!name || !phone || !email) {
        showFormMessage('Пожалуйста, заполните все обязательные поля', 'error');
        return;
    }
    
    if (!privacy) {
        // Подсвечиваем чекбокс и показываем подсказку
        const privacyGroup = document.getElementById('privacyGroup');
        privacyGroup.classList.add('has-error');
        
        // Убираем подсветку при клике на чекбокс
        const privacyCheckbox = document.getElementById('privacy');
        privacyCheckbox.addEventListener('change', function onCheck() {
            privacyGroup.classList.remove('has-error');
            privacyCheckbox.removeEventListener('change', onCheck);
        }, { once: true });
        
        // Прокручиваем к чекбоксу
        privacyGroup.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        showFormMessage('Пожалуйста, отметьте согласие с политикой конфиденциальности', 'error');
        return;
    }
    
    // Phone validation (simple)
    const phoneRegex = /^[\+\d\s\-\(\)]{7,20}$/;
    if (!phoneRegex.test(phone)) {
        showFormMessage('Пожалуйста, введите корректный номер телефона', 'error');
        return;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showFormMessage('Пожалуйста, введите корректный email', 'error');
        return;
    }
    
    // Отправка напрямую в Telegram через Bot API
    const submitBtn = this.querySelector('.btn-submit');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '⏳ Отправка...';
    submitBtn.disabled = true;
    
    try {
        const goalText = {
            'ege': 'ЕГЭ',
            'oge': 'ОГЭ',
            'ielts': 'IELTS/TOEFL',
            'general': 'Общий английский',
            'other': 'Другое'
        }[data.goal] || data.goal || 'Не указана';
        
        const message = '📩 <b>Новая заявка с сайта!</b>\n\n' +
            '👤 <b>Имя:</b> ' + name + '\n' +
            '📞 <b>Телефон:</b> ' + phone + '\n' +
            '📧 <b>Email:</b> ' + email + '\n' +
            '🎯 <b>Цель:</b> ' + goalText + '\n' +
            (data.message ? '💬 <b>Комментарий:</b> ' + data.message + '\n' : '') +
            '✅ <b>Согласие с политикой:</b> Да\n' +
            '🕐 <b>Время:</b> ' + new Date().toLocaleString('ru-RU');
        
        const response = await fetch('https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_id: TELEGRAM_CHAT_ID,
                text: message,
                parse_mode: 'HTML',
            }),
        });
        
        const result = await response.json();
        
        if (response.ok && result.ok) {
            showFormMessage('✅ Спасибо! Ваша заявка принята. Я свяжусь с вами в течение 2 часов.', 'success');
            contactForm.reset();
        } else {
            showFormMessage('❌ Ошибка отправки. Пожалуйста, попробуйте позже или напишите мне в Telegram @anna_english_tutor', 'error');
        }
    } catch (error) {
        console.error('Ошибка отправки:', error);
        showFormMessage('❌ Не удалось отправить заявку. Проверьте подключение к интернету или попробуйте позже.', 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

function showFormMessage(message, type) {
    // Remove existing message
    const existingMsg = document.querySelector('.form-message');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    const msgDiv = document.createElement('div');
    msgDiv.className = 'form-message form-message--' + type;
    msgDiv.textContent = message;
    
    const form = document.getElementById('contactForm');
    form.insertBefore(msgDiv, form.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(function() {
        msgDiv.remove();
    }, 5000);
}

// ===== STICKY NAVBAR ON SCROLL =====
let lastScroll = 0;
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
    
    lastScroll = currentScroll;
});

// ===== SCROLL REVEAL ANIMATIONS =====
const revealElements = document.querySelectorAll('.section');

const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, {
    threshold: 0.1
});

revealElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    revealObserver.observe(el);
});

// ===== PHONE INPUT MASK =====
const phoneInput = document.getElementById('phone');

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

// ===== VIDEO AUTOPLAY ON SCROLL =====
const aboutVideo = document.getElementById('aboutVideo');
const videoOverlay = document.getElementById('videoPlayOverlay');
let videoPlayed = false;

if (aboutVideo) {
    // Intersection Observer для автоплея при скролле
    const videoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !videoPlayed) {
                aboutVideo.play().then(() => {
                    videoOverlay.classList.add('hidden');
                    videoPlayed = true;
                }).catch(() => {
                    // Браузер заблокировал автовоспроизведение - ждём клика
                });
            } else if (!entry.isIntersecting && aboutVideo.paused === false) {
                aboutVideo.pause();
            }
        });
    }, { threshold: 0.5 });

    videoObserver.observe(aboutVideo);

    // Клик по overlay для запуска видео
    videoOverlay.addEventListener('click', () => {
        aboutVideo.play();
        videoOverlay.classList.add('hidden');
        videoPlayed = true;
    });

    // Клик по самому видео - пауза/плей
    aboutVideo.addEventListener('click', () => {
        if (aboutVideo.paused) {
            aboutVideo.play();
        } else {
            aboutVideo.pause();
        }
    });

    // Когда видео закончилось - показываем overlay снова
    aboutVideo.addEventListener('ended', () => {
        videoOverlay.classList.remove('hidden');
        videoPlayed = false;
    });
}
