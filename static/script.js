// Navbar scroll effect
const nav = document.querySelector('nav');
window.addEventListener('scroll', () => {
  nav?.classList.toggle('scrolled', window.scrollY > 60);
});

// Flash messages auto-dismiss
document.querySelectorAll('.flash').forEach(f => {
  setTimeout(() => { f.style.opacity='0'; setTimeout(()=>f.remove(),400); }, 4500);
  f.onclick = () => f.remove();
  f.style.transition = 'opacity 0.4s';
});

// Fade-in on scroll
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1 });
document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

// Counter animation
function animateCounter(el) {
  const target = parseInt(el.dataset.target);
  let curr = 0;
  const step = Math.ceil(target / 60);
  const timer = setInterval(() => {
    curr = Math.min(curr + step, target);
    el.textContent = curr.toLocaleString() + (el.dataset.suffix || '');
    if(curr >= target) clearInterval(timer);
  }, 25);
}
document.querySelectorAll('[data-target]').forEach(el => {
  new IntersectionObserver(([e]) => { if(e.isIntersecting) animateCounter(el); }, { threshold: 0.5 }).observe(el);
});

// Modal helpers
window.openModal = (id) => {
  const m = document.getElementById(id);
  if(m) m.classList.add('active');
};
window.closeModal = (id) => {
  const m = document.getElementById(id);
  if(m) m.classList.remove('active');
};
document.querySelectorAll('.modal-overlay').forEach(m => {
  m.addEventListener('click', e => { if(e.target === m) m.classList.remove('active'); });
});

// Booking summary live update
const pkgSelect = document.getElementById('package_id');
const dateInput = document.getElementById('travel_date');
if(pkgSelect) {
  pkgSelect.addEventListener('change', updateSummary);
  dateInput?.addEventListener('change', updateSummary);
  updateSummary();
}
function updateSummary() {
  const opt = pkgSelect?.options[pkgSelect.selectedIndex];
  const price = parseFloat(opt?.dataset.price || 0);
  const title = opt?.dataset.title || '—';
  const date = dateInput?.value || '—';
  document.getElementById('sum-pkg') && (document.getElementById('sum-pkg').textContent = title);
  document.getElementById('sum-date') && (document.getElementById('sum-date').textContent = date);
  document.getElementById('sum-price') && (document.getElementById('sum-price').textContent = price ? '$'+price.toFixed(2) : '—');
}

// Admin: Add package via AJAX
const addPkgForm = document.getElementById('add-pkg-form');
if(addPkgForm) {
  addPkgForm.addEventListener('submit', async e => {
    e.preventDefault();
    const fd = new FormData(addPkgForm);
    const payload = Object.fromEntries(fd);
    payload.price = parseFloat(payload.price);
    const res = await fetch('/admin/package', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    });
    if(res.ok) { closeModal('add-pkg-modal'); location.reload(); }
    else { alert('Error adding package'); }
  });
}

// Admin: Delete (AJAX)
document.querySelectorAll('[data-delete]').forEach(btn => {
  btn.addEventListener('click', async () => {
    if(!confirm('Are you sure you want to delete this?')) return;
    const url = btn.dataset.delete;
    const res = await fetch(url, { method:'DELETE' });
    if(res.ok) btn.closest('tr').remove();
    else alert('Error deleting item');
  });
});
