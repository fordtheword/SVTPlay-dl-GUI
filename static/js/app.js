// API Base URL
const API_BASE = window.location.origin;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadDownloads();
    loadFiles();
    loadProfiles();

    // Set up event listeners
    document.getElementById('downloadForm').addEventListener('submit', handleDownload);
    document.getElementById('checkInfoBtn').addEventListener('click', checkInfo);
    document.getElementById('refreshBtn').addEventListener('click', loadDownloads);
    document.getElementById('refreshFilesBtn').addEventListener('click', loadFiles);
    document.getElementById('saveProfileBtn').addEventListener('click', saveProfile);
    document.getElementById('deleteProfileBtn').addEventListener('click', deleteProfile);
    document.getElementById('profileSelect').addEventListener('change', loadProfileData);
    document.getElementById('upgradeBtn').addEventListener('click', upgradeSystem);

    // Load system info
    loadSystemInfo();

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
    const downloadDir = document.getElementById('downloadDir').value.trim();
    const token = document.getElementById('tokenInput').value.trim();
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

    // Add download directory if specified
    if (downloadDir) {
        options.download_dir = downloadDir;
    }

    // Add token if specified
    if (token) {
        options.token = token;
    }

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
            // Don't clear fields if user wants to keep them for repeated downloads
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

                ${download.episodes && Object.keys(download.episodes).length > 0 ? `
                    <div class="mt-3">
                        <details ${download.status === 'downloading' ? 'open' : ''}>
                            <summary style="cursor: pointer;" class="mb-2">
                                <i class="bi bi-list-ol"></i>
                                <strong>Avsnitt (${download.total_episodes || Object.keys(download.episodes).length})</strong>
                                ${download.total_episodes ? `
                                    - ${download.completed_episodes || 0} nedladdade,
                                    ${download.skipped_episodes || 0} hoppade över
                                ` : ''}
                            </summary>
                            <div class="episode-list" style="max-height: 300px; overflow-y: auto;">
                                ${Object.values(download.episodes)
                                    .sort((a, b) => a.number - b.number)
                                    .map(ep => {
                                        let icon, className, statusText;
                                        if (ep.status === 'completed') {
                                            icon = '✅';
                                            className = 'text-success';
                                            statusText = 'Nedladdad';
                                        } else if (ep.status === 'skipped') {
                                            icon = '⏭️';
                                            className = 'text-info';
                                            statusText = 'Hoppade över (fanns redan)';
                                        } else if (ep.status === 'downloading') {
                                            icon = '⏳';
                                            className = 'text-warning';
                                            statusText = 'Laddar ner...';
                                        } else {
                                            icon = '⏸️';
                                            className = 'text-muted';
                                            statusText = 'Väntar...';
                                        }

                                        return `
                                            <div class="d-flex align-items-center py-1 px-2 border-bottom" style="font-size: 0.9rem;">
                                                <span class="me-2">${icon}</span>
                                                <span class="flex-grow-1">
                                                    <strong>Avsnitt ${ep.number}</strong>
                                                    ${ep.filename ? `<br><small class="text-muted">${ep.filename.substring(0, 50)}${ep.filename.length > 50 ? '...' : ''}</small>` : ''}
                                                </span>
                                                <small class="${className}">${statusText}</small>
                                            </div>
                                        `;
                                    }).join('')}
                            </div>
                        </details>
                    </div>
                ` : ''}
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

// Profile Management Functions

// Load all profiles
async function loadProfiles() {
    try {
        const response = await fetch(API_BASE + '/api/profiles');
        const result = await response.json();

        if (result.success) {
            const profileSelect = document.getElementById('profileSelect');

            // Clear existing options except the first one
            profileSelect.innerHTML = '<option value="">-- Välj en sparad serie eller skapa ny --</option>';

            // Add profiles to dropdown
            result.profiles.forEach(profile => {
                const option = document.createElement('option');
                option.value = profile.id;
                option.textContent = profile.name;
                profileSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading profiles:', error);
    }
}

// Load profile data when selected
function loadProfileData() {
    const profileSelect = document.getElementById('profileSelect');
    const selectedProfileId = profileSelect.value;
    const deleteBtn = document.getElementById('deleteProfileBtn');

    if (!selectedProfileId) {
        // Clear form when no profile is selected
        deleteBtn.disabled = true;
        return;
    }

    // Enable delete button
    deleteBtn.disabled = false;

    // Fetch and load profile data
    fetch(API_BASE + '/api/profiles/' + selectedProfileId)
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                const profile = result.profile;

                // Populate form fields
                document.getElementById('seriesName').value = profile.name;
                document.getElementById('urlInput').value = profile.url;
                document.getElementById('downloadDir').value = profile.download_dir;
                document.getElementById('qualitySelect').value = profile.quality;
                document.getElementById('subtitleCheck').checked = profile.subtitle;

                // Set token if available
                if (profile.token) {
                    document.getElementById('tokenInput').value = profile.token;
                } else {
                    document.getElementById('tokenInput').value = '';
                }

                // Set download type
                if (profile.download_type === 'season') {
                    document.getElementById('typeSeason').checked = true;
                } else {
                    document.getElementById('typeSingle').checked = true;
                }

                showNotification('Profil "' + profile.name + '" laddad!', 'success');
            }
        })
        .catch(error => {
            showNotification('Fel vid laddning av profil: ' + error.message, 'danger');
        });
}

