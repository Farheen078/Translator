
let entries = [];     
let selectedMood = "radiant";


const moodBtns = document.querySelectorAll('.mood-btn');
const entryTitle = document.getElementById('entryTitle');
const entryNote = document.getElementById('entryNote');
const saveBtn = document.getElementById('saveEntryBtn');
const historyDiv = document.getElementById('historyList');
const totalSpan = document.getElementById('totalCount');
const streakSpan = document.getElementById('streakCount');
const topMoodSpan = document.getElementById('topMood');
const themeToggle = document.getElementById('themeToggle');


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
        const day = new Date(entry.date).toISOString().split('T')[0];
        uniqueDays.add(day);
    });
    const sortedDays = Array.from(uniqueDays).sort().reverse();
    if (sortedDays.length === 0) return 0;
    let streak = 1;
    const todayStr = new Date().toISOString().split('T')[0];
    if (sortedDays[0] !== todayStr) return 0; 
    for (let i = 0; i < sortedDays.length - 1; i++) {
        const current = new Date(sortedDays[i]);
        const next = new Date(sortedDays[i + 1]);
        const diffDays = (current - next) / (1000 * 3600 * 24);
        if (diffDays === 1) streak++;
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
    const recent = [...entries].sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 12);
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
                    <button class="delete-entry" data-id="${entry.id}"><i class="fas fa-trash-alt"></i></button>
                </div>
                <div class="entry-text">${escapeHtml(entry.note.substring(0, 100))}${entry.note.length > 100 ? '...' : ''}</div>
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
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function (m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

function deleteEntryById(id) {
    entries = entries.filter(entry => entry.id !== id);
    saveToStorage();
    renderAll();
}

function updateStats() {
    totalSpan.innerText = entries.length;
    streakSpan.innerText = calculateStreak();
    topMoodSpan.innerText = getTopMood();
}

function renderAll() {
    renderHistory();
    updateStats();
}

function saveCurrentEntry() {
    const title = entryTitle.value.trim();
    const note = entryNote.value.trim();
    if (!title && !note) {
        alert("Write a short title or note to capture your mood ✨");
        return;
    }
    const newEntry = {
        id: Date.now(),
        date: new Date().toISOString(),
        mood: selectedMood,
        title: title || "untitled moment",
        note: note || "no additional note",
    };
    entries.unshift(newEntry);
    saveToStorage();
    entryTitle.value = "";
    entryNote.value = "";
    renderAll();
  
    const feedback = document.createElement('div');
    feedback.innerText = "✓ saved";
    feedback.style.position = "fixed";
    feedback.style.bottom = "20px";
    feedback.style.right = "20px";
    feedback.style.background = "#e28d6c";
    feedback.style.color = "white";
    feedback.style.padding = "8px 18px";
    feedback.style.borderRadius = "40px";
    feedback.style.fontWeight = "500";
    feedback.style.zIndex = "999";
    document.body.appendChild(feedback);
    setTimeout(() => feedback.remove(), 1500);
}


function initMoodSelection() {
    moodBtns.forEach(btn => {
        const moodVal = btn.getAttribute('data-mood');
        if (moodVal === selectedMood) btn.classList.add('active');
        btn.addEventListener('click', () => {
            moodBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedMood = btn.getAttribute('data-mood');
        });
    });
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


entryNote.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') saveCurrentEntry();
});