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

    // Show results container
    awaitingMessage.style.display = 'none';
    resultsContainer.style.display = 'flex';
    resultsTable.innerHTML = '';
    progressText.textContent = 'Processing...';
    
    searchBtn.disabled = true;
    searchBtn.textContent = 'Searching...';

    try {
        const response = await fetch('/api/bulk-search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ songs, api: 'deezer' })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Search failed');
        }

        const data = await response.json();
        currentResults = data.results;
        displayResults(data.results);
    } catch (error) {
        progressText.textContent = `❌ Error: ${error.message}`;
        console.error('Search error:', error);
    } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = 'Search';
    }
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

// Display results in a table
function displayResults(results) {
    const html = `
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
            <tbody>
                ${results.map((result, index) => `
                    <tr>
                        <td>${escapeHtml(result.title || 'N/A')}</td>
                        <td>${escapeHtml(result.artist || 'N/A')}</td>
                        <td class="isrc-cell">${result.isrc ? escapeHtml(result.isrc) : '—'}</td>
                        <td>${result.releaseDate ? escapeHtml(result.releaseDate) : '—'}</td>
                        <td>${result.labels ? escapeHtml(result.labels) : '—'}</td>
                        <td>${result.distributor ? escapeHtml(result.distributor) : '—'}</td>
                        <td>
                            <span class="status-badge ${result.found ? 'status-success' : 'status-error'}">
                                ${result.found ? '✓' : '✗'}
                            </span>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    resultsTable.innerHTML = html;

    // Update progress
    const foundCount = results.filter(r => r.found).length;
    const totalCount = results.length;
    updateProgress(foundCount, totalCount);
}

// Update progress text
function updateProgress(found, total) {
    progressText.textContent = `Found: ${found}/${total} (${Math.round((found / total) * 100)}%)`;
}

// Clear input
function clearInput() {
    songsInput.value = '';
    trackCount.textContent = '0';
    resultsContainer.style.display = 'none';
    awaitingMessage.style.display = 'flex';
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
