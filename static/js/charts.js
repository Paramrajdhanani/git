/* ==========================================================================
   GitHub Profile Finder - Dynamic Theme-Aware Chart.js Visualizations
   ========================================================================== */

const activeCharts = [];

document.addEventListener('DOMContentLoaded', () => {
  if (typeof Chart === 'undefined') return;

  const langDataEl = document.getElementById('chart-languages-data');
  const starDataEl = document.getElementById('chart-stars-data');
  const dnaDataEl = document.getElementById('chart-dna-data');

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

  if (dnaDataEl) {
    try {
      const dnaData = JSON.parse(dnaDataEl.textContent);
      initDnaChart(dnaData);
    } catch (e) {
      console.error("Error parsing DNA chart data:", e);
    }
  }

  // Listen for real-time theme changes
  window.addEventListener('themeChanged', () => {
    updateChartsTheme();
  });
});

function getThemeColors() {
  const styles = getComputedStyle(document.documentElement);
  return {
    textMain: styles.getPropertyValue('--text-main').trim() || '#f0f6fc',
    textMuted: styles.getPropertyValue('--text-muted').trim() || '#8b949e',
    gridLine: styles.getPropertyValue('--glass-border').trim() || 'rgba(255, 255, 255, 0.08)',
  };
}

function updateChartsTheme() {
  const colors = getThemeColors();
  
  activeCharts.forEach(chart => {
    if (!chart) return;
    
    if (chart.options.plugins?.legend?.labels) {
      chart.options.plugins.legend.labels.color = colors.textMain;
    }
    
    if (chart.options.scales?.x) {
      if (chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = colors.textMuted;
    }
    
    if (chart.options.scales?.y) {
      if (chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = colors.textMuted;
      if (chart.options.scales.y.grid) chart.options.scales.y.grid.color = colors.gridLine;
    }
    
    if (chart.options.scales?.r) {
      if (chart.options.scales.r.ticks) chart.options.scales.r.ticks.color = colors.textMuted;
      if (chart.options.scales.r.pointLabels) chart.options.scales.r.pointLabels.color = colors.textMain;
      if (chart.options.scales.r.grid) chart.options.scales.r.grid.color = colors.gridLine;
    }

    chart.update();
  });
}

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
  const themeColors = getThemeColors();

  const chart = new Chart(ctx, {
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
            color: themeColors.textMain,
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
      animation: {
        animateScale: true,
        animateRotate: true,
        duration: 1400,
        easing: 'easeOutQuart'
      }
    }
  });

  activeCharts.push(chart);
}

// Repository Stars Bar Chart
function initStarsChart(repos) {
  const ctx = document.getElementById('starsBarChart');
  if (!ctx) return;

  const sortedRepos = [...repos].sort((a, b) => b.stargazers_count - a.stargazers_count).slice(0, 8);
  const labels = sortedRepos.map(r => r.name);
  const values = sortedRepos.map(r => r.stargazers_count);
  const themeColors = getThemeColors();

  const chart = new Chart(ctx, {
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
          ticks: { color: themeColors.textMuted },
          grid: { display: false }
        },
        y: {
          ticks: { color: themeColors.textMuted },
          grid: { color: themeColors.gridLine }
        }
      },
      plugins: {
        legend: { display: false }
      },
      animation: {
        duration: 1200,
        easing: 'easeOutQuart'
      }
    }
  });

  activeCharts.push(chart);
}

// Repository Size Chart
function initSizeChart(repos) {
  const ctx = document.getElementById('sizeChart');
  if (!ctx) return;

  const sortedRepos = [...repos].sort((a, b) => b.size - a.size).slice(0, 8);
  const labels = sortedRepos.map(r => r.name);
  const values = sortedRepos.map(r => Math.round(r.size / 1024 * 10) / 10); // in MB
  const themeColors = getThemeColors();

  const chart = new Chart(ctx, {
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
          ticks: { color: themeColors.textMuted },
          grid: { display: false }
        },
        y: {
          ticks: { color: themeColors.textMuted },
          grid: { color: themeColors.gridLine }
        }
      },
      plugins: {
        legend: { display: false }
      },
      animation: {
        duration: 1300,
        easing: 'easeOutQuart'
      }
    }
  });

  activeCharts.push(chart);
}

// Developer DNA Radar Chart
function initDnaChart(dnaData) {
  const ctx = document.getElementById('dnaRadarChart');
  if (!ctx) return;

  const labels = Object.keys(dnaData);
  const values = Object.values(dnaData);
  const themeColors = getThemeColors();

  const chart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: 'DNA Score',
        data: values,
        backgroundColor: 'rgba(35, 134, 54, 0.25)',
        borderColor: '#2ea043',
        pointBackgroundColor: '#2ea043',
        pointBorderColor: '#fff',
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: themeColors.gridLine },
          grid: { color: themeColors.gridLine },
          pointLabels: { color: themeColors.textMain, font: { family: 'Inter', size: 10 } },
          ticks: { display: false, max: 100 }
        }
      },
      plugins: {
        legend: { display: false }
      },
      animation: {
        duration: 1500,
        easing: 'easeInOutCubic'
      }
    }
  });

  activeCharts.push(chart);
}