// Save profile
async function saveProfile() {
    const name = document.getElementById('seriesName').value.trim();
    const url = document.getElementById('urlInput').value.trim();
    const downloadDir = document.getElementById('downloadDir').value.trim();
    const token = document.getElementById('tokenInput').value.trim();
    const quality = document.getElementById('qualitySelect').value;
    const subtitle = document.getElementById('subtitleCheck').checked;
    const downloadType = document.querySelector('input[name="downloadType"]:checked').value;

    if (!name) {
        showNotification('Vänligen ange ett serie-namn för att spara profilen', 'warning');
        return;
    }

    if (!url) {
        showNotification('Vänligen ange en URL', 'warning');
        return;
    }

    if (!downloadDir) {
        showNotification('Vänligen ange en nedladdningsmapp', 'warning');
        return;
    }

    const profileData = {
        name: name,
        url: url,
        download_dir: downloadDir,
        quality: quality,
        subtitle: subtitle,
        download_type: downloadType
    };

    // Add token if specified
    if (token) {
        profileData.token = token;
    }

    try {
        const response = await fetch(API_BASE + '/api/profiles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Profil "' + name + '" sparad!', 'success');
            loadProfiles(); // Reload profiles dropdown
        } else {
            showNotification('Fel: ' + result.error, 'danger');
        }
    } catch (error) {
        showNotification('Fel vid sparning av profil: ' + error.message, 'danger');
    }
}

// Delete profile
async function deleteProfile() {
    const profileSelect = document.getElementById('profileSelect');
    const selectedProfileId = profileSelect.value;

    if (!selectedProfileId) {
        showNotification('Ingen profil vald', 'warning');
        return;
    }

    const selectedOption = profileSelect.options[profileSelect.selectedIndex];
    const profileName = selectedOption.textContent;

    if (!confirm('Är du säker på att du vill ta bort profilen "' + profileName + '"?')) {
        return;
    }

    try {
        const response = await fetch(API_BASE + '/api/profiles/' + selectedProfileId, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Profil "' + profileName + '" borttagen!', 'success');

            // Clear form
            document.getElementById('seriesName').value = '';
            document.getElementById('urlInput').value = '';
            document.getElementById('downloadDir').value = '';
            document.getElementById('profileSelect').value = '';
            document.getElementById('deleteProfileBtn').disabled = true;

            loadProfiles(); // Reload profiles dropdown
        } else {
            showNotification('Fel: ' + result.error, 'danger');
        }
    } catch (error) {
        showNotification('Fel vid borttagning av profil: ' + error.message, 'danger');
    }
}

// System Management Functions

// Load system information
async function loadSystemInfo() {
    try {
        const response = await fetch(API_BASE + '/api/system/info');
        const result = await response.json();

        if (result.success) {
            const info = result.info;
            const systemInfoDiv = document.getElementById('systemInfo');

            systemInfoDiv.innerHTML = `
                <div class="row small">
                    <div class="col-md-6">
                        <strong>Python:</strong> ${info.python_version}<br>
                        <strong>svtplay-dl:</strong> ${info.svtplay_dl_version}
                    </div>
                    <div class="col-md-6">
                        <strong>Branch:</strong> ${info.git_branch}<br>
                        <strong>Commit:</strong> ${info.latest_commit}
                    </div>
                </div>
            `;
        } else {
            document.getElementById('systemInfo').innerHTML =
                '<small class="text-danger">Kunde inte ladda systeminformation</small>';
        }
    } catch (error) {
        console.error('Error loading system info:', error);
        document.getElementById('systemInfo').innerHTML =
            '<small class="text-danger">Fel: ' + error.message + '</small>';
    }
}

