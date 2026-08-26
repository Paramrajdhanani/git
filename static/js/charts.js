/* ==========================================================================
   GitHub Profile Finder - Chart.js Data Visualizations
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  if (typeof Chart === 'undefined') return;

  const langDataEl = document.getElementById('chart-languages-data');
  const starDataEl = document.getElementById('chart-stars-data');

  if (langDataEl) {
    try {
      const langData = JSON.parse(langDataEl.textContent);
      initLanguageChart(langData);
    } catch (e) {
      console.error("Error parsing language chart data:", e);
    }
  }

  if (starDataEl) {
    try {
      const starData = JSON.parse(starDataEl.textContent);
      initStarsChart(starData);
      initSizeChart(starData);
    } catch (e) {
      console.error("Error parsing stars chart data:", e);
    }
  }
});

const LANGUAGE_COLORS = {
  'Python': '#3572A5',
  'JavaScript': '#f1e05a',
  'TypeScript': '#3178c6',
  'HTML': '#e34c26',
  'CSS': '#563d7c',
  'C': '#555555',
  'C++': '#f34b7d',
  'C#': '#178600',
  'Java': '#b07219',
  'Go': '#00ADD8',
  'Rust': '#dea584',
  'PHP': '#4F5D95',
  'Ruby': '#701516',
  'Shell': '#89e051',
  'Kotlin': '#A97BFF',
  'Swift': '#F05138',
  'Dart': '#00B4AB',
  'Vue': '#41b883',
};

function getLangColor(lang, index) {
  if (LANGUAGE_COLORS[lang]) return LANGUAGE_COLORS[lang];
  const defaultColors = ['#2f81f7', '#a371f7', '#3fb950', '#d29922', '#f85149', '#58a6ff', '#bc8cff'];
  return defaultColors[index % defaultColors.length];
}

// Language Distribution Doughnut Chart
function initLanguageChart(data) {
  const ctx = document.getElementById('languageDoughnutChart');
  if (!ctx) return;

  const labels = Object.keys(data);
  const values = Object.values(data);
  const colors = labels.map((l, idx) => getLangColor(l, idx));

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: 'transparent',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-main').trim() || '#f0f6fc',
            font: { family: 'Inter', size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => ` ${context.label}: ${context.raw} repos`
          }
        }
      },
      cutout: '70%',
    }
  });
}

// Repository Stars Bar Chart
function initStarsChart(repos) {
  const ctx = document.getElementById('starsBarChart');
  if (!ctx) return;

  // Filter top 8 starred repos
  const sortedRepos = [...repos].sort((a, b) => b.stargazers_count - a.stargazers_count).slice(0, 8);
  const labels = sortedRepos.map(r => r.name);
  const values = sortedRepos.map(r => r.stargazers_count);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Stars',
        data: values,
        backgroundColor: 'rgba(47, 129, 247, 0.7)',
        borderColor: '#2f81f7',
        borderWidth: 1.5,
        borderRadius: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() },
          grid: { display: false }
        },
        y: {
          ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// Repository Size Chart
function initSizeChart(repos) {
  const ctx = document.getElementById('sizeChart');
  if (!ctx) return;

  const sortedRepos = [...repos].sort((a, b) => b.size - a.size).slice(0, 8);
  const labels = sortedRepos.map(r => r.name);
  const values = sortedRepos.map(r => Math.round(r.size / 1024 * 10) / 10); // in MB

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Size (MB)',
        data: values,
        backgroundColor: 'rgba(163, 113, 247, 0.7)',
        borderColor: '#a371f7',
        borderWidth: 1.5,
        borderRadius: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() },
          grid: { display: false }
        },
        y: {
          ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}
