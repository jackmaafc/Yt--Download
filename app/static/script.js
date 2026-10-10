document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('url-input');
    const formatSelect = document.getElementById('format-select');
    const qualitySelect = document.getElementById('quality-select');
    const savePathInput = document.getElementById('save-path');
    const useDefaultsCheckbox = document.getElementById('use-defaults');
    const saveDefaultsBtn = document.getElementById('save-defaults-btn');
    const downloadBtn = document.getElementById('download-btn');
    const queueContainer = document.getElementById('queue-container');
    const clearCompletedBtn = document.getElementById('clear-completed-btn');

    // Update quality options based on format
    formatSelect.addEventListener('change', () => {
        if (formatSelect.value.startsWith('audio')) {
            qualitySelect.innerHTML = '<option value="best">Best Audio</option>';
            qualitySelect.disabled = true;
        } else {
            qualitySelect.innerHTML = `
                <option value="best">Best Available</option>
                <option value="2160p">2160p (4K)</option>
                <option value="1440p">1440p (2K)</option>
                <option value="1080p">1080p</option>
                <option value="720p">720p</option>
                <option value="480p">480p</option>
                <option value="360p">360p</option>
            `;
            qualitySelect.disabled = false;
        }
    });

    // Initial setup if format is audio from settings
    if (window.INITIAL_SETTINGS.format_type && window.INITIAL_SETTINGS.format_type.startsWith('audio')) {
        formatSelect.value = window.INITIAL_SETTINGS.format_type;
        formatSelect.dispatchEvent(new Event('change'));
    } else {
        formatSelect.value = window.INITIAL_SETTINGS.format_type || 'video';
        qualitySelect.value = window.INITIAL_SETTINGS.quality || 'best';
    }

    // Toggle default settings group
    function updateSettingsState() {
        if (useDefaultsCheckbox.checked) {
            formatSelect.disabled = true;
            qualitySelect.disabled = true;
            savePathInput.disabled = true;
        } else {
            formatSelect.disabled = false;
            qualitySelect.disabled = formatSelect.value.startsWith('audio');
            savePathInput.disabled = false;
        }
    }
    useDefaultsCheckbox.addEventListener('change', updateSettingsState);
    updateSettingsState();

    // Save Defaults
    saveDefaultsBtn.addEventListener('click', async () => {
        const settings = {
            use_defaults: useDefaultsCheckbox.checked,
            format_type: formatSelect.value,
            quality: qualitySelect.value,
            save_path: savePathInput.value
        };
        try {
            await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            alert('Settings saved as default!');
        } catch (e) {
            alert('Failed to save settings.');
        }
    });

    // Add Download
    downloadBtn.addEventListener('click', async () => {
        const text = urlInput.value.trim();
        if (!text) {
            alert('Please enter at least one URL.');
            return;
        }
        
        const urls = text.split('\n').map(u => u.trim()).filter(u => u);
        const data = {
            urls,
            format_type: formatSelect.value,
            quality: qualitySelect.value,
            save_path: savePathInput.value
        };

        downloadBtn.disabled = true;
        downloadBtn.textContent = 'Adding...';

        try {
            const res = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await res.json();
            if (result.error) {
                alert(result.error);
            } else {
                urlInput.value = '';
                fetchQueue();
            }
        } catch (e) {
            alert('Failed to add downloads.');
        }

        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Download';
    });

    // Clear completed
    clearCompletedBtn.addEventListener('click', async () => {
        await fetch('/api/queue/clear', { method: 'POST' });
        fetchQueue();
    });

    // Remove specific job
    window.removeJob = async (jobId) => {
        await fetch(`/api/queue/${jobId}`, { method: 'DELETE' });
        fetchQueue();
    };

    // Render queue
    function escapeHTML(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function renderQueue(jobs) {
        if (jobs.length === 0) {
            queueContainer.innerHTML = '<p style="color: var(--text-muted); text-align: center;">Queue is empty.</p>';
            return;
        }

        queueContainer.innerHTML = jobs.map(job => {
            const isDone = job.status === 'completed' || job.status === 'failed';
            const safeTitle = escapeHTML(job.filename || job.url);
            const safeStatus = escapeHTML(job.status);
            const safeError = job.error ? escapeHTML(job.error) : '';
            return `
                <div class="queue-item">
                    <div class="queue-item-header">
                        <div class="queue-item-title">${safeTitle}</div>
                        <div class="queue-item-status status-${safeStatus}">${safeStatus}</div>
                    </div>
                    ${job.status === 'downloading' ? `
                        <div class="queue-item-details">
                            <span>${escapeHTML(job.progress)}%</span>
                            <span>${escapeHTML(job.speed)}</span>
                            <span>ETA: ${escapeHTML(job.eta)}</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" style="width: ${escapeHTML(job.progress)}%"></div>
                        </div>
                    ` : ''}
                    ${safeError ? `<div style="color: var(--danger-color); font-size: 0.85rem; margin-top: 0.5rem;">${safeError}</div>` : ''}
                    <div class="queue-item-actions">
                        ${isDone ? `<button class="btn-secondary btn-small" onclick="removeJob('${escapeHTML(job.id)}')">Remove</button>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    // Polling queue
    async function fetchQueue() {
        try {
            const res = await fetch('/api/queue');
            const jobs = await res.json();
            renderQueue(jobs);
        } catch (e) {
            console.error('Failed to fetch queue');
        }
    }

    // Quit application
    document.getElementById('quit-btn').addEventListener('click', async () => {
        if (confirm('Are you sure you want to quit the application? Any active downloads will be interrupted.')) {
            try {
                await fetch('/api/shutdown', { method: 'POST' });
            } catch (e) {
                // Ignore errors since server is dying
            }
            document.body.innerHTML = '<div style="display:flex; justify-content:center; align-items:center; height:100vh; flex-direction:column; font-family:sans-serif;"><h1>App Shut Down</h1><p>You can now safely close this browser tab.</p></div>';
            setTimeout(() => window.close(), 1000);
        }
    });

    fetchQueue();
    setInterval(fetchQueue, 1500);
});
