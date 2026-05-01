/**
 * MAIN.JS - Método Fábrica Viral v2.0 Premium — REFINADO
 * Descrição: Orquestração principal, VSL player, timer, sticky CTA e social proof
 * Versão: 2.1
 */

const main = {
  // ===== VSL PLAYER CUSTOMIZADO =====
  initVSLPlayer() {
    const video = utils.$('#vsl-video');
    const overlay = utils.$('#vsl-overlay');
    const playBtn = utils.$('#vsl-play-btn');
    const toggle = utils.$('#vsl-toggle');
    const icon = utils.$('#vsl-toggle-icon');
    const fill = utils.$('#vsl-progress-fill');
    const timeTxt = utils.$('#vsl-time-display');
    const muteBtn = utils.$('#vsl-mute');
    const fsBtn = utils.$('#vsl-fs');
    const progBg = utils.$('.vsl-progress-bg');
    const ctrlBar = utils.$('#vsl-progress-wrap');

    if (!video) return;

    function formatTime(s) {
      const m = Math.floor(s / 60);
      const sec = Math.floor(s % 60).toString().padStart(2, '0');
      return `${m}:${sec}`;
    }

    function play() {
      video.play();
      overlay.classList.add('hidden');
      ctrlBar.classList.add('always-visible');
      icon.textContent = '⏸';
    }

    // Play ao clicar no overlay
    utils.on(overlay, 'click', play);
    utils.on(playBtn, 'click', (e) => {
      e.stopPropagation();
      play();
    });

    // Toggle play/pause
    utils.on(toggle, 'click', () => {
      if (video.paused) {
        video.play();
        icon.textContent = '⏸';
      } else {
        video.pause();
        icon.textContent = '▶';
      }
    });

    // Progress
    utils.on(video, 'timeupdate', () => {
      if (!video.duration) return;
      const pct = (video.currentTime / video.duration) * 100;
      fill.style.width = pct + '%';
      timeTxt.textContent = `${formatTime(video.currentTime)} / ${formatTime(video.duration)}`;
    });

    // Seek ao clicar na barra
    utils.on(progBg, 'click', (e) => {
      const rect = progBg.getBoundingClientRect();
      const pct = (e.clientX - rect.left) / rect.width;
      video.currentTime = pct * video.duration;
    });

    // Mute
    utils.on(muteBtn, 'click', () => {
      video.muted = !video.muted;
      muteBtn.textContent = video.muted ? '🔇' : '🔊';
    });

    // Fullscreen
    utils.on(fsBtn, 'click', () => {
      const player = utils.$('#vsl-player');
      if (!document.fullscreenElement) {
        player.requestFullscreen?.() || player.webkitRequestFullscreen?.();
      } else {
        document.exitFullscreen?.() || document.webkitExitFullscreen?.();
      }
    });

    // Pausa quando sai do viewport
    const obs = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting && !video.paused) {
        video.pause();
        icon.textContent = '▶';
      }
    }, { threshold: 0.3 });
    obs.observe(video);

    // Ao terminar: mostrar overlay com CTA
    utils.on(video, 'ended', () => {
      overlay.classList.remove('hidden');
      overlay.innerHTML = `
        <div style="text-align:center;padding:20px">
          <p style="color:#fff;font-size:1.1rem;margin-bottom:20px;font-weight:600">
            Gostou? Agora é só garantir sua vaga →
          </p>
          <a href="https://pay.cakto.com.br/3bafz2u?affiliate=95dz9FKL"
             target="_blank" rel="noopener noreferrer"
             style="display:inline-block;background:#00ff80;color:#050709;font-weight:800;padding:16px 36px;border-radius:10px;text-decoration:none;font-size:1rem">
            QUERO O MÉTODO AGORA →
          </a>
        </div>`;
    });
  },

  // ===== TIMER REGRESSIVO PERSISTENTE =====
  initTimer() {
    const timerDisplay = utils.$('#timer-display');
    if (!timerDisplay) return;

    let deadline = utils.storage.get('fv_timer_deadline');
    if (!deadline) {
      deadline = Date.now() + 24 * 60 * 60 * 1000;
      utils.storage.set('fv_timer_deadline', deadline);
    }

    const update = () => {
      const now = Date.now();
      const diff = Math.max(0, (deadline - now) / 1000);

      if (diff <= 0) {
        timerDisplay.innerHTML = `
          <div class="timer-unit">
            <div class="timer-number" style="background: rgba(255,0,0,0.1); border-color: rgba(255,0,0,0.3);">
              <span style="color: #ff4d4d;">EXPIRADO</span>
            </div>
          </div>
        `;
        return;
      }

      const time = utils.formatTime(diff);
      timerDisplay.innerHTML = `
        <div class="timer-unit">
          <div class="timer-number">${time.hours}</div>
          <div class="timer-label">horas</div>
        </div>
        <div class="timer-colon">:</div>
        <div class="timer-unit">
          <div class="timer-number">${time.minutes}</div>
          <div class="timer-label">minutos</div>
        </div>
        <div class="timer-colon">:</div>
        <div class="timer-unit">
          <div class="timer-number">${time.seconds}</div>
          <div class="timer-label">segundos</div>
        </div>
      `;
    };

    update();
    setInterval(update, 1000);
  },

  // ===== STICKY CTA =====
  initStickyCTA() {
    const cta = utils.$('#sticky-cta');
    const closeBtn = utils.$('#sticky-close');
    if (!cta) return;

    const handleScroll = utils.throttle(() => {
      const isClosed = utils.storage.getSession('sticky_cta_closed');
      if (window.scrollY > 600 && !isClosed) {
        cta.classList.add('visible');
      } else {
        cta.classList.remove('visible');
      }
    }, 100);

    window.addEventListener('scroll', handleScroll);

    if (closeBtn) {
      utils.on(closeBtn, 'click', () => {
        cta.classList.remove('visible');
        utils.storage.setSession('sticky_cta_closed', true);
      });
    }
  },

  // ===== SCROLL PROGRESS BAR =====
  initScrollProgress() {
    const bar = utils.$('#scroll-progress');
    if (!bar) return;

    window.addEventListener('scroll', utils.throttle(() => {
      bar.style.width = utils.getScrollPercent() + '%';
    }, 50));
  },

  // ===== SOCIAL PROOF TOASTS =====
  initSocialProofToasts() {
    const socialProofData = [
      { name: 'João S.', city: 'São Paulo, SP', time: 'agora mesmo' },
      { name: 'Camila R.', city: 'Rio de Janeiro, RJ', time: 'há 2 minutos' },
      { name: 'Pedro M.', city: 'Curitiba, PR', time: 'há 3 minutos' },
      { name: 'Ana L.', city: 'Belo Horizonte, MG', time: 'há 5 minutos' },
      { name: 'Lucas F.', city: 'Fortaleza, CE', time: 'há 7 minutos' },
      { name: 'Mariana C.', city: 'Porto Alegre, RS', time: 'há 9 minutos' },
      { name: 'Gabriel T.', city: 'Recife, PE', time: 'há 11 minutos' },
      { name: 'Beatriz O.', city: 'Salvador, BA', time: 'há 14 minutos' },
      { name: 'Felipe N.', city: 'Manaus, AM', time: 'há 16 minutos' },
      { name: 'Julia A.', city: 'Brasília, DF', time: 'há 18 minutos' },
      { name: 'Rafael B.', city: 'Goiânia, GO', time: 'há 20 minutos' },
      { name: 'Larissa M.', city: 'Campinas, SP', time: 'há 23 minutos' },
      { name: 'Diego K.', city: 'Florianópolis, SC', time: 'há 25 minutos' },
      { name: 'Priscila V.', city: 'Natal, RN', time: 'há 28 minutos' },
      { name: 'Rodrigo S.', city: 'João Pessoa, PB', time: 'há 30 minutos' }
    ];

    const showToast = () => {
      const item = socialProofData[Math.floor(Math.random() * socialProofData.length)];
      const usedNames = utils.storage.getSession('shown_toasts') || [];

      // Evita repetir nomes na mesma sessão
      if (usedNames.includes(item.name)) {
        setTimeout(showToast, 5000);
        return;
      }

      usedNames.push(item.name);
      utils.storage.setSession('shown_toasts', usedNames);

      const initials = utils.getInitials(item.name);
      const bgColor = utils.generateColorFromString(item.name);

      const toast = document.createElement('div');
      toast.className = 'social-toast';
      toast.innerHTML = `
        <div class="social-toast__avatar" style="background-color: ${bgColor};">
          ${initials}
        </div>
        <div class="social-toast__text">
          <strong>${item.name}</strong>
          <span>${item.city} — ${item.time}</span>
        </div>
      `;

      document.body.appendChild(toast);
      setTimeout(() => toast.classList.add('visible'), 100);

      setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 400);
      }, 5000);

      const nextInterval = Math.random() * 40 + 50;
      setTimeout(showToast, nextInterval * 1000);
    };

    setTimeout(showToast, 10000);
  },

  // ===== SMOOTH SCROLL =====
  initSmoothScroll() {
    utils.delegate(document.body, 'click', 'a[href^="#"]', (e, el) => {
      const href = el.getAttribute('href');
      if (href === '#') return;
      e.preventDefault();
      utils.scrollTo(href);
    });
  },

  // ===== TRACK CTA CLICKS =====
  initCTATracking() {
    utils.delegate(document.body, 'click', '[data-cta]', (e, el) => {
      const ctaName = el.dataset.cta;
      utils.trackCTAClick(ctaName);
    });
  }
};

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', () => {
  main.initVSLPlayer();
  main.initTimer();
  main.initStickyCTA();
  main.initScrollProgress();
  main.initSocialProofToasts();
  main.initSmoothScroll();
  main.initCTATracking();
});
