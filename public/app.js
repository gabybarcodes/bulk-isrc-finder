// ========================================
// BULK ISRC FINDER - Label Finder Edition
// Version: 7-columns (SONG, ARTIST, ISRC, RELEASE DATE, LABEL(S), DISTRIBUTOR, STATUS)
// Last Updated: 2026-05-05 19:00 UTC
// ========================================

// DOM Elements
const songsInput = document.getElementById('songsInput');
const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('clearBtn');
const trackCount = document.getElementById('trackCount');
const awaitingMessage = document.getElementById('awaitingMessage');
const resultsContainer = document.getElementById('resultsContainer');
const resultsTable = document.getElementById('resultsTable');
const progressBarContainer = document.getElementById('progressBarContainer');
const progressBarFill = document.getElementById('progressBarFill');
const progressText = document.getElementById('progressText');
const exportCsvBtn = document.getElementById('exportCsvBtn');

let currentResults = [];

// Event Listeners
searchBtn.addEventListener('click', performBulkSearch);
clearBtn.addEventListener('click', clearInput);
exportCsvBtn.addEventListener('click', exportToCSV);
songsInput.addEventListener('input', updateTrackCount);

// Update track count
function updateTrackCount() {
    const songs = parseSongsInput(songsInput.value);
    trackCount.textContent = songs.length;
}

// Perform bulk search
async function performBulkSearch() {
    const input = songsInput.value.trim();

    if (!input) {
        alert('Please enter at least one song');
        return;
    }

    const songs = parseSongsInput(input);

    if (songs.length === 0) {
        alert('No valid songs found. Use format: "Song Title - Artist Name"');
        return;
    }

    awaitingMessage.style.display = 'none';
    resultsContainer.style.display = 'flex';
    resultsTable.innerHTML = '';
    currentResults = [];

    progressBarContainer.style.display = 'block';
    progressBarFill.style.width = '0%';
    progressBarFill.classList.remove('progress-bar-done');
    progressText.textContent = `0 / ${songs.length}`;

    searchBtn.disabled = true;
    searchBtn.textContent = 'Suchen...';

    initResultsTable();

    let foundCount = 0;

    for (let i = 0; i < songs.length; i++) {
        const song = songs[i];
        let result;

        try {
            const response = await fetch('/api/search-single', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ song })
            });
            result = response.ok
                ? await response.json()
                : { input: `${song.title} - ${song.artist}`, found: false, error: 'Request failed' };
        } catch (e) {
            result = { input: `${song.title} - ${song.artist}`, found: false, error: e.message };
        }

        currentResults.push(result);
        if (result.found) foundCount++;
        appendResultRow(result);

        const pct = Math.round(((i + 1) / songs.length) * 100);
        progressBarFill.style.width = `${pct}%`;
        progressText.textContent = `${i + 1} / ${songs.length}`;
    }

    progressBarFill.classList.add('progress-bar-done');
    progressText.textContent = `Gefunden: ${foundCount}/${songs.length} (${Math.round((foundCount / songs.length) * 100)}%)`;

    searchBtn.disabled = false;
    searchBtn.textContent = 'Suchen';
}

function initResultsTable() {
    resultsTable.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>SONG</th>
                    <th>ARTIST</th>
                    <th>ISRC</th>
                    <th>RELEASE DATE</th>
                    <th>LABEL(S)</th>
                    <th>DISTRIBUTOR</th>
                    <th>STATUS</th>
                </tr>
            </thead>
            <tbody id="resultsBody"></tbody>
        </table>`;
}

function appendResultRow(result) {
    const tbody = document.getElementById('resultsBody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td data-label="Song">${escapeHtml(result.title || 'N/A')}</td>
        <td data-label="Artist">${escapeHtml(result.artist || 'N/A')}</td>
        <td class="isrc-cell" data-label="ISRC">${result.isrc ? escapeHtml(result.isrc) : '—'}</td>
        <td data-label="Release Date">${result.releaseDate ? escapeHtml(result.releaseDate) : '—'}</td>
        <td data-label="Label(s)">${result.labels ? escapeHtml(result.labels) : '—'}</td>
        <td class="distributor-cell" data-label="Distributor">${result.distributor ? escapeHtml(result.distributor) : '—'}</td>
        <td><span class="status-badge ${result.found ? 'status-success' : 'status-error'}">${result.found ? '✓' : '✗'}</span></td>`;
    tbody.appendChild(tr);
}

// Parse songs from input
function parseSongsInput(input) {
    return input
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => {
            const parts = line.split(' - ');
            if (parts.length >= 2) {
                return {
                    title: parts[0].trim(),
                    artist: parts.slice(1).join(' - ').trim()
                };
            }
            return null;
        })
        .filter(song => song !== null);
}

// Clear input
function clearInput() {
    songsInput.value = '';
    trackCount.textContent = '0';
    resultsContainer.style.display = 'none';
    awaitingMessage.style.display = 'flex';
    progressBarContainer.style.display = 'none';
    progressBarFill.style.width = '0%';
    currentResults = [];
}

// Export to CSV
function exportToCSV() {
    console.log('Export CSV clicked, results:', currentResults);
    
    if (!currentResults || currentResults.length === 0) {
        alert('No results to export. Please search first.');
        return;
    }

    const headers = ['Song', 'Artist', 'ISRC', 'Release Date', 'Label(s)', 'Distributor', 'Status'];
    const rows = currentResults.map(result => [
        result.title || '',
        result.artist || '',
        result.isrc || '',
        result.releaseDate || '',
        result.labels || '',
        result.distributor || '',
        result.found ? 'Found' : 'Not Found'
    ]);

    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
        csv += row.map(cell => `"${cell}"`).join(',') + '\n';
    });

    downloadFile(csv, `isrc-results-${new Date().toISOString().split('T')[0]}.csv`, 'text/csv');
    console.log('CSV export completed');
}

// Download file helper
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Escape HTML special characters
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// On load - check server connection
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status !== 'ok') {
            progressText.textContent = '⚠️ Server error';
        }
    } catch (error) {
        progressText.textContent = '⚠️ Could not connect to server';
    }
});
