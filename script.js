
let entries = [];          
let selectedMood = "radiant";
let editingId = null;      


const moodBtns = document.querySelectorAll('.mood-btn');
const entryTitle = document.getElementById('entryTitle');
const entryNote = document.getElementById('entryNote');
const saveBtn = document.getElementById('saveEntryBtn');
const historyDiv = document.getElementById('historyList');
const totalSpan = document.getElementById('totalCount');
const streakSpan = document.getElementById('streakCount');
const topMoodSpan = document.getElementById('topMood');
const themeToggle = document.getElementById('themeToggle');
const editIndicator = document.getElementById('editIndicator');
const exportBtn = document.getElementById('exportBtn');
const importBtn = document.getElementById('importBtn');
const importFileInput = document.getElementById('importFileInput');


function moodToValue(mood) {
    const map = { radiant: 4, calm: 3, tired: 2, stressed: 1 };
    return map[mood] || 2;
}


function updateMoodChart() {
    const ctx = document.getElementById('moodChart').getContext('2d');
    
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        last7Days.push(d.toISOString().split('T')[0]);
    }
   
    const dailyAvg = last7Days.map(day => {
        const dayEntries = entries.filter(e => e.date.split('T')[0] === day);
        if (dayEntries.length === 0) return null;
        const avg = dayEntries.reduce((sum, e) => sum + moodToValue(e.mood), 0) / dayEntries.length;
        return avg;
    });
    
    const labels = last7Days.map(d => d.slice(5));
    const data = dailyAvg.map(v => v !== null ? v : null);
    
    if (moodChart) {
        moodChart.data.datasets[0].data = data;
        moodChart.update();
    } else {
        moodChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'mood intensity',
                    data: data,
                    borderColor: '#e28d6c',
                    backgroundColor: 'rgba(226,141,108,0.1)',
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#c56f4e',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const val = ctx.raw;
                                if (val === null) return 'no entry';
                                if (val >= 3.5) return '✨ radiant';
                                if (val >= 2.5) return '🌸 calm';
                                if (val >= 1.5) return '🌙 tired';
                                return '⚡ stressed';
                            }
                        }
                    }
                },
                scales: {
                    y: { min: 0.5, max: 4.5, ticks: { stepSize: 1, callback: (val) => ['', 'stressed', 'tired', 'calm', 'radiant'][val] } }
                }
            }
        });
    }
}


