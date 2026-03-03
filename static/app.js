const urlInput = document.getElementById('urlInput');
const fetchButton = document.getElementById('fetchButton');
const downloadButton = document.getElementById('downloadButton');
const metadataEl = document.getElementById('metadata');
const videoTitle = document.getElementById('videoTitle');
const thumbnail = document.getElementById('thumbnail');
const duration = document.getElementById('duration');
const formatSelect = document.getElementById('formatSelect');
const audioOnly = document.getElementById('audioOnly');
const savePath = document.getElementById('savePath');
const progressWrap = document.getElementById('progressWrap');
const progressBar = document.getElementById('progressBar');
const statusMessage = document.getElementById('statusMessage');
const historyList = document.getElementById('historyList');
const themeToggle = document.getElementById('themeToggle');

const formatDuration = (seconds) => {
  if (!seconds) return 'Unknown duration';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
};

const showError = (message) => {
  statusMessage.textContent = message;
  statusMessage.style.color = '#d9534f';
};

const showSuccess = (message) => {
  statusMessage.textContent = message;
  statusMessage.style.color = '#4bbf73';
};

fetchButton.addEventListener('click', async () => {
  statusMessage.textContent = '';
  const url = urlInput.value.trim();
  try {
    const response = await fetch('/api/metadata', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Failed to fetch metadata');

    metadataEl.classList.remove('hidden');
    videoTitle.textContent = data.title || 'Untitled';
    thumbnail.src = data.thumbnail || '';
    duration.textContent = `Duration: ${formatDuration(data.duration)}`;

    formatSelect.innerHTML = '';
    for (const fmt of data.formats) {
      const option = document.createElement('option');
      option.value = fmt.format_id;
      option.textContent = fmt.label;
      formatSelect.appendChild(option);
    }
    showSuccess('Metadata loaded. Choose options and click Download.');
  } catch (error) {
    showError(error.message);
  }
});

downloadButton.addEventListener('click', async () => {
  const url = urlInput.value.trim();
  const format_id = formatSelect.value;
  progressWrap.classList.remove('hidden');
  progressBar.style.width = '0%';

  try {
    const response = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        format_id,
        audio_only: audioOnly.checked,
        save_dir: savePath.value.trim() || null,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Failed to start download');

    pollStatus(data.task_id);
  } catch (error) {
    showError(error.message);
  }
});

async function pollStatus(taskId) {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/download/${taskId}/status`);
    const data = await response.json();

    if (!response.ok) {
      clearInterval(interval);
      showError(data.error || 'Unable to retrieve status');
      return;
    }

    progressBar.style.width = `${data.progress || 0}%`;
    statusMessage.textContent = data.message || data.status;

    if (data.status === 'completed') {
      clearInterval(interval);
      showSuccess(`Completed: ${data.file_path}`);
      loadHistory();
    }

    if (data.status === 'failed') {
      clearInterval(interval);
      showError(`Failed: ${data.message}`);
    }
  }, 1000);
}

async function loadHistory() {
  const response = await fetch('/api/history');
  const data = await response.json();
  historyList.innerHTML = '';

  for (const item of data.items || []) {
    const li = document.createElement('li');
    li.textContent = `${item.downloaded_at} - ${item.title} (${item.audio_only ? 'MP3' : 'Video'}) -> ${item.file_path}`;
    historyList.appendChild(li);
  }
}

themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
});

if (localStorage.getItem('theme') === 'dark') {
  document.body.classList.add('dark');
}

loadHistory();
