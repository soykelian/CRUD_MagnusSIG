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

})();
