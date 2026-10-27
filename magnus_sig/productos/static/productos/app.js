(() => {
  'use strict';

  // Los filtros de la lista se aplican al cambiar de opción.
  document.querySelectorAll('select[data-autosubmit]').forEach((select) => {
    select.addEventListener('change', () => {
      // HTMX ya envía la petición en el evento change definido en el formulario.
      if (window.htmx && select.form?.hasAttribute('hx-get')) return;
      if (typeof select.form.requestSubmit === 'function') select.form.requestSubmit();
      else select.form.submit();
    });
  });

  // Confirmación antes de eliminar una categoría.
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  // Control del Menú Hamburguesa para Móvil
  const menuToggle = document.getElementById('mobile-menu-toggle');
  const sidebar = document.getElementById('app-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  const closeBtn = document.getElementById('sidebar-close-btn');

  function openMobileMenu() {
    if (!sidebar) return;
    sidebar.classList.add('is-open');
    if (backdrop) backdrop.classList.add('is-active');
    if (menuToggle) {
      menuToggle.setAttribute('aria-expanded', 'true');
      menuToggle.classList.add('is-active');
    }
    document.body.classList.add('menu-open');
  }

  function closeMobileMenu() {
    if (!sidebar) return;
    sidebar.classList.remove('is-open');
    if (backdrop) backdrop.classList.remove('is-active');
    if (menuToggle) {
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.classList.remove('is-active');
    }
    document.body.classList.remove('menu-open');
  }

  if (menuToggle) {
    menuToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      if (sidebar && sidebar.classList.contains('is-open')) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', (event) => {
      event.stopPropagation();
      closeMobileMenu();
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', () => {
      closeMobileMenu();
    });
  }

  // Cerrar al pulsar Escape
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && sidebar && sidebar.classList.contains('is-open')) {
      closeMobileMenu();
    }
  });

  // Cerrar al hacer clic en un enlace de navegación en móvil
  if (sidebar) {
    sidebar.querySelectorAll('.nav-item').forEach((item) => {
      item.addEventListener('click', () => {
        if (window.innerWidth <= 820) {
          closeMobileMenu();
        }
      });
    });
  }

  // Al redimensionar la ventana a tamaño de escritorio, resetear estado
  window.addEventListener('resize', () => {
    if (window.innerWidth > 820 && sidebar && sidebar.classList.contains('is-open')) {
      closeMobileMenu();
    }
  });

})();
