// ============================================================
// upload.js — Handles file selection, drag-drop, and
//             form submission with animated loading states
// ============================================================

const dropzone    = document.getElementById('dropzone');
const fileInput   = document.getElementById('resumeFile');
const filePreview = document.getElementById('filePreview');
const fileName    = document.getElementById('fileName');
const fileSize    = document.getElementById('fileSize');
const fileRemove  = document.getElementById('fileRemove');
const uploadForm  = document.getElementById('uploadForm');
const analyzeBtn  = document.getElementById('analyzeBtn');
const loadingOverlay = document.getElementById('loadingOverlay');

// ── Drag and Drop Handlers ────────────────────────────────

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('drag-over');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('drag-over');
});

dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    showFilePreview(file);
  }
});

// ── File Input Change ─────────────────────────────────────

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    showFilePreview(fileInput.files[0]);
  }
});

// ── Show File Preview ─────────────────────────────────────

function showFilePreview(file) {
  // Validate extension
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['pdf', 'docx'].includes(ext)) {
    alert('❌ Please upload a PDF or DOCX file only.');
    return;
  }
  // Validate size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('❌ File size must be less than 5MB.');
    return;
  }
  // Show preview
  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);
  document.getElementById('dropzoneContent').style.opacity = '0.4';
  filePreview.classList.remove('d-none');
}

// ── Remove File ───────────────────────────────────────────

fileRemove.addEventListener('click', () => {
  fileInput.value = '';
  filePreview.classList.add('d-none');
  document.getElementById('dropzoneContent').style.opacity = '1';
});

// ── Format file size ──────────────────────────────────────

function formatBytes(bytes) {
  if (bytes < 1024)       return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ── Loading Animation Steps ───────────────────────────────

const loadingMessages = [
  '📄 Extracting text from resume...',
  '🧠 Identifying skills with NLP...',
  '📊 Calculating your resume score...',
  '🎯 Recommending career paths...'
];

const stepIds = ['step1', 'step2', 'step3', 'step4'];

function animateLoadingSteps() {
  let idx = 0;
  const interval = setInterval(() => {
    if (idx > 0) {
      document.getElementById(stepIds[idx - 1]).classList.remove('active');
      document.getElementById(stepIds[idx - 1]).classList.add('done');
      document.getElementById(stepIds[idx - 1]).textContent =
        '✅ ' + document.getElementById(stepIds[idx - 1]).textContent.slice(3);
    }
    if (idx < stepIds.length) {
      document.getElementById(stepIds[idx]).classList.add('active');
      document.getElementById('loadingText').textContent = loadingMessages[idx];
      idx++;
    } else {
      clearInterval(interval);
    }
  }, 1000);
}

// ── Form Submission ───────────────────────────────────────

uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Validate file selected
  if (!fileInput.files || fileInput.files.length === 0) {
    alert('⚠️ Please select a resume file to analyze.');
    return;
  }

  // Show loading overlay
  loadingOverlay.classList.remove('d-none');
  analyzeBtn.disabled = true;
  animateLoadingSteps();

  // Build FormData
  const formData = new FormData(uploadForm);

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      // Hide loader and show error
      loadingOverlay.classList.add('d-none');
      analyzeBtn.disabled = false;
      alert('❌ Error: ' + data.error);
      return;
    }

    // Store result in sessionStorage for results page
    sessionStorage.setItem('resumeAnalysis', JSON.stringify(data));

    // Redirect to results page
    window.location.href = '/results';

  } catch (err) {
    console.error('Analysis error:', err);
    loadingOverlay.classList.add('d-none');
    analyzeBtn.disabled = false;
    alert('❌ Something went wrong. Please make sure the Flask server is running.');
  }
});
