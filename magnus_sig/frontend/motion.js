import 'aos/dist/aos.css';
import 'lenis/dist/lenis.css';
import AOS from 'aos';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import htmx from 'htmx.org';

gsap.registerPlugin(ScrollTrigger);
window.htmx = htmx;
window.AOS = AOS;

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const canAnimate = !prefersReducedMotion.matches;

if (canAnimate) {
  document.body.classList.add('motion-enabled');
  AOS.init({ duration: 420, easing: 'ease-out-cubic', once: true, offset: 20, disable: false });

  const lenis = new Lenis({
    duration: 0.85,
    smoothWheel: true,
    syncTouch: false,
    prevent: (node) => Boolean(node.closest('.table-wrap, .modal, [data-lenis-prevent]')),
  });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);

  const dashboard = document.querySelector('.dashboard-showcase');
  if (dashboard) {
    gsap.fromTo(dashboard.querySelectorAll('.balance-line'),
      { strokeDasharray: (index, element) => `${element.getTotalLength()} ${element.getTotalLength()}`, strokeDashoffset: (index, element) => element.getTotalLength() },
      { strokeDashoffset: 0, duration: 0.9, stagger: 0.12, ease: 'power2.out', delay: 0.08 });
    gsap.fromTo(dashboard.querySelectorAll('.inventory-meter i'), { scaleX: 0, transformOrigin: 'left center' },
      { scaleX: 1, duration: 0.55, stagger: 0.08, ease: 'power2.out', delay: 0.12 });
    gsap.fromTo(dashboard.querySelectorAll('.month-flow-bar'), { scaleY: 0, transformOrigin: 'center bottom' },
      { scaleY: 1, duration: 0.45, stagger: 0.035, ease: 'power2.out', delay: 0.18 });
    const gauge = dashboard.querySelector('.health-gauge-value');
    if (gauge) gsap.fromTo(gauge, { attr: { 'stroke-dasharray': '0 100' } },
      { attr: { 'stroke-dasharray': gauge.getAttribute('stroke-dasharray') }, duration: 0.7, ease: 'power2.out', delay: 0.12 });

    gsap.utils.toArray('.dashboard-lower-grid > .surface-panel').forEach((panel) => {
      gsap.fromTo(panel, { y: 14, autoAlpha: 0.78 }, {
        y: 0, autoAlpha: 1, duration: 0.48, ease: 'power2.out',
        scrollTrigger: { trigger: panel, start: 'top 88%', once: true },
      });
    });
  }

  document.querySelectorAll('[data-aos]').forEach((element) => {
    element.addEventListener('aos:in', () => element.classList.add('motion-revealed'), { once: true });
  });
} else {
  document.querySelectorAll('[data-aos]').forEach((element) => element.classList.add('aos-animate'));
}

// HTMX updates totals live while the normal GET links remain a no-JS fallback.
document.body.addEventListener('htmx:afterSwap', () => {
  if (typeof AOS.refreshHard === 'function') AOS.refreshHard();
});

const chartHost = document.querySelector('[data-stock-chart]');
if (chartHost) {
  const payload = document.getElementById('stock-chart-data');
  const toggle = document.querySelector('[data-chart-toggle]');
  const status = document.querySelector('[data-chart-status]');
  const chart2d = document.querySelector('[data-chart-2d]');
  let chart3dModule;

  toggle?.addEventListener('click', async () => {
    const show3d = toggle.getAttribute('aria-pressed') !== 'true';
    if (!show3d) {
      chart3dModule?.destroyChart(chartHost);
      chartHost.hidden = true;
      chart2d.hidden = false;
      toggle.setAttribute('aria-pressed', 'false');
      toggle.textContent = 'Ver en 3D';
      status.textContent = '';
      return;
    }
    try {
      status.textContent = 'Preparando visualización…';
      chart3dModule ||= await import('./stock-chart-3d.js');
      await chart3dModule.renderChart(chartHost, JSON.parse(payload.textContent), { animate: canAnimate });
      chartHost.hidden = false;
      chart2d.hidden = true;
      toggle.setAttribute('aria-pressed', 'true');
      toggle.textContent = 'Ver gráfico sencillo';
      status.textContent = 'Visualización 3D de los valores reales por categoría.';
    } catch (error) {
      console.error('No fue posible iniciar el gráfico 3D:', error);
      status.textContent = 'No se pudo mostrar la vista 3D en este navegador. El gráfico sencillo sigue disponible.';
    }
  });
}
