/* ==========================================================================
   GitHub Profile Finder - Main Interactive JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initThemeSwitcher();
  initAutocomplete();
  initCounters();
  initFavoriteButtons();
  initAOS();
});

// Initialize AOS (Animate on Scroll)
function initAOS() {
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      once: true,
      easing: 'ease-out-quad'
    });
  }
}

// Dark / Light Theme Toggle System
function initThemeSwitcher() {
  const themeToggles = document.querySelectorAll('.theme-toggle-btn');
  const storedTheme = localStorage.getItem('theme') || document.documentElement.getAttribute('data-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', storedTheme);

  function updateIcons(theme) {
    themeToggles.forEach(btn => {
      const darkIcon = btn.querySelector('.dark-icon');
      const lightIcon = btn.querySelector('.light-icon');
      if (darkIcon && lightIcon) {
        if (theme === 'dark') {
          darkIcon.classList.remove('d-none');
          lightIcon.classList.add('d-none');
        } else {
          darkIcon.classList.add('d-none');
          lightIcon.classList.remove('d-none');
        }
      }
    });
  }

  updateIcons(storedTheme);

  themeToggles.forEach(btn => {
    btn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateIcons(newTheme);

      // Sync with Backend
      fetch('/accounts/api/theme/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ theme: newTheme })
      }).catch(err => console.log('Theme sync error:', err));
    });
  });
}

// Live Autocomplete for Search Box
function initAutocomplete() {
  const searchInputs = document.querySelectorAll('.search-autocomplete-input');
  
  searchInputs.forEach(input => {
    const dropdown = input.closest('.search-box-wrapper')?.querySelector('.autocomplete-dropdown');
    if (!dropdown) return;

    let timeout = null;

    input.addEventListener('input', (e) => {
      clearTimeout(timeout);
      const query = e.target.value.trim();

      if (query.length < 2) {
        dropdown.style.display = 'none';
        return;
      }

      timeout = setTimeout(() => {
        fetch(`/api/autocomplete/?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            if (data.suggestions && data.suggestions.length > 0) {
              dropdown.innerHTML = data.suggestions.map(s => `
                <div class="autocomplete-item" onclick="window.location.href='/user/${s.username}/'">
                  <img src="${s.avatar_url}" alt="${s.username}">
                  <div>
                    <strong style="color: var(--text-main);">@${s.username}</strong>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">${s.name || ''}</div>
                  </div>
                </div>
              `).join('');
              dropdown.style.display = 'block';
            } else {
              dropdown.style.display = 'none';
            }
          })
          .catch(() => dropdown.style.display = 'none');
      }, 250);
    });

    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
      }
    });
  });
}

// Animated Stat Counters
function initCounters() {
  const counters = document.querySelectorAll('.counter-value');
  counters.forEach(counter => {
    const target = parseInt(counter.getAttribute('data-target') || '0', 10);
    if (isNaN(target)) return;

    let count = 0;
    const duration = 1500;
    const increment = Math.max(1, Math.ceil(target / (duration / 16)));

    const timer = setInterval(() => {
      count += increment;
      if (count >= target) {
        counter.textContent = target.toLocaleString();
        clearInterval(timer);
      } else {
        counter.textContent = count.toLocaleString();
      }
    }, 16);
  });
}

// Favorite Profile Button Toggle
function initFavoriteButtons() {
  const favBtns = document.querySelectorAll('.btn-favorite-toggle');
  
  favBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const username = btn.getAttribute('data-username');
      const name = btn.getAttribute('data-name');
      const avatar = btn.getAttribute('data-avatar');
      const bio = btn.getAttribute('data-bio');

      fetch('/favorites/api/toggle/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ username, name, avatar_url: avatar, bio })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'unauthenticated') {
          Swal.fire({
            icon: 'info',
            title: 'Account Required',
            text: data.message,
            showCancelButton: true,
            confirmButtonText: 'Login Now',
            cancelButtonText: 'Cancel'
          }).then(result => {
            if (result.isConfirmed) {
              window.location.href = '/accounts/login/';
            }
          });
        } else if (data.status === 'success') {
          const icon = btn.querySelector('i');
          if (data.is_favorite) {
            btn.classList.add('btn-warning');
            btn.classList.remove('btn-outline-warning');
            if (icon) icon.className = 'fas fa-star';
          } else {
            btn.classList.remove('btn-warning');
            btn.classList.add('btn-outline-warning');
            if (icon) icon.className = 'far fa-star';
          }
          
          Swal.fire({
            toast: true,
            position: 'top-end',
            icon: 'success',
            title: data.message,
            showConfirmButton: false,
            timer: 2500
          });
        }
      })
      .catch(err => console.error('Favorite error:', err));
    });
  });
}

// Copy URL to Clipboard
function copyProfileUrl() {
  const url = window.location.href;
  navigator.clipboard.writeText(url).then(() => {
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Profile URL copied to clipboard!',
      showConfirmButton: false,
      timer: 2000
    });
  }).catch(() => {
    alert('Failed to copy URL');
  });
}

// Helper to extract CSRF Token
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
         document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
}
