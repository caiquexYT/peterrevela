/**
 * COMPONENTS.JS - Método Fábrica Viral v2.0 Premium — REFINADO
 * Descrição: Componentes reutilizáveis, FAQ animado, depoimentos e módulos
 * Versão: 2.1
 */

const components = {
  // ===== FAQ ACCORDION COM ANIMAÇÃO SUAVE =====
  initFAQ() {
    const faqItems = utils.$$('.faq-item');
    if (faqItems.length === 0) return;

    faqItems.forEach(item => {
      const question = item.querySelector('.faq-question');
      const answer = item.querySelector('.faq-answer');
      const icon = item.querySelector('.faq-icon');

      utils.on(question, 'click', () => {
        const isOpen = item.classList.contains('open');

        // Fecha todos os outros
        faqItems.forEach(i => {
          if (i !== item && i.classList.contains('open')) {
            const ans = i.querySelector('.faq-answer');
            ans.style.maxHeight = ans.scrollHeight + 'px';
            requestAnimationFrame(() => {
              ans.style.transition = 'max-height 0.35s ease, opacity 0.25s ease';
              ans.style.maxHeight = '0';
              ans.style.opacity = '0';
            });
            i.classList.remove('open');
            const ic = i.querySelector('.faq-icon');
            if (ic) ic.style.transform = 'rotate(0deg)';
          }
        });

        // Toggle atual
        if (!isOpen) {
          item.classList.add('open');
          answer.style.maxHeight = '0';
          answer.style.opacity = '0';
          answer.style.overflow = 'hidden';
          requestAnimationFrame(() => {
            answer.style.transition = 'max-height 0.4s ease, opacity 0.3s ease';
            answer.style.maxHeight = answer.scrollHeight + 'px';
            answer.style.opacity = '1';
          });
          if (icon) icon.style.transform = 'rotate(45deg)';
        } else {
          item.classList.remove('open');
          answer.style.maxHeight = answer.scrollHeight + 'px';
          requestAnimationFrame(() => {
            answer.style.transition = 'max-height 0.35s ease, opacity 0.25s ease';
            answer.style.maxHeight = '0';
            answer.style.opacity = '0';
          });
          if (icon) icon.style.transform = 'rotate(0deg)';
        }
      });
    });
  },

  // ===== RENDER DEPOIMENTOS (MASONRY) =====
  renderTestimonials() {
    const container = utils.$('#testimonials-grid');
    if (!container) return;

    const testimonials = [
      {
        name: 'Carlos Silva',
        city: 'São Paulo, SP',
        stars: 5,
        text: 'Comecei sem saber nada de YouTube. Em 18 dias já tinha meu primeiro vídeo monetizado. Hoje são R$2.800/mês constantes.'
      },
      {
        name: 'Fernanda Martins',
        city: 'Belo Horizonte, MG',
        stars: 5,
        text: 'Trabalho das 8h às 18h. Fiz o curso no fim de semana e em 3 semanas já tinha renda extra. Simples demais de aplicar.'
      },
      {
        name: 'Rafael Torres',
        city: 'Porto Alegre, RS',
        stars: 5,
        text: 'Tinha medo de aparecer na câmera. O método resolve isso 100%. Meu canal já tem 12k inscritos e nunca mostrei meu rosto.'
      },
      {
        name: 'Aline Costa',
        city: 'Curitiba, PR',
        stars: 5,
        text: 'A IA faz 90% do trabalho pesado. O que eu levava dias pra editar, agora faço em minutos. Melhor investimento do ano.'
      },
      {
        name: 'Marcos Oliveira',
        city: 'Fortaleza, CE',
        stars: 5,
        text: 'O suporte é excelente e o método direto ao ponto. Sem enrolação. Já recuperei o valor do curso na primeira semana.'
      },
      {
        name: 'Juliana Rocha',
        city: 'Recife, PE',
        stars: 5,
        text: 'Finalmente um método que funciona para quem é iniciante. Não precisa ser expert em tecnologia, a IA facilita tudo.'
      }
    ];

    testimonials.forEach((t, index) => {
      const initials = utils.getInitials(t.name);
      const bgColor = utils.generateColorFromString(t.name);

      const card = document.createElement('div');
      card.className = 'testimonial-card card';
      card.setAttribute('data-animate', 'fade-up');
      card.setAttribute('data-stagger', index);

      card.innerHTML = `
        <div class="testimonial-header">
          <div class="testimonial-avatar" style="background-color: ${bgColor}; color: #050709;">
            ${initials}
          </div>
          <div class="testimonial-info">
            <h4 class="testimonial-name">${t.name}</h4>
            <span class="testimonial-city">${t.city}</span>
          </div>
        </div>
        <div class="testimonial-stars">${'★'.repeat(t.stars)}</div>
        <p class="testimonial-text">${t.text}</p>
      `;

      container.appendChild(card);
    });
  },

  // ===== RENDER MÓDULOS =====
  renderModules() {
    const container = utils.$('#modules-list');
    if (!container) return;

    const modules = [
      { title: 'Módulo 1: Como criar personagens com IA', price: 197 },
      { title: 'Módulo 2: Script viral em 10 minutos', price: 147 },
      { title: 'Módulo 3: Monetização e primeiras vendas', price: 247 },
      { title: 'Módulo 4: SEO para YouTube com IA', price: 197 },
      { title: 'Bônus 1: 30 templates prontos para copiar', price: 97 },
      { title: 'Bônus 2: Comunidade privada de alunos', price: 197 },
      { title: 'Bônus 3: Suporte por 90 dias', price: 147 }
    ];

    const total = modules.reduce((sum, m) => sum + m.price, 0);

    modules.forEach((m, index) => {
      const item = document.createElement('div');
      item.className = 'offer-module-row';
      item.setAttribute('data-animate', 'fade-in');
      item.setAttribute('data-stagger', index);

      item.innerHTML = `
        <div class="offer-module-left">
          <span class="offer-module-check">✓</span>
          <span class="offer-module-title">${m.title}</span>
        </div>
        <span class="offer-module-price">R$${m.price}</span>
      `;

      container.appendChild(item);
    });

    // Adiciona linha total
    const totalRow = document.createElement('div');
    totalRow.className = 'offer-total-row';
    totalRow.innerHTML = `
      <span>Valor total</span>
      <span class="offer-total-value"><s>R$${total}</s></span>
    `;
    container.appendChild(totalRow);
  },

  // ===== RENDER METRICS BAR =====
  renderMetricsBar() {
    const container = utils.$('#metrics-bar');
    if (!container) return;

    const metrics = [
      { value: 500, label: 'Alunos', suffix: '+', format: 'simple' },
      { value: 15000, label: 'Renda média/mês', suffix: '', format: 'currency' },
      { value: 97, label: 'Taxa de aprovação', suffix: '%', format: 'simple' },
      { value: 15, label: 'Dias pro 1º resultado', suffix: '', format: 'simple' }
    ];

    metrics.forEach(m => {
      const item = document.createElement('div');
      item.className = 'metric-item';

      let valueDisplay = '';
      if (m.format === 'currency') {
        valueDisplay = utils.formatCurrency(m.value);
      } else {
        valueDisplay = m.value + m.suffix;
      }

      item.innerHTML = `
        <div class="metric-value" data-counter="${m.value}" data-suffix="${m.suffix}">
          ${valueDisplay}
        </div>
        <div class="metric-label">${m.label}</div>
      `;

      container.appendChild(item);
    });

    // Inicia contadores
    animations.initCounters();
  }
};

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', () => {
  components.initFAQ();
  components.renderTestimonials();
  components.renderModules();
  components.renderMetricsBar();
});
