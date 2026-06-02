/* ── Notes Pro — script.js ─────────────────────────────────── */

// ── Sidebar (mobile) ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const burger  = document.getElementById('burgerBtn');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');

  function openSidebar()  { sidebar?.classList.add('open'); overlay?.classList.add('active'); }
  function closeSidebar() { sidebar?.classList.remove('open'); overlay?.classList.remove('active'); }

  burger?.addEventListener('click', openSidebar);
  overlay?.addEventListener('click', closeSidebar);

  // Close on nav-link click (mobile)
  sidebar?.querySelectorAll('.nav-link').forEach(el => el.addEventListener('click', closeSidebar));

  // ── Theme toggle button (injected) ──────────────────────
// ── Auto-dismiss flash messages ──────────────────────────
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 3500);
  });

  // ── Confirm delete buttons ───────────────────────────────
  // already handled inline in templates

  // ── Tag input autocomplete hint ──────────────────────────
  const tagInputs = document.querySelectorAll('input[name="tags"]');
  tagInputs.forEach(inp => {
    inp.addEventListener('keydown', e => {
      if (e.key === 'Enter') e.preventDefault(); // don't submit on comma-tag entry
    });
  });
});
