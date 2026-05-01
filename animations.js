/**
 * ANIMATIONS.JS - Método Fábrica Viral v2.0 Premium — REFINADO
 * Descrição: Sistema de animações profissional, partículas e efeitos
 * Versão: 2.1
 */

const animations = {
  // ===== SCROLL ANIMATIONS =====
  initScrollAnimations() {
    if (utils.isReducedMotion()) return;

    const observerOptions = {
      threshold: 0.15,
      rootMargin: '0px 0px -40px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated');

          // Stagger effect para containers
          if (entry.target.classList.contains('stagger-container')) {
            const children = entry.target.querySelectorAll('[data-stagger]');
            children.forEach((child, index) => {
              const delay = (child.dataset.stagger || index) * 100;
              setTimeout(() => {
                child.classList.add('animated');
              }, delay);
            });
          }
        }
      });
    }, observerOptions);

    const animElements = utils.$$('[data-animate]');
    animElements.forEach(el => observer.observe(el));
  },

  // ===== HERO PARTICLES (Canvas) =====
  initHeroParticles() {
    const canvas = utils.$('#hero-particles');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width, height;
    let particles = [];
    let animationId = null;
    let isVisible = true;

    // Page Visibility API para performance
    document.addEventListener('visibilitychange', () => {
      isVisible = !document.hidden;
    });

    class Particle {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.size = Math.random() * 2 + 1;
        this.speedX = (Math.random() - 0.5) * 0.3;
        this.speedY = (Math.random() - 0.5) * 0.3;
        this.opacity = Math.random() * 0.25 + 0.15;
      }

      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x < 0 || this.x > width || this.y < 0 || this.y > height) {
          this.reset();
        }
      }

      draw() {
        ctx.fillStyle = `rgba(0, 255, 128, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    const resize = () => {
      width = canvas.width = canvas.parentElement.offsetWidth;
      height = canvas.height = canvas.parentElement.offsetHeight;
    };

    const init = () => {
      resize();
      particles = Array.from({ length: 30 }, () => new Particle());
    };

    const animate = () => {
      if (isVisible) {
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => {
          p.update();
          p.draw();
        });
      }
      animationId = requestAnimationFrame(animate);
    };

    window.addEventListener('resize', utils.debounce(resize, 200));
    init();
    animate();
  },

  // ===== COUNTER ANIMADO COM EASING =====
  animateCounter(el, end, duration = 1800) {
    if (!el || utils.isReducedMotion()) {
      el.textContent = utils.formatCurrency(end);
      return;
    }

    const start = 0;
    const startTime = performance.now();

    // easeOutCubic
    const easeOutCubic = (t) => {
      return 1 - Math.pow(1 - t, 3);
    };

    const step = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(progress);
      const current = Math.floor(eased * (end - start) + start);

      el.textContent = utils.formatCurrency(current);

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };

    requestAnimationFrame(step);
  },

  // ===== COUNTER COM INTERSECTION OBSERVER =====
  initCounters() {
    const counters = utils.$$('[data-counter]');
    if (counters.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.dataset.animated) {
          const el = entry.target;
          const end = parseFloat(el.dataset.counter);
          const suffix = el.dataset.suffix || '';
          const duration = parseInt(el.dataset.duration) || 1800;

          el.dataset.animated = 'true';

          // Se tem suffix, formata diferente
          if (suffix === '%') {
            animations.animateCounterSimple(el, end, duration, '%');
          } else if (suffix === '+') {
            animations.animateCounterSimple(el, end, duration, '+');
          } else {
            animations.animateCounter(el, end, duration);
          }

          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(c => observer.observe(c));
  },

  animateCounterSimple(el, end, duration, suffix) {
    const start = 0;
    const startTime = performance.now();

    const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

    const step = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutCubic(progress);
      const current = Math.floor(eased * (end - start) + start);

      el.textContent = current + suffix;

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    };

    requestAnimationFrame(step);
  },

  // ===== NÚMERO HERO ANIMADO =====
  initHeroNumber() {
    const heroNumber = utils.$('[data-hero-number]');
    if (!heroNumber) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.dataset.animated) {
          entry.target.dataset.animated = 'true';
          const value = parseFloat(entry.target.dataset.heroNumber);

          setTimeout(() => {
            animations.animateCounter(entry.target, value, 2500);
          }, 300);

          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    observer.observe(heroNumber);
  }
};

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', () => {
  animations.initScrollAnimations();
  animations.initHeroParticles();
  animations.initCounters();
  animations.initHeroNumber();
});