// Upgrade system
async function upgradeSystem() {
    const upgradeBtn = document.getElementById('upgradeBtn');
    const upgradeOutput = document.getElementById('upgradeOutput');
    const upgradeAlert = document.getElementById('upgradeAlert');
    const upgradeDetails = document.getElementById('upgradeDetails');

    if (!confirm('Är du säker på att du vill uppgradera systemet?\n\nDetta kommer att:\n- Hämta senaste koden från GitHub\n- Uppgradera alla Python-paket\n\nServern behöver startas om efter uppgraderingen.')) {
        return;
    }

    // Disable button and show loading
    upgradeBtn.disabled = true;
    upgradeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Uppgraderar...';

    upgradeOutput.style.display = 'block';
    upgradeAlert.className = 'alert alert-info';
    upgradeAlert.textContent = 'Uppgradering pågår... Detta kan ta några minuter.';
    upgradeDetails.textContent = '';

    try {
        const response = await fetch(API_BASE + '/api/system/upgrade', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            upgradeAlert.className = 'alert alert-success';
            upgradeAlert.textContent = result.message;

            let details = '=== Git Output ===\n' + result.git_output + '\n\n';
            if (result.pip_output) {
                details += '=== Pip Output ===\n' + result.pip_output;
            }
            upgradeDetails.textContent = details;

            if (result.restart_required) {
                upgradeAlert.textContent += '\n\nVIKTIGT: Starta om servern för att använda de nya uppdateringarna!';
                showNotification('Uppgradering klar! Starta om servern.', 'warning');
            } else {
                showNotification('Systemet är redan uppdaterat!', 'success');
            }

            // Reload system info
            setTimeout(loadSystemInfo, 2000);
        } else {
            upgradeAlert.className = 'alert alert-danger';
            upgradeAlert.textContent = 'Uppgradering misslyckades: ' + result.error;

            let details = '';
            if (result.git_output) {
                details += '=== Git Output ===\n' + result.git_output + '\n\n';
            }
            if (result.error) {
                details += '=== Error ===\n' + result.error;
            }
            upgradeDetails.textContent = details;

            showNotification('Uppgradering misslyckades!', 'danger');
        }
    } catch (error) {
        upgradeAlert.className = 'alert alert-danger';
        upgradeAlert.textContent = 'Fel vid uppgradering: ' + error.message;
        upgradeDetails.textContent = error.stack || error.message;
        showNotification('Fel vid uppgradering: ' + error.message, 'danger');
    } finally {
        // Re-enable button
        upgradeBtn.disabled = false;
        upgradeBtn.innerHTML = '<i class="bi bi-arrow-up-circle"></i> Uppgradera system';
    }
}

// ===== Folder Browser =====

let currentBrowserPath = '';
let folderBrowserModal = null;

// Initialize folder browser modal
document.addEventListener('DOMContentLoaded', function() {
    folderBrowserModal = new bootstrap.Modal(document.getElementById('folderBrowserModal'));

    // Browse button click
    document.getElementById('browseFolderBtn').addEventListener('click', openFolderBrowser);

    // Refresh button click
    document.getElementById('refreshFoldersBtn').addEventListener('click', function() {
        loadFolders(currentBrowserPath || undefined);
    });

    // Select folder button click
    document.getElementById('selectFolderBtn').addEventListener('click', function() {
        document.getElementById('downloadDir').value = currentBrowserPath;
        folderBrowserModal.hide();
        showNotification('Mapp vald: ' + currentBrowserPath, 'success');
    });
});

async function openFolderBrowser() {
    // Get current path from input or use default
    const currentInput = document.getElementById('downloadDir').value.trim();
    const startPath = currentInput || undefined;

    // Show modal
    folderBrowserModal.show();

    // Load folders
    await loadFolders(startPath);
}

async function loadFolders(path) {
    const folderList = document.getElementById('folderList');
    const currentPathInput = document.getElementById('currentPathInput');

    try {
        // Show loading
        folderList.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Laddar...</span>
                </div>
            </div>
        `;

        const response = await fetch('/api/browse-folders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ path: path })
        });

        const data = await response.json();

        if (data.success) {
            currentBrowserPath = data.current_path;
            currentPathInput.value = currentBrowserPath;

            // Display folders
            if (data.items.length === 0) {
                folderList.innerHTML = '<div class="list-group-item text-muted">Inga undermappar hittades</div>';
            } else {
                folderList.innerHTML = '';
                data.items.forEach(item => {
                    const itemEl = document.createElement('a');
                    itemEl.href = '#';
                    itemEl.className = 'list-group-item list-group-item-action d-flex align-items-center';

                    if (item.is_parent) {
                        itemEl.innerHTML = `
                            <i class="bi bi-arrow-up-circle me-2"></i>
                            <span>${item.name}</span>
                            <small class="text-muted ms-auto">Överordnad mapp</small>
                        `;
                    } else {
                        itemEl.innerHTML = `
                            <i class="bi bi-folder me-2"></i>
                            <span>${item.name}</span>
                        `;
                    }

                    itemEl.addEventListener('click', function(e) {
                        e.preventDefault();
                        loadFolders(item.path);
                    });

                    folderList.appendChild(itemEl);
                });
            }
        } else {
            folderList.innerHTML = `<div class="list-group-item list-group-item-danger">Fel: ${data.error}</div>`;
        }
    } catch (error) {
        folderList.innerHTML = `<div class="list-group-item list-group-item-danger">Fel vid laddning: ${error.message}</div>`;
    }
}