function loadFromStorage() {
    const stored = localStorage.getItem('moodflow_entries');
    if (stored) {
        entries = JSON.parse(stored);
        entries.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else {
       
        entries = [{
            id: Date.now(),
            date: new Date().toISOString(),
            mood: "calm",
            title: "Welcome to MoodFlow",
            note: "Track your moods daily and see patterns. Your data stays private."
        }];
    }
    renderAll();
}

function saveToStorage() {
    localStorage.setItem('moodflow_entries', JSON.stringify(entries));
}


function calculateStreak() {
    if (entries.length === 0) return 0;
    const uniqueDays = new Set();
    entries.forEach(entry => {
        uniqueDays.add(entry.date.split('T')[0]);
    });
    const sortedDays = Array.from(uniqueDays).sort().reverse();
    if (sortedDays.length === 0) return 0;
    const todayStr = new Date().toISOString().split('T')[0];
    if (sortedDays[0] !== todayStr) return 0;
    let streak = 1;
    for (let i = 0; i < sortedDays.length - 1; i++) {
        const current = new Date(sortedDays[i]);
        const next = new Date(sortedDays[i + 1]);
        const diff = (current - next) / (1000 * 3600 * 24);
        if (diff === 1) streak++;
        else break;
    }
    return streak;
}


function getTopMood() {
    if (entries.length === 0) return "—";
    const moodCount = {};
    entries.forEach(e => { moodCount[e.mood] = (moodCount[e.mood] || 0) + 1; });
    let top = null, max = 0;
    for (let [mood, cnt] of Object.entries(moodCount)) {
        if (cnt > max) { max = cnt; top = mood; }
    }
    const moodEmojis = { radiant: "✨ Radiant", calm: "🌸 Calm", tired: "🌙 Tired", stressed: "⚡ Stressed" };
    return moodEmojis[top] || top;
}


function renderHistory() {
    if (!historyDiv) return;
    if (entries.length === 0) {
        historyDiv.innerHTML = `<div class="empty-msg">🌸 Add your first mood entry</div>`;
        return;
    }
    const recent = [...entries].sort((a,b) => new Date(b.date) - new Date(a.date)).slice(0, 12);
    historyDiv.innerHTML = recent.map(entry => {
        const dateObj = new Date(entry.date);
        const formatted = dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        let moodIcon = "";
        if (entry.mood === 'radiant') moodIcon = '✨';
        else if (entry.mood === 'calm') moodIcon = '🌸';
        else if (entry.mood === 'tired') moodIcon = '🌙';
        else moodIcon = '⚡';
        return `
            <div class="entry" data-id="${entry.id}">
                <div class="entry-header">
                    <span><span class="mood-icon">${moodIcon}</span> ${escapeHtml(entry.title || "untitled")} · ${formatted}</span>
                    <div class="entry-actions">
                        <button class="edit-entry" data-id="${entry.id}" title="edit"><i class="fas fa-pen"></i></button>
                        <button class="delete-entry" data-id="${entry.id}" title="delete"><i class="fas fa-trash-alt"></i></button>
                    </div>
                </div>
                <div class="entry-text">${escapeHtml(entry.note.substring(0, 120))}${entry.note.length > 120 ? '...' : ''}</div>
            </div>
        `;
    }).join('');
    
  
    document.querySelectorAll('.delete-entry').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.getAttribute('data-id'));
            deleteEntryById(id);
        });
    });
    document.querySelectorAll('.edit-entry').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.getAttribute('data-id'));
            startEditEntry(id);
        });
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, (m) => {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

function deleteEntryById(id) {
    if (confirm('Delete this entry?')) {
        entries = entries.filter(entry => entry.id !== id);
        saveToStorage();
        renderAll();
        if (editingId === id) cancelEdit();
    }
}

function startEditEntry(id) {
    const entry = entries.find(e => e.id === id);
    if (!entry) return;
    editingId = id;
    selectedMood = entry.mood;
    entryTitle.value = entry.title || '';
    entryNote.value = entry.note || '';
    
    moodBtns.forEach(btn => {
        if (btn.getAttribute('data-mood') === selectedMood) btn.classList.add('active');
        else btn.classList.remove('active');
    });
    editIndicator.style.display = 'block';
    saveBtn.innerHTML = '<i class="fas fa-pen"></i> Update entry';
}

function cancelEdit() {
    editingId = null;
    entryTitle.value = '';
    entryNote.value = '';
    editIndicator.style.display = 'none';
    saveBtn.innerHTML = '<i class="fas fa-save"></i> Save intention + mood';
   
}


function saveCurrentEntry() {
    const title = entryTitle.value.trim();
    const note = entryNote.value.trim();
    if (!title && !note) {
        alert("Write a short title or note to capture your mood ✨");
        return;
    }
    if (editingId !== null) {
       
        const index = entries.findIndex(e => e.id === editingId);
        if (index !== -1) {
            entries[index] = {
                ...entries[index],
                mood: selectedMood,
                title: title || "untitled moment",
                note: note || "no additional note",
                date: new Date().toISOString()  
            };
        }
        cancelEdit();
    } else {
      
        const newEntry = {
            id: Date.now(),
            date: new Date().toISOString(),
            mood: selectedMood,
            title: title || "untitled moment",
            note: note || "no additional note",
        };
        entries.unshift(newEntry);
    }
    saveToStorage();
    renderAll();
    entryTitle.value = "";
    entryNote.value = "";
   
    const feedback = document.createElement('div');
    feedback.innerText = editingId !== null ? "✓ updated" : "✓ saved";
    feedback.style.cssText = "position:fixed; bottom:20px; right:20px; background:#e28d6c; color:white; padding:8px 18px; border-radius:40px; font-weight:500; z-index:999;";
    document.body.appendChild(feedback);
    setTimeout(() => feedback.remove(), 1500);
}


function updateStats() {
    totalSpan.innerText = entries.length;
    streakSpan.innerText = calculateStreak();
    topMoodSpan.innerText = getTopMood();
}

function renderAll() {
    renderHistory();
    updateStats();
    updateMoodChart();
}


function exportData() {
    const dataStr = JSON.stringify(entries, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `moodflow_backup_${new Date().toISOString().slice(0,19)}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function importData(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const imported = JSON.parse(e.target.result);
            if (Array.isArray(imported) && imported.every(item => item.id && item.date && item.mood)) {
                entries = imported;
                saveToStorage();
                renderAll();
                cancelEdit();
                alert(`Imported ${entries.length} entries successfully!`);
            } else {
                alert('Invalid file format');
            }
        } catch (err) {
            alert('Error parsing file');
        }
    };
    reader.readAsText(file);
}


function initMoodSelection() {
    moodBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            moodBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedMood = btn.getAttribute('data-mood');
        });
    });
  
    const defaultBtn = document.querySelector(`.mood-btn[data-mood="${selectedMood}"]`);
    if (defaultBtn) defaultBtn.classList.add('active');
}


function initTheme() {
    const storedTheme = localStorage.getItem('moodflow_theme');
    if (storedTheme === 'dark') {
        document.body.classList.add('dark');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i> Light mode';
    } else {
        document.body.classList.remove('dark');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i> Dark mode';
    }
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        localStorage.setItem('moodflow_theme', isDark ? 'dark' : 'light');
        themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i> Light mode' : '<i class="fas fa-moon"></i> Dark mode';
    });
}


loadFromStorage();
initMoodSelection();
initTheme();
saveBtn.addEventListener('click', saveCurrentEntry);
exportBtn.addEventListener('click', exportData);
importBtn.addEventListener('click', () => importFileInput.click());
importFileInput.addEventListener('change', (e) => {
    if (e.target.files.length) importData(e.target.files[0]);
    importFileInput.value = '';
});


entryNote.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') saveCurrentEntry();
});