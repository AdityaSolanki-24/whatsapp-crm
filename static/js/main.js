/* WhatsApp CRM — Global JS */

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar Toggle (mobile) ──────────────────────────────
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebarToggle');
  const overlay = document.getElementById('sidebarOverlay');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      if (overlay) overlay.classList.toggle('show');
    });
  }

  if (overlay) {
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('show');
      overlay.classList.remove('show');
    });
  }

  // ── Auto-dismiss flash alerts ────────────────────────────
  document.querySelectorAll('.alert.fade.show').forEach(function (alert) {
    setTimeout(function () {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 6000);
  });

  // ── Confirm delete forms ─────────────────────────────────
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm(form.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // ── Activate tooltip everywhere ──────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  // ── Animate stat cards on load ───────────────────────────
  document.querySelectorAll('.stat-card').forEach(function (card, i) {
    card.style.opacity = '0';
    card.style.transform = 'translateY(12px)';
    setTimeout(function () {
      card.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, i * 60);
  });

});
