/* ==========================================================================
   GitHub Profile Finder - Realtime Repository Filtering & Sorting
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const repoGrid = document.getElementById('repo-grid');
  if (!repoGrid) return;

  const repoCards = Array.from(document.querySelectorAll('.repo-item-col'));
  const searchInput = document.getElementById('repo-search-input');
  const langSelect = document.getElementById('repo-lang-filter');
  const sortSelect = document.getElementById('repo-sort-filter');
  const repoCountBadge = document.getElementById('visible-repo-count');
  const emptyState = document.getElementById('repo-empty-state');

  function filterAndSortRepos() {
    const query = (searchInput?.value || '').toLowerCase().trim();
    const selectedLang = (langSelect?.value || 'all').toLowerCase();
    const sortVal = sortSelect?.value || 'stars-desc';

    let visibleCards = repoCards.filter(col => {
      const name = col.getAttribute('data-name') || '';
      const desc = col.getAttribute('data-desc') || '';
      const lang = (col.getAttribute('data-lang') || 'n/a').toLowerCase();

      const matchesSearch = !query || name.includes(query) || desc.includes(query);
      const matchesLang = selectedLang === 'all' || lang === selectedLang;

      return matchesSearch && matchesLang;
    });

    // Sorting
    visibleCards.sort((a, b) => {
      if (sortVal === 'stars-desc') {
        return parseInt(b.getAttribute('data-stars') || '0', 10) - parseInt(a.getAttribute('data-stars') || '0', 10);
      } else if (sortVal === 'stars-asc') {
        return parseInt(a.getAttribute('data-stars') || '0', 10) - parseInt(b.getAttribute('data-stars') || '0', 10);
      } else if (sortVal === 'newest') {
        return new Date(b.getAttribute('data-updated') || 0) - new Date(a.getAttribute('data-updated') || 0);
      } else if (sortVal === 'oldest') {
        return new Date(a.getAttribute('data-updated') || 0) - new Date(b.getAttribute('data-updated') || 0);
      } else if (sortVal === 'name') {
        return a.getAttribute('data-name').localeCompare(b.getAttribute('data-name'));
      }
      return 0;
    });

    // Update DOM
    repoCards.forEach(card => card.style.display = 'none');
    visibleCards.forEach(card => {
      card.style.display = '';
      repoGrid.appendChild(card); // preserve sort order
    });

    if (repoCountBadge) {
      repoCountBadge.textContent = visibleCards.length;
    }

    if (emptyState) {
      emptyState.style.display = visibleCards.length === 0 ? 'block' : 'none';
    }
  }

  searchInput?.addEventListener('input', filterAndSortRepos);
  langSelect?.addEventListener('change', filterAndSortRepos);
  sortSelect?.addEventListener('change', filterAndSortRepos);
});

// Global Git Clone Clipboard Copy Handler
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn-copy-clone');
  if (!btn) return;

  const cloneUrl = btn.getAttribute('data-clone') || '';
  if (!cloneUrl) return;

  const command = `git clone ${cloneUrl}`;
  navigator.clipboard.writeText(command).then(() => {
    const origHtml = btn.innerHTML;
    btn.innerHTML = `<i class="fas fa-check me-1 text-success"></i> Copied!`;
    btn.classList.remove('btn-outline-secondary');
    btn.classList.add('btn-success', 'text-white');
    setTimeout(() => {
      btn.innerHTML = origHtml;
      btn.classList.remove('btn-success', 'text-white');
      btn.classList.add('btn-outline-secondary');
    }, 2000);
  }).catch(() => {
    prompt('Copy git clone command:', command);
  });
});
