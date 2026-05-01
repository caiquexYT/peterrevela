/**
 * UTILS.JS - Método Fábrica Viral v2.0 Premium — REFINADO
 * Descrição: Utilitários robustos, helpers de DOM, storage e performance
 * Versão: 2.1
 */

const utils = {
  // ===== DOM HELPERS =====
  $(selector) {
    return document.querySelector(selector);
  },

  $$(selector) {
    return document.querySelectorAll(selector);
  },

  on(el, event, handler) {
    if (el) el.addEventListener(event, handler);
  },

  off(el, event, handler) {
    if (el) el.removeEventListener(event, handler);
  },

  delegate(parent, event, selector, handler) {
    utils.on(parent, event, (e) => {
      const target = e.target.closest(selector);
      if (target && parent.contains(target)) {
        handler.call(target, e, target);
      }
    });
  },

  addClass(el, ...classes) {
    if (el) el.classList.add(...classes);
  },

  removeClass(el, ...classes) {
    if (el) el.classList.remove(...classes);
  },

  toggleClass(el, cls) {
    if (el) el.classList.toggle(cls);
  },

  hasClass(el, cls) {
    return el ? el.classList.contains(cls) : false;
  },

  // ===== STORAGE =====
  storage: {
    set(key, val) {
      try {
        localStorage.setItem(key, JSON.stringify(val));
      } catch (e) {
        // silently fail
      }
    },
    get(key) {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
      } catch (e) {
        return null;
      }
    },
    remove(key) {
      try {
        localStorage.removeItem(key);
      } catch (e) {
        // silently fail
      }
    },
    setSession(key, val) {
      try {
        sessionStorage.setItem(key, JSON.stringify(val));
      } catch (e) {
        // silently fail
      }
    },
    getSession(key) {
      try {
        const item = sessionStorage.getItem(key);
        return item ? JSON.parse(item) : null;
      } catch (e) {
        return null;
      }
    }
  },

  // ===== FORMATAÇÃO =====
  formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  },

  formatNumber(value) {
    if (value >= 1000) {
      return (value / 1000).toFixed(0) + 'k';
    }
    return value.toString();
  },

  formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return {
      hours: h.toString().padStart(2, '0'),
      minutes: m.toString().padStart(2, '0'),
      seconds: s.toString().padStart(2, '0')
    };
  },

  formatTimeDisplay(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  },

  // ===== PERFORMANCE =====
  debounce(fn, delay) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), delay);
    };
  },

  throttle(fn, limit) {
    let inThrottle;
    return function (...args) {
      if (!inThrottle) {
        fn.apply(this, args);
        inThrottle = true;
        setTimeout(() => {
          inThrottle = false;
        }, limit);
      }
    };
  },

  lazyLoadImages() {
    if (!('IntersectionObserver' in window)) {
      const imgs = utils.$$('img[data-src]');
      imgs.forEach(img => {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
      });
      return;
    }

    const imgs = utils.$$('img[data-src]');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          observer.unobserve(img);
        }
      });
    }, { rootMargin: '200px' });

    imgs.forEach(img => observer.observe(img));
  },

  // ===== SCROLL HELPERS =====
  getScrollPercent() {
    const h = document.documentElement;
    const b = document.body;
    const st = 'scrollTop';
    const sh = 'scrollHeight';
    return ((h[st] || b[st]) / ((h[sh] || b[sh]) - h.clientHeight)) * 100;
  },

  scrollTo(selector, offset = 80) {
    const el = utils.$(selector);
    if (el) {
      const y = el.getBoundingClientRect().top + window.pageYOffset - offset;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  },

  isInViewport(el, threshold = 0.2) {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    const viewHeight = Math.max(document.documentElement.clientHeight, window.innerHeight);
    return !(rect.bottom < viewHeight * threshold || rect.top > viewHeight * (1 - threshold));
  },

  // ===== ANALYTICS =====
  trackEvent(category, action, label) {
    if (window.gtag) {
      window.gtag('event', action, {
        event_category: category,
        event_label: label
      });
    }
  },

  trackCTAClick(ctaName) {
    utils.trackEvent('CTA', 'click', ctaName);
  },

  // ===== UTILITIES =====
  generateColorFromString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const colors = [
      '#00ff80', '#00e872', '#00cc66', '#00b359',
      '#009966', '#008059', '#006d4d', '#005a40'
    ];
    return colors[Math.abs(hash) % colors.length];
  },

  getInitials(name) {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  },

  isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  },

  isReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
};

// Auto-init lazy loading
document.addEventListener('DOMContentLoaded', () => {
  utils.lazyLoadImages();
});
