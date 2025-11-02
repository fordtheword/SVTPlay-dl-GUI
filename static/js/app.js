// API Base URL
const API_BASE = window.location.origin;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadDownloads();
    loadFiles();

    // Set up event listeners
    document.getElementById('downloadForm').addEventListener('submit', handleDownload);
    document.getElementById('checkInfoBtn').addEventListener('click', checkInfo);
    document.getElementById('refreshBtn').addEventListener('click', loadDownloads);
    document.getElementById('refreshFilesBtn').addEventListener('click', loadFiles);

    // Auto-refresh downloads every 5 seconds
    setInterval(loadDownloads, 5000);
});

// Show notification
function showNotification(message, type = 'info') {
    const toast = new bootstrap.Toast(document.getElementById('notificationToast'));
    const toastBody = document.getElementById('toastMessage');
    toastBody.textContent = message;
    toastBody.className = `toast-body bg-${type} text-white`;
    toast.show();
}

// Handle download form submission
async function handleDownload(event) {
    event.preventDefault();

    const url = document.getElementById('urlInput').value.trim();
    const downloadType = document.querySelector('input[name="downloadType"]:checked').value;
    const quality = document.getElementById('qualitySelect').value;
    const subtitle = document.getElementById('subtitleCheck').checked;

    if (!url) {
        showNotification('Vänligen ange en URL', 'warning');
        return;
    }

    const options = {
        quality: quality,
        subtitle: subtitle
    };

    try {
        const endpoint = downloadType === 'season' ? '/api/download/season' : '/api/download';

        const response = await fetch(API_BASE + endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, options })
        });

        const result = await response.json();

        if (result.success) {
            showNotification(
                downloadType === 'season'
                    ? 'Säsongsnedladdning startad!'
                    : 'Nedladdning startad!',
                'success'
            );
            document.getElementById('urlInput').value = '';
            document.getElementById('infoCard').style.display = 'none';
            loadDownloads();
        } else {
            showNotification('Fel: ' + result.error, 'danger');
        }
    } catch (error) {
        showNotification('Fel vid kommunikation med servern: ' + error.message, 'danger');
    }
}

// Check video info
async function checkInfo() {
    const url = document.getElementById('urlInput').value.trim();

    if (!url) {
        showNotification('Vänligen ange en URL', 'warning');
        return;
    }

    try {
        // First try to list episodes
        const episodesResponse = await fetch(API_BASE + '/api/episodes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const episodesResult = await episodesResponse.json();

        const infoCard = document.getElementById('infoCard');
        const infoContent = document.getElementById('infoContent');

        if (episodesResult.success && episodesResult.episodes && episodesResult.episodes.length > 0) {
            // Show episodes
            let html = `
                <div class="alert alert-info">
                    <strong>Serie hittad!</strong>
                    ${episodesResult.count} avsnitt tillgängliga
                </div>
                <div class="list-group" style="max-height: 300px; overflow-y: auto;">
            `;

            episodesResult.episodes.forEach((episode, index) => {
                html += `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">Avsnitt ${index + 1}</h6>
                        </div>
                        <small class="text-muted">${episode}</small>
                    </div>
                `;
            });

            html += '</div>';
            infoContent.innerHTML = html;
            infoCard.style.display = 'block';
            showNotification('Information hämtad!', 'success');
        } else {
            // Single video
            infoContent.innerHTML = `
                <div class="alert alert-info">
                    URL verifierad! Klicka på "Starta nedladdning" för att börja.
                </div>
            `;
            infoCard.style.display = 'block';
            showNotification('URL verifierad!', 'success');
        }
    } catch (error) {
        showNotification('Kunde inte hämta information: ' + error.message, 'danger');
    }
}

// Load downloads
async function loadDownloads() {
    try {
        const response = await fetch(API_BASE + '/api/downloads');
        const result = await response.json();

        if (result.success) {
            displayDownloads(result.downloads);
        }
    } catch (error) {
        console.error('Error loading downloads:', error);
    }
}

// Display downloads
function displayDownloads(downloads) {
    const downloadsList = document.getElementById('downloadsList');

    if (downloads.length === 0) {
        downloadsList.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                <p class="mt-2">Inga nedladdningar än</p>
            </div>
        `;
        return;
    }

    // Sort by started_at, newest first
    downloads.sort((a, b) => new Date(b.started_at) - new Date(a.started_at));

    let html = '';
    downloads.forEach(download => {
        const statusClass = `status-${download.status}`;
        const statusText = getStatusText(download.status);
        const typeIcon = download.type === 'season'
            ? '<i class="bi bi-collection-play"></i>'
            : '<i class="bi bi-file-play"></i>';

        html += `
            <div class="download-item">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <strong>${typeIcon} ${truncateUrl(download.url)}</strong>
                        <br>
                        <small class="text-muted">Startad: ${formatDate(download.started_at)}</small>
                    </div>
                    <span class="download-status ${statusClass}">${statusText}</span>
                </div>

                ${download.status === 'downloading' ? `
                    <div class="progress mb-2">
                        <div class="progress-bar progress-bar-striped progress-bar-animated"
                             role="progressbar" style="width: 100%">
                            Laddar ner...
                        </div>
                    </div>
                ` : ''}

                ${download.error ? `
                    <div class="alert alert-danger mb-0 mt-2">
                        <small><strong>Fel:</strong> ${download.error}</small>
                    </div>
                ` : ''}

                <small class="text-muted">${download.message}</small>
            </div>
        `;
    });

    downloadsList.innerHTML = html;
}

// Load files
async function loadFiles() {
    try {
        const response = await fetch(API_BASE + '/api/downloads/files');
        const result = await response.json();

        if (result.success) {
            displayFiles(result.files);
        }
    } catch (error) {
        console.error('Error loading files:', error);
    }
}

// Display files
function displayFiles(files) {
    const filesList = document.getElementById('filesList');

    if (files.length === 0) {
        filesList.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-folder-x" style="font-size: 3rem;"></i>
                <p class="mt-2">Inga filer än</p>
            </div>
        `;
        return;
    }

    // Sort by modified date, newest first
    files.sort((a, b) => b.modified - a.modified);

    let html = '';
    files.forEach(file => {
        html += `
            <div class="file-item">
                <span class="file-name">
                    <i class="bi bi-file-earmark-play"></i>
                    ${file.name}
                </span>
                <span class="file-size">${formatFileSize(file.size)}</span>
                <a href="/downloads/${encodeURIComponent(file.name)}"
                   class="btn btn-sm btn-outline-primary"
                   download>
                    <i class="bi bi-download"></i>
                </a>
            </div>
        `;
    });

    filesList.innerHTML = html;
}

// Helper functions
function getStatusText(status) {
    const statusMap = {
        'queued': 'I kö',
        'downloading': 'Laddar ner',
        'completed': 'Klar',
        'failed': 'Misslyckades'
    };
    return statusMap[status] || status;
}

function truncateUrl(url, maxLength = 50) {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('sv-SE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
