const drop = document.getElementById('drop');
const fileInput = document.getElementById('file');
const preview = document.getElementById('preview');
const progress = document.getElementById('progress');
const downloadBtn = document.getElementById('downloadBtn');
const fileInfo = document.getElementById('fileInfo');

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    preview.src = e.target.result;
    preview.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

function showFileInfo(file) {
  fileInfo.textContent = `${file.name} (${(file.size/1024).toFixed(1)} KB)`;
  fileInfo.classList.remove('hidden');
}

function resetUI() {
  preview.src = '';
  preview.style.display = 'none';
  progress.classList.add('hidden');
  progress.classList.remove('processing');
  downloadBtn.classList.add('hidden');
  downloadBtn.href = '#';
  fileInfo.textContent = '';
  fileInfo.classList.add('hidden');
}

function setProcessingState(isProcessing) {
  fileInput.disabled = isProcessing;
  drop.style.pointerEvents = isProcessing ? 'none' : 'auto';
  drop.style.opacity = isProcessing ? '0.6' : '1';
}

function handleFile(file) {
  if (!file.type.startsWith('image/')) {
    alert('Please select an image file.');
    return;
  }
  resetUI();
  showFileInfo(file);
  showPreview(file);
  progress.classList.remove('hidden');
  progress.textContent = 'Processing...';
  progress.classList.add('processing');
  setProcessingState(true);

  const formData = new FormData();
  formData.append('image', file);

  fetch('/remove', {
    method: 'POST',
    body: formData
  })
    .then(async response => {
      setProcessingState(false);
      progress.classList.remove('processing');
      if (!response.ok) {
        let err = 'Failed to process image';
        try {
          const data = await response.json();
          err = data.error || err;
        } catch {}
        throw new Error(err);
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      preview.src = url;
      preview.style.display = 'block';
      downloadBtn.href = url;
      downloadBtn.classList.remove('hidden');
      progress.classList.add('hidden');
    })
    .catch(err => {
      setProcessingState(false);
      progress.classList.remove('processing');
      progress.textContent = 'Error: ' + err.message;
    });
}

// Drag & Drop events
drop.addEventListener('dragover', e => {
  e.preventDefault();
  drop.classList.add('dragover');
});
drop.addEventListener('dragleave', e => {
  drop.classList.remove('dragover');
});
drop.addEventListener('drop', e => {
  e.preventDefault();
  drop.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

// File input event
fileInput.addEventListener('change', e => {
  const file = e.target.files[0];
  if (file) handleFile(file);
});

// Keyboard accessibility: focus file input on Enter/Space
drop.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' ') {
    fileInput.click();
  }
});
drop.tabIndex = 0;
drop.setAttribute('role', 'button');
drop.setAttribute('aria-label', 'Upload image by clicking or dragging and dropping');

// Make "Browse" text open the file dialog
document.querySelector('.browse-btn').addEventListener('click', (e) => {
  e.preventDefault();
  fileInput.click();
});