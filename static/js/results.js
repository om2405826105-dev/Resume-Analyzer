// ============================================================
// results.js — Renders all analysis results and charts
//              using Chart.js and the stored sessionStorage data
// ============================================================

// ── Load Data from sessionStorage ────────────────────────
const raw = sessionStorage.getItem('resumeAnalysis');

if (!raw) {
  // No data — show empty state
  document.getElementById('resultsContent').classList.add('d-none');
  document.getElementById('noDataState').classList.remove('d-none');
} else {
  const data = JSON.parse(raw);
  renderResults(data);
}

// ── Main Render Function ──────────────────────────────────

function renderResults(data) {
  setHeaderInfo(data);
  renderScore(data.score);
  renderSkills(data.skills);
  renderSkillDistChart(data.skill_distribution);
  renderCareerMatchChart(data.careers);
  renderCareerCards(data.careers);
  renderSkillGap(data.careers);
  populateRoadmapSelector(data.careers);
  renderRoadmap();
  renderSuggestions(data.suggestions);
}

// ── Header: Name & Email ──────────────────────────────────

function setHeaderInfo(data) {
  const nameEl   = document.getElementById('resultName');
  const emailEl  = document.getElementById('resultEmail');
  const avatarEl = document.getElementById('userAvatar');

  const displayName = data.name && data.name !== 'Anonymous' ? data.name : 'Resume Analysis';
  nameEl.textContent  = displayName;
  emailEl.textContent = data.email || '';
  avatarEl.textContent = displayName.charAt(0).toUpperCase();

  document.title = `${displayName} — ResumeAI Results`;
}

// ── Resume Score (Doughnut Gauge) ─────────────────────────

function renderScore(score) {
  document.getElementById('scoreValue').textContent = score;

  // Grade label
  let grade, color;
  if (score >= 85)      { grade = '🏆 Excellent Resume'; color = '#22c55e'; }
  else if (score >= 70) { grade = '👍 Good Resume';      color = '#f5a623'; }
  else if (score >= 55) { grade = '📝 Average Resume';   color = '#f59e0b'; }
  else                  { grade = '⚠️ Needs Improvement'; color = '#ef4444'; }

  document.getElementById('scoreGrade').textContent = grade;
  document.getElementById('scoreGrade').style.color  = color;
  document.getElementById('scoreMeta').textContent   = `Score out of 100 based on skills, content, and structure`;

  // Doughnut chart
  const ctx = document.getElementById('scoreGauge').getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: [color, '#252836'],
        borderWidth: 0,
        hoverOffset: 0
      }]
    },
    options: {
      cutout: '78%',
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { duration: 1200, easing: 'easeInOutQuart' }
    }
  });
}

// ── Skills Grid ───────────────────────────────────────────

function renderSkills(skills) {
  const grid = document.getElementById('skillsGrid');
  document.getElementById('skillCountBadge').textContent = skills.length;

  if (skills.length === 0) {
    grid.innerHTML = '<p style="color:var(--text-muted); font-size:0.85rem;">No specific skills detected. Try a more detailed resume.</p>';
    return;
  }

  grid.innerHTML = skills.map(s =>
    `<span class="skill-chip">${s}</span>`
  ).join('');
}

// ── Skill Distribution Pie Chart ─────────────────────────

function renderSkillDistChart(dist) {
  const labels = Object.keys(dist);
  const values = Object.values(dist);

  if (labels.length === 0) return;

  const COLORS = ['#f5a623','#4f8ef7','#22c55e','#a78bfa','#f87171','#34d399'];

  const ctx = document.getElementById('skillDistChart').getContext('2d');
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: COLORS.slice(0, labels.length),
        borderColor: '#13161e',
        borderWidth: 3
      }]
    },
    options: {
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#7a7f9a', font: { size: 11 }, padding: 12, boxWidth: 12 }
        }
      },
      animation: { duration: 1000 }
    }
  });
}

// ── Career Match Bar Chart ────────────────────────────────

