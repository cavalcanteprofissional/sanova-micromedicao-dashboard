document.addEventListener('DOMContentLoaded', () => {

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Hamburger Menu ---- */
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open');
      navToggle.classList.toggle('active');
      navToggle.setAttribute('aria-expanded', open);
    });

    navLinks.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---- Scroll Reveal ---- */
  const revealElements = document.querySelectorAll('.reveal');

  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -50px 0px' }
  );

  revealElements.forEach((el) => revealObserver.observe(el));

  /* ---- Counter Animation ---- */
  function animateCounter(el) {
    const target = parseInt(el.dataset.count, 10);
    if (isNaN(target)) return;

    if (prefersReducedMotion) {
      el.textContent = target.toLocaleString('pt-BR');
      return;
    }

    const duration = 2000;
    const start = performance.now();

    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(eased * target);

      if (target >= 1000000) {
        el.textContent = (current / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
      } else if (target >= 1000) {
        el.textContent = current.toLocaleString('pt-BR');
      } else {
        el.textContent = current;
      }

      if (progress < 1) requestAnimationFrame(update);
      else el.textContent = target.toLocaleString('pt-BR');
    }

    requestAnimationFrame(update);
  }

  const counterObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );

  document.querySelectorAll('.hero-stat-value[data-count]').forEach((el) => {
    counterObserver.observe(el);
  });

  /* ---- Charts ---- */
  const chartColors = {
    primary: '#2980B9',
    warning: '#F39C12',
    danger: '#E74C3C',
    success: '#27AE60',
    cardBg: '#1a1f2e',
    text: '#94a3b8',
    border: '#1e293b',
    title: '#f1f3f5',
  };

  const categoryData = {
    labels: ['Residencial', 'Comercial', 'Industrial', 'Pública'],
    values: [1664, 143, 83, 5],
    colors: [chartColors.primary, chartColors.warning, chartColors.danger, chartColors.success],
  };

  const categoryCtx = document.getElementById('categoryChart');
  if (categoryCtx) {
    new Chart(categoryCtx, {
      type: 'doughnut',
      data: {
        labels: categoryData.labels,
        datasets: [{
          data: categoryData.values,
          backgroundColor: categoryData.colors,
          borderColor: chartColors.cardBg,
          borderWidth: 3,
          hoverOffset: 8,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: chartColors.cardBg,
            titleColor: chartColors.title,
            bodyColor: chartColors.text,
            borderColor: chartColors.border,
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((ctx.parsed / total) * 100).toFixed(1);
                return ` ${ctx.parsed} (${pct}%)`;
              },
            },
          },
        },
        cutout: '65%',
      },
    });
  }

  /* Volume chart */
  const volumeCtx = document.getElementById('volumeChart');
  if (volumeCtx) {
    const monthlyVolumes = [785000, 802000, 798000, 815000, 790000, 810000, 825000, 808000, 795000, 820000, 805000, 830000, 812000];
    const labels = ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5', 'Mês 6', 'Mês 7', 'Mês 8', 'Mês 9', 'Mês 10', 'Mês 11', 'Mês 12', 'Atual'];

    new Chart(volumeCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Volume (m³)',
          data: monthlyVolumes,
          borderColor: chartColors.primary,
          backgroundColor: 'rgba(41, 128, 185, 0.08)',
          fill: true,
          tension: 0.3,
          pointBackgroundColor: chartColors.primary,
          pointBorderColor: chartColors.cardBg,
          pointBorderWidth: 2,
          pointRadius: 3,
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: chartColors.cardBg,
            titleColor: chartColors.title,
            bodyColor: chartColors.text,
            borderColor: chartColors.border,
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => `${(ctx.parsed.y / 1000).toFixed(0)} mil m³`,
            },
          },
        },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.5)', drawBorder: false },
            ticks: { color: '#64748b', font: { size: 11 } },
          },
          y: {
            grid: { color: 'rgba(30, 41, 59, 0.5)', drawBorder: false },
            ticks: {
              color: '#64748b',
              font: { size: 11 },
              callback: (v) => `${(v / 1000).toFixed(0)}k`,
            },
          },
        },
      },
    });
  }

  /* Billing chart */
  const billingCtx = document.getElementById('billingChart');
  if (billingCtx) {
    const monthlyBilling = [92500, 94800, 93500, 96200, 93800, 95500, 97100, 95200, 94100, 96800, 95000, 97800, 96100];
    const labels = ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5', 'Mês 6', 'Mês 7', 'Mês 8', 'Mês 9', 'Mês 10', 'Mês 11', 'Mês 12', 'Atual'];

    new Chart(billingCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Faturamento (R$)',
          data: monthlyBilling,
          backgroundColor: 'rgba(39, 174, 96, 0.6)',
          borderColor: chartColors.success,
          borderWidth: 1,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: chartColors.cardBg,
            titleColor: chartColors.title,
            bodyColor: chartColors.text,
            borderColor: chartColors.border,
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => `R$ ${ctx.parsed.y.toLocaleString('pt-BR')}`,
            },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#64748b', font: { size: 11 } },
          },
          y: {
            grid: { color: 'rgba(30, 41, 59, 0.5)', drawBorder: false },
            ticks: {
              color: '#64748b',
              font: { size: 11 },
              callback: (v) => `R$${(v / 1000).toFixed(0)}k`,
            },
          },
        },
      },
    });
  }

  /* ---- Navbar scroll effect (debounced) ---- */
  const navbar = document.getElementById('navbar');
  let ticking = false;

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        navbar.classList.toggle('navbar-scrolled', window.scrollY > 100);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

});
