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
    const counters = document.querySelectorAll('.stat-number [data-target]');
    counters.forEach(counter => {
        const targetAttr = counter.getAttribute('data-target');
        if (!targetAttr) return;
        const target = parseInt(targetAttr);
        if (isNaN(target) || target <= 0) {
            counter.textContent = targetAttr || '0';
            return;
        }
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
const videoWrapper = document.querySelector('.about-video-wrapper');

if (aboutVideo) {
    // Видео играет со звуком, без привязки к скроллу
    aboutVideo.muted = false;
    aboutVideo.volume = 0.33;
    aboutVideo.play().catch(() => {});

    if (videoOverlay) {
        videoOverlay.classList.add('hidden');
    }

    // Клик по любой части видео-обертки для play/pause
    if (videoWrapper) {
        videoWrapper.addEventListener('click', (e) => {
            if (e.target.tagName === 'VIDEO' && (e.target.hasAttribute('controls') || document.querySelector('.about-video[controls]'))) {
                return;
            }
            if (aboutVideo.paused) {
                aboutVideo.play();
            } else {
                aboutVideo.pause();
            }
        });
    }
}

// ===== FORM SUBMISSION TO BACKEND API =====
(function() {
    const API_URL = '/api/lead';

    const form = document.getElementById('contactForm');
    if (!form) return;

    const successBlock = document.getElementById('formSuccess');
    const submitButton = form.querySelector('button[type="submit"]');
    const btnText = submitButton ? submitButton.querySelector('.btn-text') : null;
    const btnLoader = submitButton ? submitButton.querySelector('.btn-loader') : null;

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
            if (btnText) btnText.style.display = 'none';
            if (btnLoader) btnLoader.style.display = 'inline';
        }

        var xhr = new XMLHttpRequest();
        xhr.open('POST', API_URL, true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onload = function() {
            if (submitButton) {
                submitButton.disabled = false;
                if (btnText) btnText.style.display = 'inline';
                if (btnLoader) btnLoader.style.display = 'none';
            }

            if (xhr.status === 200) {
                try {
                    var resp = JSON.parse(xhr.responseText);
                    if (resp.status === 'success') {
                        form.style.display = 'none';
                        if (successBlock) successBlock.style.display = 'block';
                    } else {
                        alert('Ошибка отправки. Попробуйте позже или напишите в Telegram @bek_english_tutor');
                    }
                } catch(e) {
                    alert('Ошибка отправки. Попробуйте позже или напишите в Telegram @bek_english_tutor');
                }
            } else {
                alert('Ошибка соединения. Попробуйте позже или напишите в Telegram @bek_english_tutor');
            }
        };

        xhr.onerror = function() {
            if (submitButton) {
                submitButton.disabled = false;
                if (btnText) btnText.style.display = 'inline';
                if (btnLoader) btnLoader.style.display = 'none';
            }
            alert('Ошибка соединения. Попробуйте позже или напишите в Telegram @bek_english_tutor');
        };

        var data = JSON.stringify({
            name: name,
            phone: phone,
            email: email,
            goal: goal,
            message: comment,
            privacy: true
        });

        xhr.send(data);
    });
})();