function renderCareerMatchChart(careers) {
  const top5    = careers.slice(0, 5);
  const labels  = top5.map(c => c.career);
  const values  = top5.map(c => c.match_percentage);

  const ctx = document.getElementById('careerMatchChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Match %',
        data: values,
        backgroundColor: values.map((v, i) => i === 0 ? '#f5a623' : '#4f8ef744'),
        borderColor:     values.map((v, i) => i === 0 ? '#f5a623' : '#4f8ef7'),
        borderWidth: 2,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      scales: {
        x: {
          max: 100,
          ticks: { color: '#7a7f9a', callback: v => v + '%' },
          grid:  { color: '#252836' }
        },
        y: { ticks: { color: '#eef0f6', font: { size: 12 } }, grid: { display: false } }
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.raw}% match` } }
      },
      animation: { duration: 1200 }
    }
  });
}

// ── Career Recommendation Cards ───────────────────────────

function renderCareerCards(careers) {
  const container = document.getElementById('careerCards');
  container.innerHTML = careers.map((c, i) => `
    <div class="col-md-6 col-lg-4">
      <div class="career-card ${i === 0 ? 'top-match' : ''}">
        ${i === 0 ? '<div class="top-badge">⭐ Top Match</div>' : ''}
        <div class="career-icon">${c.icon}</div>
        <div class="career-title">${c.career}</div>
        <div class="career-desc">${c.description}</div>
        <div class="career-salary">Avg: ${c.avg_salary}</div>
        <div class="match-bar-label">
          <span>Match</span>
          <span class="match-pct">${c.match_percentage}%</span>
        </div>
        <div class="match-progress">
          <div style="width:${c.match_percentage}%; background: ${i===0?'linear-gradient(90deg,#f5a623,#ff8c00)':'linear-gradient(90deg,#4f8ef7,#7c3aed)'}"></div>
        </div>
      </div>
    </div>
  `).join('');
}

// ── Skill Gap Analysis ────────────────────────────────────

function renderSkillGap(careers) {
  const container = document.getElementById('skillGapContainer');
  container.innerHTML = careers.slice(0, 3).map(c => `
    <div class="gap-item">
      <div class="gap-career">
        ${c.icon} ${c.career}
        <span>— ${c.match_percentage}% match</span>
      </div>
      ${c.matched_skills.length > 0 ? `
        <div class="gap-section">
          <div class="gap-label">✅ Skills You Have</div>
          <div class="gap-chips">
            ${c.matched_skills.map(s => `<span class="chip-have">${s}</span>`).join('')}
          </div>
        </div>` : ''}
      ${c.missing_skills.length > 0 ? `
        <div class="gap-section mt-2">
          <div class="gap-label">❌ Missing Skills</div>
          <div class="gap-chips">
            ${c.missing_skills.map(s => `<span class="chip-missing">${s}</span>`).join('')}
          </div>
        </div>` : '<p style="color:var(--green);font-size:0.82rem;margin:6px 0 0">🎉 You have all required skills!</p>'}
    </div>
  `).join('');
}

// ── Roadmap Selector + Renderer ───────────────────────────

function populateRoadmapSelector(careers) {
  const sel = document.getElementById('roadmapSelector');
  // Store careers globally for roadmap rendering
  window._careers = careers;
  sel.innerHTML = careers.map((c, i) =>
    `<option value="${i}">${c.icon} ${c.career}</option>`
  ).join('');
}

function renderRoadmap() {
  const idx   = parseInt(document.getElementById('roadmapSelector').value);
  const career = window._careers[idx];
  const container = document.getElementById('roadmapSteps');

  container.innerHTML = `<div class="roadmap-steps">
    ${career.roadmap.map((step, i) => `
      <div class="roadmap-step">
        <div class="roadmap-num">${i + 1}</div>
        <div class="roadmap-text">${step}</div>
      </div>
    `).join('')}
  </div>`;
}

// ── Improvement Suggestions ───────────────────────────────

function renderSuggestions(suggestions) {
  const container = document.getElementById('suggestionsContainer');

  if (!suggestions || suggestions.length === 0) {
    container.innerHTML = `<div class="all-good">🎉 Your resume looks comprehensive! No major improvements needed.</div>`;
    return;
  }

  const icons = ['📎','📝','🔗','📞','🚀','💼','📊','✍️','🎓','🏆'];
  container.innerHTML = suggestions.map((s, i) => `
    <div class="suggestion-item">
      <span class="s-icon">${icons[i % icons.length]}</span>
      <span>${s}</span>
    </div>
  `).join('');
}
