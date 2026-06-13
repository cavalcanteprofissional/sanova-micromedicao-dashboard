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
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -50px 0px' }
  );
  document.querySelectorAll('.reveal').forEach((el) => revealObserver.observe(el));

  /* ---- Counter Animation ---- */
  function animateCounter(el, target) {
    const prefix = el.dataset.prefix || '';
    if (prefersReducedMotion) { el.textContent = prefix + target.toLocaleString('pt-BR'); return; }
    const duration = 2000, start = performance.now();
    function update(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(eased * target);
      el.textContent = (target >= 1000 ? prefix + current.toLocaleString('pt-BR') : prefix + current);
      if (progress < 1) requestAnimationFrame(update);
      else el.textContent = prefix + target.toLocaleString('pt-BR');
    }
    requestAnimationFrame(update);
  }

  const counterObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.count, 10);
          if (!isNaN(target)) {
            animateCounter(el, target);
            counterObserver.unobserve(el);
          }
        }
      });
    },
    { threshold: 0.5 }
  );
  document.querySelectorAll('.hero-stat-value[data-count]').forEach((el) => counterObserver.observe(el));

  /* ---- Load data from JSON ---- */
  let d = null;  // data

  fetch('data.json')
    .then((r) => {
      if (!r.ok) throw new Error('Failed to load data.json');
      return r.json();
    })
    .then((data) => {
      d = data;
      renderCharts();
      markEmptyWrappers();
    })
    .catch((err) => {
      console.warn('data.json not loaded, using defaults:', err);
      renderCharts();
      markEmptyWrappers();
    });

  function renderCharts() {
    if (typeof Chart === 'undefined') { renderChartFallback(); return; }

    const C = {
      primary: '#1976D2', warning: '#FFA000', danger: '#D32F2F',
      success: '#00BFA5', info: '#00ACC1',
      cardBg: '#121D33', text: '#94a3b8', border: '#1E2A40', title: '#EEF2F6',
    };

    const cats = d ? d.categories : { residencial: 1664, comercial: 143, industrial: 83, publica: 5 };
    const catLabels = Object.keys(cats).map((k) => k.charAt(0).toUpperCase() + k.slice(1));
    const catValues = Object.values(cats);
    const catColors = [C.primary, C.warning, C.danger, C.success];

    /* ---- Category Doughnut ---- */
    const catCtx = document.getElementById('categoryChart');
    if (catCtx) {
      new Chart(catCtx, {
        type: 'doughnut',
        data: {
          labels: catLabels,
          datasets: [{ data: catValues, backgroundColor: catColors, borderColor: C.cardBg, borderWidth: 3, hoverOffset: 8 }],
        },
        options: {
          responsive: true, maintainAspectRatio: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: C.cardBg, titleColor: C.title, bodyColor: C.text,
              borderColor: C.border, borderWidth: 1, padding: 12, cornerRadius: 8,
              callbacks: {
                label: (ctx) => {
                  const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                  return ` ${ctx.parsed} (${((ctx.parsed / total) * 100).toFixed(1)}%)`;
                },
              },
            },
          },
          cutout: '65%',
        },
      });
    }

    /* ---- Age Histogram ---- */
    const ageCtx = document.getElementById('ageChart');
    if (ageCtx && d) {
      const ageData = d.age_distribution;
      const labels = Object.keys(ageData);
      const values = Object.values(ageData);
      new Chart(ageCtx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Hidrômetros',
            data: values,
            backgroundColor: values.map((v, i) => i >= 5 ? 'rgba(211, 47, 47, 0.7)' : 'rgba(25, 118, 210, 0.7)'),
            borderColor: values.map((v, i) => i >= 5 ? C.danger : C.primary),
            borderWidth: 1,
            borderRadius: 3,
          }],
        },
        options: {
          responsive: true, maintainAspectRatio: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: 'Idade dos Hidrômetros (anos)', color: C.title, font: { size: 13, weight: '600' }, padding: { bottom: 12 } },
            tooltip: {
              backgroundColor: C.cardBg, titleColor: C.title, bodyColor: C.text,
              borderColor: C.border, borderWidth: 1, padding: 12, cornerRadius: 8,
            },
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 10 } } },
            y: { grid: { color: 'rgba(30, 42, 64, 0.5)', drawBorder: false }, ticks: { color: '#64748b', font: { size: 10 } } },
          },
        },
      });
    }

    /* ---- Zero Consumption by Category ---- */
    const zeroCtx = document.getElementById('zeroByCategoryChart');
    if (zeroCtx && d) {
      const zData = d.zero_consumption_by_category;
      const zLabels = Object.keys(zData).filter((k) => k !== 'NÃO INFORMADA');
      const zeroVals = zLabels.map((k) => Math.round((zData[k].zero / zData[k].total) * 100));
      const nearZeroVals = zLabels.map((k) => Math.round((zData[k].near_zero / zData[k].total) * 100));

      new Chart(zeroCtx, {
        type: 'bar',
        data: {
          labels: zLabels,
          datasets: [
            { label: 'Consumo Zero (%)', data: zeroVals, backgroundColor: 'rgba(211, 47, 47, 0.7)', borderColor: C.danger, borderWidth: 1, borderRadius: 3 },
            { label: 'Quase Zero (%)', data: nearZeroVals, backgroundColor: 'rgba(255, 160, 0, 0.6)', borderColor: C.warning, borderWidth: 1, borderRadius: 3 },
          ],
        },
        options: {
          responsive: true, maintainAspectRatio: true,
          plugins: {
            legend: { labels: { color: C.text, font: { size: 11 }, boxWidth: 12, padding: 12 } },
            title: { display: true, text: 'Consumo Zero por Categoria (%)', color: C.title, font: { size: 13, weight: '600' }, padding: { bottom: 12 } },
            tooltip: {
              backgroundColor: C.cardBg, titleColor: C.title, bodyColor: C.text,
              borderColor: C.border, borderWidth: 1, padding: 12, cornerRadius: 8,
              callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}%` },
            },
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 10 } } },
            y: { grid: { color: 'rgba(30, 42, 64, 0.5)', drawBorder: false }, ticks: { color: '#64748b', font: { size: 10 }, maxTicksLimit: 6 } },
          },
        },
      });
    }

    /* ---- Volume Line Chart ---- */
    const volCtx = document.getElementById('volumeChart');
    if (volCtx) {
      const volData = d ? d.monthly_volume : [785000, 802000, 798000, 815000, 790000, 810000, 825000, 808000, 795000, 820000, 805000, 830000, 812000];
      const labels = d ? d.monthly_labels : ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5', 'Mês 6', 'Mês 7', 'Mês 8', 'Mês 9', 'Mês 10', 'Mês 11', 'Mês 12', 'Atual'];
      new Chart(volCtx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Volume (m³)',
            data: volData,
            borderColor: C.primary,
            backgroundColor: 'rgba(25, 118, 210, 0.08)',
            fill: true, tension: 0.3,
            pointBackgroundColor: C.primary,
            pointBorderColor: C.cardBg,
            pointBorderWidth: 2, pointRadius: 3, borderWidth: 2,
          }],
        },
        options: {
          responsive: true, maintainAspectRatio: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: 'Volume Mensal (m³)', color: C.title, font: { size: 13, weight: '600' }, padding: { bottom: 12 } },
            tooltip: {
              backgroundColor: C.cardBg, titleColor: C.title, bodyColor: C.text,
              borderColor: C.border, borderWidth: 1, padding: 12, cornerRadius: 8,
              callbacks: { label: (ctx) => `${(ctx.parsed.y / 1000).toFixed(0)} mil m³` },
            },
          },
          scales: {
            x: { grid: { color: 'rgba(30, 42, 64, 0.5)', drawBorder: false }, ticks: { color: '#64748b', font: { size: 10 } } },
            y: { grid: { color: 'rgba(30, 42, 64, 0.5)', drawBorder: false }, ticks: { color: '#64748b', font: { size: 10 }, callback: (v) => `${(v / 1000).toFixed(0)}k` } },
          },
        },
      });
    }

    /* ---- Billing Bar Chart ---- */
    const billCtx = document.getElementById('billingChart');
    if (billCtx) {
      const billData = d ? d.monthly_billing : [92500, 94800, 93500, 96200, 93800, 95500, 97100, 95200, 94100, 96800, 95000, 97800, 96100];
      const labels = d ? d.monthly_labels : ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5', 'Mês 6', 'Mês 7', 'Mês 8', 'Mês 9', 'Mês 10', 'Mês 11', 'Mês 12', 'Atual'];
      new Chart(billCtx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Faturamento (R$)',
            data: billData,
            backgroundColor: 'rgba(0, 191, 165, 0.6)',
            borderColor: C.success,
            borderWidth: 1, borderRadius: 4,
          }],
        },
        options: {
          responsive: true, maintainAspectRatio: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: 'Faturamento Mensal (R$)', color: C.title, font: { size: 13, weight: '600' }, padding: { bottom: 12 } },
            tooltip: {
              backgroundColor: C.cardBg, titleColor: C.title, bodyColor: C.text,
              borderColor: C.border, borderWidth: 1, padding: 12, cornerRadius: 8,
              callbacks: { label: (ctx) => `R$ ${ctx.parsed.y.toLocaleString('pt-BR')}` },
            },
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 10 } } },
            y: { grid: { color: 'rgba(30, 42, 64, 0.5)', drawBorder: false }, ticks: { color: '#64748b', font: { size: 10 }, callback: (v) => `R$${(v / 1000).toFixed(0)}k` } },
          },
        },
      });
    }

    /* ---- Flags Severity Chart ---- */
    const flagsCtx = document.getElementById('flagsChart');
    if (flagsCtx && d) {
      const flagMap = {
        'consumo_zero': { label: 'Consumo Zero', color: C.danger },
        'consumo_implausivel': { label: 'Consumo Implausível', color: C.danger },
        'consumo_constante': { label: 'Consumo Constante', color: C.warning },
        'ativa_sem_receita': { label: 'Ativa sem Receita', color: C.warning },
        'outlier_extremo': { label: 'Outlier Extremo', color: C.warning },
        'dados_incompletos': { label: 'Dados Incompletos', color: C.info },
        'data_invalida': { label: 'Data Inválida', color: C.info },
        'sem_categoria': { label: 'Sem Categoria', color: C.info },
        'anomalia_leitura': { label: 'Anomalia Leitura', color: C.danger },
        'valor_negativo': { label: 'Valor Negativo', color: C.info },
        'sem_hidrometro': { label: 'Sem Hidrômetro', color: C.info },
      };

      const flags = d.flags;
      const labels = [];
      const values = [];
      const colors = [];

      Object.keys(flagMap).forEach((key) => {
        if (flags[key] && flags[key] > 0) {
          labels.push(flagMap[key].label);
          values.push(flags[key]);
          colors.push(flagMap[key].color);
        }
      });

      new Chart(flagsCtx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Quantidade',
            data: values,
            backgroundColor: colors.map((c) => c + '99'),
            borderColor: colors,
            borderWidth: 1,
            borderRadius: 3,
          }],
        },
        options: {
          indexAxis: 'y',
          responsive: true, maintainAspectRatio: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: 'Anomalias por Tipo', color: C.title, font: { size: 14, weight: '600' }, padding: { bottom: 16 } },
            tooltip: {
              backgroundColor: C.cardBg, titleColor: C.title, bodyColor: C.text,
              borderColor: C.border, borderWidth: 1, padding: 12, cornerRadius: 8,
            },
          },
          scales: {
            x: { grid: { color: 'rgba(30, 42, 64, 0.5)', drawBorder: false }, ticks: { color: '#64748b', font: { size: 10 } } },
            y: { grid: { display: false }, ticks: { color: C.text, font: { size: 11 } } },
          },
        },
      });
    }

    /* ---- Recovery Potential Chart ---- */
    const recCtx = document.getElementById('recoveryChart');
    if (recCtx && d) {
      const rec = d.recovery_potential;
      const recData = [
        { label: 'Consumo Zero',  value: rec.consumo_zero || 0 },
        { label: 'Dados Incompletos', value: rec.dados_incompletos || 0 },
        { label: 'Ativas s/ Receita', value: rec.ativas_sem_receita || 0 },
        { label: 'Outliers',  value: rec.outliers || 0 },
      ];
      const recColors = [C.danger, C.info, C.warning, C.warning];

      if (typeof Plot !== 'undefined') {
        recCtx.parentNode.style.position = 'relative';
        const plotDiv = document.createElement('div');
        plotDiv.style.cssText = 'width:100%;height:260px;';
        recCtx.parentNode.insertBefore(plotDiv, recCtx);
        recCtx.style.display = 'none';
        const p = Plot.plot({
          marks: [
            Plot.barX(recData, {
              x: 'value', y: 'label',
              fill: (d, i) => recColors[i],
              sort: { y: 'x', reverse: true },
            }),
            Plot.text(recData, {
              x: 'value', y: 'label',
              text: (d) => `R$ ${d.value.toLocaleString('pt-BR')}`,
              textAnchor: 'start', dx: 4,
              fill: '#94a3b8', fontSize: 11,
            }),
          ],
          x: { axis: null, grid: true, tickFormat: '' },
          y: { label: null },
          color: { legend: false },
          marginLeft: 120,
          marginRight: 100,
          height: 220,
          style: { background: 'transparent', color: '#94a3b8', fontSize: 12, fontFamily: 'Inter, sans-serif' },
        });
        plotDiv.appendChild(p);
      } else {
        new Chart(recCtx, {
          type: 'bar',
          data: {
            labels: recData.map((d) => d.label),
            datasets: [{
              label: 'Potencial (R$)',
              data: recData.map((d) => d.value),
              backgroundColor: recColors.map((c) => c + '99'),
              borderColor: recColors,
              borderWidth: 1, borderRadius: 3,
            }],
          },
          options: {
            indexAxis: 'y',
            responsive: true, maintainAspectRatio: true,
            plugins: {
              legend: { display: false },
              title: { display: true, text: 'Potencial de Recuperação (R$)', color: C.title, font: { size: 13, weight: '600' }, padding: { bottom: 12 } },
              tooltip: { backgroundColor: C.cardBg, titleColor: C.title, bodyColor: C.text, borderColor: C.border, borderWidth: 1, padding: 12, cornerRadius: 8, callbacks: { label: (ctx) => `R$ ${ctx.parsed.y.toLocaleString('pt-BR')}` } },
            },
            scales: {
              x: { grid: { color: 'rgba(30, 42, 64, 0.5)', drawBorder: false }, ticks: { color: '#64748b', font: { size: 10 }, callback: (v) => `R$${(v).toFixed(0)}` } },
              y: { grid: { display: false }, ticks: { color: C.text, font: { size: 11 } } },
            },
          },
        });
      }
    }
  }

  /* ---- Mark empty chart wrappers ---- */
  function markEmptyWrappers() {
    const dependentIds = ['ageChart', 'zeroByCategoryChart', 'flagsChart', 'recoveryChart'];
    dependentIds.forEach((id) => {
      const canvas = document.getElementById(id);
      if (!canvas) return;
      if (canvas.style.display === 'none') return;
      const wrapper = canvas.closest('.chart-wrapper');
      if (!wrapper) return;
      if (!d || canvas.getContext('2d').getImageData(1, 1, 1, 1).data[3] === 0) {
        wrapper.classList.add('empty');
      }
    });
  }

  /* ---- Chart.js Fallback (HTML tables) ---- */
  function renderChartFallback() {
    document.querySelectorAll('.chart-preview').forEach((container) => {
      const fallback = container.querySelector('canvas');
      if (!fallback) return;
      const table = document.createElement('div');
      table.className = 'chart-fallback';
      table.innerHTML = '<p style="color:#ffa000;font-size:0.85rem;">\u26A0\uFE0F Gr&aacute;fico n&atilde;o dispon&iacute;vel. Ative JavaScript ou use um navegador moderno.</p>';
      container.appendChild(table);
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

/* ---- Logo click: smooth scroll to hero ---- */
document.querySelector('.nav-logo-link')?.addEventListener('click', (e) => {
  e.preventDefault();
  const hero = document.getElementById('hero');
  if (hero) {
    hero.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});
