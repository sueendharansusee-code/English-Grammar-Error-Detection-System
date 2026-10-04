/**
 * English Grammar Error Detection System - Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const textInput = document.getElementById('text-input');
    const wordCountSpan = document.getElementById('stat-word-count');
    const charCountSpan = document.getElementById('stat-char-count');
    
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnClear = document.getElementById('btn-clear');
    const btnCopyCorrected = document.getElementById('btn-copy-corrected');
    const samplesContainer = document.getElementById('samples-container');
    
    const placeholderState = document.getElementById('placeholder-state');
    const resultsDashboard = document.getElementById('results-dashboard');
    
    const scoreNum = document.getElementById('score-num');
    const scoreStatus = document.getElementById('score-status');
    const scoreDialFill = document.getElementById('score-dial-fill');
    
    const metricErrors = document.getElementById('metric-errors');
    const metricCorrect = document.getElementById('metric-correct');
    const metricSuggestions = document.getElementById('metric-suggestions');
    
    const highlightView = document.getElementById('highlight-view');
    const errorsList = document.getElementById('errors-list');
    const issueCountSpan = document.getElementById('issue-count');
    const engineBadge = document.getElementById('engine-badge');
    const filterChipsContainer = document.getElementById('filter-chips');
    
    const btnOpenHistory = document.getElementById('btn-open-history');
    const btnCloseHistory = document.getElementById('btn-close-history');
    const btnClearHistory = document.getElementById('btn-clear-history');
    const historyModal = document.getElementById('history-modal');
    const historyList = document.getElementById('history-list');
    const historyBadge = document.getElementById('history-badge');

    // State Variables
    let currentAnalysisResult = null;
    let activeFilter = 'all';

    // --- Init ---
    fetchSamples();
    fetchHistoryCount();
    updateWordAndCharCount();

    // --- Event Listeners ---
    textInput.addEventListener('input', updateWordAndCharCount);

    btnClear.addEventListener('click', () => {
        textInput.value = '';
        updateWordAndCharCount();
        resetResultsView();
        showToast('Text cleared.');
    });

    btnAnalyze.addEventListener('click', () => {
        const text = textInput.value.strip ? textInput.value.strip() : textInput.value.trim();
        if (!text) {
            showToast('Please enter or paste English text to check.');
            return;
        }
        analyzeText(text);
    });

    btnCopyCorrected.addEventListener('click', () => {
        if (!currentAnalysisResult || !currentAnalysisResult.corrected_text) return;
        navigator.clipboard.writeText(currentAnalysisResult.corrected_text)
            .then(() => showToast('Corrected text copied to clipboard!'))
            .catch(() => showToast('Failed to copy text.'));
    });

    btnOpenHistory.addEventListener('click', () => {
        loadHistoryModal();
        historyModal.classList.remove('hidden');
    });

    btnCloseHistory.addEventListener('click', () => {
        historyModal.classList.add('hidden');
    });

    btnClearHistory.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear all history records?')) return;
        try {
            const res = await fetch('/api/history', { method: 'DELETE' });
            const data = await res.json();
            if (data.status === 'success') {
                showToast('History cleared.');
                loadHistoryModal();
                fetchHistoryCount();
            }
        } catch (err) {
            showToast('Failed to clear history.');
        }
    });

    filterChipsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('chip')) {
            document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            e.target.classList.add('active');
            activeFilter = e.target.getAttribute('data-filter');
            renderIssuesList();
        }
    });

    // --- Helper Functions ---
    function updateWordAndCharCount() {
        const text = textInput.value;
        charCountSpan.textContent = text.length;
        const words = text.trim().split(/\s+/).filter(w => w.length > 0);
        wordCountSpan.textContent = words.length;
    }

    function resetResultsView() {
        placeholderState.classList.remove('hidden');
        resultsDashboard.classList.add('hidden');
        currentAnalysisResult = null;
    }

    function showToast(msg) {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<i class="fa-solid fa-circle-info"></i> <span>${msg}</span>`;
        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 3200);
    }

    async function fetchSamples() {
        try {
            const res = await fetch('/api/samples');
            const result = await res.json();
            if (result.status === 'success') {
                renderSampleButtons(result.data);
            }
        } catch (err) {
            console.error('Failed to load sample sentences', err);
        }
    }

    function renderSampleButtons(samples) {
        samplesContainer.innerHTML = '';
        samples.forEach(sample => {
            const pill = document.createElement('button');
            pill.className = 'sample-pill';
            pill.textContent = sample.title;
            pill.addEventListener('click', () => {
                textInput.value = sample.text;
                updateWordAndCharCount();
                analyzeText(sample.text);
            });
            samplesContainer.appendChild(pill);
        });
    }

    async function fetchHistoryCount() {
        try {
            const res = await fetch('/api/history');
            const result = await res.json();
            if (result.status === 'success') {
                historyBadge.textContent = result.data.length;
            }
        } catch (err) {
            console.error('Failed to fetch history count', err);
        }
    }

    async function analyzeText(text) {
        // Show loading state
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...`;

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const result = await response.json();
            if (result.status === 'success') {
                currentAnalysisResult = result.data;
                displayResults(currentAnalysisResult);
                fetchHistoryCount();
                showToast('Grammar analysis complete!');
            } else {
                showToast(result.message || 'Analysis failed.');
            }
        } catch (err) {
            showToast('Network or server error occurred.');
            console.error(err);
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> <span>Check Grammar</span>`;
        }
    }

    function displayResults(data) {
        placeholderState.classList.add('hidden');
        resultsDashboard.classList.remove('hidden');

        // Update Score Gauge
        const score = data.score;
        scoreNum.textContent = score;
        
        // Gauge stroke circumference for r=50 is 2 * pi * 50 = 314
        const circumference = 314;
        const strokeOffset = circumference - (circumference * score) / 100;
        scoreDialFill.style.strokeDashoffset = strokeOffset;

        if (score >= 90) {
            scoreDialFill.style.stroke = 'var(--success)';
            scoreStatus.textContent = 'Excellent Writing';
            scoreStatus.style.background = 'var(--success-light)';
            scoreStatus.style.color = 'var(--success)';
        } else if (score >= 70) {
            scoreDialFill.style.stroke = 'var(--warning)';
            scoreStatus.textContent = 'Good - Minor Issues';
            scoreStatus.style.background = 'var(--warning-light)';
            scoreStatus.style.color = 'var(--warning)';
        } else {
            scoreDialFill.style.stroke = 'var(--danger)';
            scoreStatus.textContent = 'Needs Revision';
            scoreStatus.style.background = 'var(--danger-light)';
            scoreStatus.style.color = 'var(--danger)';
        }

        // Update Stat Cards
        metricErrors.textContent = data.error_count;
        metricCorrect.textContent = `${data.correct_sentences}/${data.sentence_count}`;
        metricSuggestions.textContent = data.suggestions_count;
        engineBadge.innerHTML = `<i class="fa-solid fa-microchip"></i> ${data.engine_used}`;

        // Render Highlighted View
        renderHighlightedView(data.original_text, data.errors);

        // Render Issues Breakdown List
        issueCountSpan.textContent = data.error_count;
        renderIssuesList();
    }

    function renderHighlightedView(originalText, errors) {
        if (!errors || errors.length === 0) {
            highlightView.innerHTML = `<span style="color: var(--success); font-weight: 600;"><i class="fa-solid fa-circle-check"></i> Great job! No grammar or writing errors detected in this text.</span>`;
            return;
        }

        const sortedErrors = [...errors].sort((a, b) => a.start - b.start);
        let html = '';
        let lastIndex = 0;

        sortedErrors.forEach((err, idx) => {
            if (err.start >= lastIndex) {
                // Add plain text before error
                html += escapeHtml(originalText.substring(lastIndex, err.start));

                const errorTypeClass = getErrorClass(err.type);
                html += `<mark class="error-mark ${errorTypeClass}" data-index="${idx}" title="${escapeHtml(err.explanation)}">${escapeHtml(originalText.substring(err.start, err.end))}</mark>`;
                lastIndex = err.end;
            }
        });

        html += escapeHtml(originalText.substring(lastIndex));
        highlightView.innerHTML = html;
    }

    function renderIssuesList() {
        errorsList.innerHTML = '';
        if (!currentAnalysisResult || !currentAnalysisResult.errors) return;

        const errors = currentAnalysisResult.errors;
        const filtered = activeFilter === 'all'
            ? errors
            : errors.filter(e => e.type === activeFilter);

        if (filtered.length === 0) {
            errorsList.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 20px;">No issues found under category '${activeFilter}'.</div>`;
            return;
        }

        filtered.forEach((err, idx) => {
            const card = document.createElement('div');
            card.className = 'error-card-item';
            
            const badgeClass = getBadgeClass(err.type);
            
            card.innerHTML = `
                <div class="error-item-header">
                    <span class="error-badge ${badgeClass}">${escapeHtml(err.type)}</span>
                </div>
                <div class="error-item-body">
                    <div class="error-phrases">
                        <span class="orig-phrase">${escapeHtml(err.original)}</span>
                        <i class="fa-solid fa-arrow-right arrow-icon"></i>
                        <span class="rep-phrase">${escapeHtml(err.replacement)}</span>
                    </div>
                    <p class="error-explanation">${escapeHtml(err.explanation)}</p>
                </div>
            `;
            errorsList.appendChild(card);
        });
    }

    async function loadHistoryModal() {
        historyList.innerHTML = '<div style="text-align: center; padding: 20px;"><i class="fa-solid fa-spinner fa-spin"></i> Loading history...</div>';
        try {
            const res = await fetch('/api/history');
            const result = await res.json();
            if (result.status === 'success') {
                renderHistoryItems(result.data);
            }
        } catch (err) {
            historyList.innerHTML = '<div style="color: var(--danger); text-align: center; padding: 20px;">Failed to load history records.</div>';
        }
    }

    function renderHistoryItems(items) {
        historyList.innerHTML = '';
        if (!items || items.length === 0) {
            historyList.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 20px;">No previous analysis records found.</div>';
            return;
        }

        items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'history-item';
            itemDiv.innerHTML = `
                <div class="history-info">
                    <div class="history-text">${escapeHtml(item.original_text)}</div>
                    <div class="history-meta">
                        ${item.timestamp} | Score: <strong>${item.score}/100</strong> | Errors: ${item.error_count}
                    </div>
                </div>
                <button class="btn btn-outline btn-load-history" data-id="${item.id}">
                    <i class="fa-solid fa-folder-open"></i> Load
                </button>
            `;
            
            itemDiv.querySelector('.btn-load-history').addEventListener('click', async () => {
                const res = await fetch(`/api/history/${item.id}`);
                const data = await res.json();
                if (data.status === 'success') {
                    const record = data.data;
                    textInput.value = record.original_text;
                    updateWordAndCharCount();
                    currentAnalysisResult = {
                        original_text: record.original_text,
                        corrected_text: record.corrected_text,
                        score: record.score,
                        error_count: record.error_count,
                        correct_sentences: record.sentence_count - record.error_count,
                        suggestions_count: record.error_count,
                        word_count: record.word_count,
                        sentence_count: record.sentence_count,
                        engine_used: "SQLite Historical Entry",
                        errors: record.details
                    };
                    displayResults(currentAnalysisResult);
                    historyModal.classList.add('hidden');
                    showToast('History analysis report loaded!');
                }
            });

            historyList.appendChild(itemDiv);
        });
    }

    function getErrorClass(type) {
        switch (type) {
            case 'Subject-Verb Agreement': return 'mark-sva';
            case 'Spelling': return 'mark-spelling';
            case 'Missing Punctuation': return 'mark-punc';
            case 'Capitalization': return 'mark-cap';
            case 'Common Patterns': return 'mark-patterns';
            case 'Repeated Words': return 'mark-rep';
            default: return 'mark-patterns';
        }
    }

    function getBadgeClass(type) {
        switch (type) {
            case 'Subject-Verb Agreement': return 'badge-sva';
            case 'Spelling': return 'badge-spelling';
            case 'Missing Punctuation': return 'badge-punc';
            case 'Capitalization': return 'badge-cap';
            case 'Common Patterns': return 'badge-patterns';
            case 'Repeated Words': return 'badge-rep';
            default: return 'badge-patterns';
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
