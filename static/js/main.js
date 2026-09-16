/* ==========================================================================
   GitHub Profile Finder - Main Interactive JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initThemeSwitcher();
  initAutocomplete();
  initCounters();
  initFavoriteButtons();
  initKeyboardShortcuts();
  initCommandPalette();
  initRippleEffects();
  initScrollProgress();
  initScrollToTop();
  initSmartNavbarOnScroll();
  initSmoothScrollLinks();
  initAOS();
});

// Initialize Keyboard Shortcuts (Ctrl+K and ?)
function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ctrl + K or Cmd + K -> Command Palette
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openCommandPalette();
    }
    // ? -> Shortcuts Modal (if not inside input)
    if (e.key === '?' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      openShortcutsModal();
    }
  });
}

// Live Quick Find / Command Palette Search Engine
function initCommandPalette() {
  const cmdInput = document.getElementById('cmdPaletteInput');
  const resultsContainer = document.getElementById('cmdPaletteResults');
  if (!cmdInput || !resultsContainer) return;

  const defaultNavHTML = resultsContainer.innerHTML;
  let debounceTimeout = null;

  cmdInput.addEventListener('input', (e) => {
    const query = e.target.value.trim().toLowerCase();
    clearTimeout(debounceTimeout);

    if (!query) {
      resultsContainer.innerHTML = defaultNavHTML;
      return;
    }

    debounceTimeout = setTimeout(() => {
      fetch(`/api/autocomplete/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          let html = '';
          
          if (data.suggestions && data.suggestions.length > 0) {
            html += `<div class="text-muted small px-2 fw-semibold mb-2">DEVELOPER PROFILES</div>`;
            data.suggestions.forEach(s => {
              html += `
                <a href="/user/${encodeURIComponent(s.username)}/" class="cmd-item p-2 rounded d-flex align-items-center justify-content-between text-decoration-none mb-1">
                  <div class="d-flex align-items-center gap-3">
                    <img src="${s.avatar_url}" class="rounded-circle" style="width: 32px; height: 32px; object-fit: cover;" alt="">
                    <div>
                      <span class="text-main fw-bold">@${s.username}</span>
                      <div class="text-muted small">${s.name || ''}</div>
                    </div>
                  </div>
                  <span class="badge bg-primary-subtle text-primary">View Profile</span>
                </a>
              `;
            });
          }

          html += `
            <div class="text-muted small px-2 fw-semibold my-2">SEARCH COMMANDS</div>
            <a href="/user/${encodeURIComponent(query)}/" class="cmd-item p-2 rounded d-flex align-items-center gap-3 text-decoration-none mb-1">
              <i class="fas fa-user-circle text-primary fs-5"></i>
              <div>
                <span class="text-main fw-bold">Go to profile @${query}</span>
                <div class="text-muted small">Direct user lookup</div>
              </div>
            </a>
            <a href="/search/repos/?q=${encodeURIComponent(query)}" class="cmd-item p-2 rounded d-flex align-items-center gap-3 text-decoration-none mb-1">
              <i class="fas fa-boxes text-success fs-5"></i>
              <div>
                <span class="text-main fw-bold">Search repositories for "${query}"</span>
                <div class="text-muted small">Open-source code explorer</div>
              </div>
            </a>
          `;

          resultsContainer.innerHTML = html;
        })
        .catch(() => {
          resultsContainer.innerHTML = defaultNavHTML;
        });
    }, 150);
  });

  cmdInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const val = cmdInput.value.trim();
      if (val) {
        window.location.href = `/user/${encodeURIComponent(val)}/`;
      }
    }
  });
}

function openCommandPalette() {
  const modalEl = document.getElementById('cmdPaletteModal');
  if (modalEl && typeof bootstrap !== 'undefined') {
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
    setTimeout(() => {
      const input = document.getElementById('cmdPaletteInput');
      if (input) {
        input.focus();
        input.select();
      }
    }, 200);
  }
}

function openShortcutsModal() {
  const modalEl = document.getElementById('shortcutsModal');
  if (modalEl && typeof bootstrap !== 'undefined') {
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
  }
}

// Open Repository README Documentation Modal
function openReadmeModal(username, reponame) {
  const modalEl = document.getElementById('readmeModal');
  const repoNameEl = document.getElementById('readmeModalRepoName');
  const spinnerEl = document.getElementById('readmeModalSpinner');
  const bodyEl = document.getElementById('readmeModalBody');

  if (!modalEl) return;

  if (repoNameEl) repoNameEl.textContent = `${username}/${reponame}`;
  if (spinnerEl) spinnerEl.style.display = 'block';
  if (bodyEl) {
    bodyEl.style.display = 'none';
    bodyEl.innerHTML = '';
  }

  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  modal.show();


  fetch(`/api/repo/readme/?username=${encodeURIComponent(username)}&reponame=${encodeURIComponent(reponame)}`)
    .then(res => res.json())
    .then(data => {
      if (spinnerEl) spinnerEl.style.display = 'none';
      if (bodyEl) {
        bodyEl.innerHTML = data.html || '<p class="text-muted p-4 text-center">No README content available.</p>';
        bodyEl.style.display = 'block';
      }
    })
    .catch(() => {
      if (spinnerEl) spinnerEl.style.display = 'none';
      if (bodyEl) {
        bodyEl.innerHTML = '<p class="text-danger p-4 text-center">Error loading README documentation.</p>';
        bodyEl.style.display = 'block';
      }
    });
}

// Developer Share Card Generator (Canvas)
function generateShareCard(username, name, avatarUrl, primaryLang, devType, stars, repos) {
  const modalEl = document.getElementById('shareCardModal');
  const canvas = document.getElementById('shareCardCanvas');
  if (!canvas || !modalEl) return;

  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;

  // Background Gradient
  const grad = ctx.createLinearGradient(0, 0, width, height);
  grad.addColorStop(0, '#0b0f19');
  grad.addColorStop(0.5, '#121a2b');
  grad.addColorStop(1, '#060913');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, width, height);

  // Border Accent Glow
  ctx.strokeStyle = '#388bfd';
  ctx.lineWidth = 4;
  ctx.strokeRect(0, 0, width, height);

  // Header Title
  ctx.fillStyle = '#388bfd';
  ctx.font = 'bold 20px Inter, sans-serif';
  ctx.fillText('GITHUB DEVELOPER CARD', 30, 45);

  // Profile Info
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 26px Inter, sans-serif';
  ctx.fillText(name || `@${username}`, 30, 95);

  ctx.fillStyle = '#8b949e';
  ctx.font = '16px Inter, sans-serif';
  ctx.fillText(`@${username} • ${devType}`, 30, 125);

  // Stats Grid Line
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(30, 150);
  ctx.lineTo(width - 30, 150);
  ctx.stroke();

  // Metrics Boxes
  const metrics = [
    { label: 'PRIMARY STACK', val: primaryLang },
    { label: 'TOTAL STARS', val: `${stars}` },
    { label: 'REPOSITORIES', val: `${repos}` }
  ];

  metrics.forEach((m, idx) => {
    const x = 30 + idx * 180;
    ctx.fillStyle = '#388bfd';
    ctx.font = 'bold 22px Inter, sans-serif';
    ctx.fillText(m.val, x, 205);

    ctx.fillStyle = '#8b949e';
    ctx.font = 'bold 11px Inter, sans-serif';
    ctx.fillText(m.label, x, 225);
  });

  // Footer Branding
  ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
  ctx.font = '12px Inter, sans-serif';
  ctx.fillText('Verified with GitHub Profile Finder App', 30, 300);

  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

function downloadShareCard() {
  const canvas = document.getElementById('shareCardCanvas');
  if (!canvas) return;

  const image = canvas.toDataURL('image/png');
  const link = document.createElement('a');
  link.download = 'developer_card.png';
  link.href = image;
  link.click();
}

// Material Button Ripple Waves
function initRippleEffects() {
  document.addEventListener('click', (e) => {
    const target = e.target.closest('.btn, .cmd-item, .topic-badge');
    if (!target) return;

    const rect = target.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.className = 'ripple-wave';

    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${e.clientY - rect.top - size / 2}px`;

    target.appendChild(ripple);

    setTimeout(() => {
      ripple.remove();
    }, 600);
  });
}

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
  const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const defaultTheme = systemPrefersDark ? 'dark' : 'dark';
  const storedTheme = localStorage.getItem('theme') || document.documentElement.getAttribute('data-theme') || defaultTheme;

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

      window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));

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

// Animated Stat Counters with IntersectionObserver & Smooth Easing
function initCounters() {
  const counters = document.querySelectorAll('.counter-value');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const counter = entry.target;
        const target = parseInt(counter.getAttribute('data-target') || '0', 10);
        if (isNaN(target)) return;

        if (typeof gsap !== 'undefined') {
          const obj = { val: 0 };
          gsap.to(obj, {
            val: target,
            duration: 1.8,
            ease: "power2.out",
            onUpdate: () => {
              counter.textContent = Math.round(obj.val).toLocaleString();
            }
          });
        } else {
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
        }

        obs.unobserve(counter);
      }
    });
  }, { threshold: 0.2 });

  counters.forEach(counter => observer.observe(counter));
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

// ==========================================================================
// Scroll Up & Down Animations System
// ==========================================================================

// 1. Live Page Reading & Scroll Progress Neon Bar
function initScrollProgress() {
  const progressBar = document.getElementById('scrollProgressBar');
  const ringCircle = document.getElementById('progressRingCircle');
  const circumference = 2 * Math.PI * 20; // Radius = 20

  if (ringCircle) {
    ringCircle.style.strokeDasharray = `${circumference}`;
    ringCircle.style.strokeDashoffset = `${circumference}`;
  }

  function updateScrollProgress() {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const progressPercent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    const boundedProgress = Math.min(Math.max(progressPercent, 0), 100);

    if (progressBar) {
      progressBar.style.width = `${boundedProgress}%`;
    }

    if (ringCircle) {
      const offset = circumference - (boundedProgress / 100) * circumference;
      ringCircle.style.strokeDashoffset = `${offset}`;
    }
  }

  window.addEventListener('scroll', updateScrollProgress, { passive: true });
  updateScrollProgress();
}

// Global Floating Navigation & Scroll-to-Top Handler
window.handleFloatingNavClick = function(event) {
  if (event) event.preventDefault();

  const currentPath = window.location.pathname;
  const isHome = currentPath === '/' || currentPath === '' || currentPath === '/index/' || currentPath.endsWith('/finder/');

  if (!isHome) {
    window.location.href = '/';
  } else {
    try {
      window.scrollTo({
        top: 0,
        left: 0,
        behavior: 'smooth'
      });
    } catch (e) {}
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  }
};

// 2. Animated Floating Navigation Button (Scroll-to-Top on Home / Go-to-Home from All Pages)
function initScrollToTop() {
  const topBtn = document.getElementById('scrollToTopBtn');
  if (!topBtn) return;

  const currentPath = window.location.pathname;
  const isHomePage = currentPath === '/' || currentPath === '' || currentPath === '/index/' || currentPath.endsWith('/finder/');
  const icon = topBtn.querySelector('.scroll-top-icon');

  if (!isHomePage) {
    topBtn.setAttribute('title', 'Go to Home Page');
    topBtn.setAttribute('aria-label', 'Go to Home Page');
    if (icon) {
      icon.className = 'fas fa-home scroll-top-icon';
    }
    topBtn.classList.add('visible');
  } else {
    topBtn.setAttribute('title', 'Scroll to top');
    topBtn.setAttribute('aria-label', 'Scroll to top of page');
    if (icon) {
      icon.className = 'fas fa-arrow-up scroll-top-icon';
    }
  }

  function toggleTopButton() {
    if (isHomePage) {
      if (window.scrollY > 150) {
        topBtn.classList.add('visible');
      } else {
        topBtn.classList.remove('visible');
      }
    } else {
      topBtn.classList.add('visible');
    }
  }

  topBtn.addEventListener('click', (e) => {
    window.handleFloatingNavClick(e);
  });

  window.addEventListener('scroll', toggleTopButton, { passive: true });
  toggleTopButton();
}

// 3. Smart Navbar Dynamics on Scroll Down vs Scroll Up
function initSmartNavbarOnScroll() {
  const navbar = document.querySelector('.glass-nav');
  if (!navbar) return;

  let lastScrollY = window.scrollY;
  let ticking = false;

  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        const currentScrollY = window.scrollY;

        // Add shadow & shrink if scrolled past header
        if (currentScrollY > 40) {
          navbar.classList.add('nav-scrolled');
        } else {
          navbar.classList.remove('nav-scrolled');
        }

        // Hide on fast scroll down, reveal on scroll up
        if (currentScrollY > 200 && currentScrollY > lastScrollY + 10) {
          navbar.classList.add('nav-hidden');
        } else if (currentScrollY < lastScrollY - 5 || currentScrollY <= 200) {
          navbar.classList.remove('nav-hidden');
        }

        lastScrollY = Math.max(currentScrollY, 0);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

// 4. Smooth Anchor Link Scrolling (e.g. Scroll Down Explore Indicator)
function initSmoothScrollLinks() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || !targetId) return;

      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        e.preventDefault();
        const headerOffset = 80;
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}





