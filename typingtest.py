#!/usr/bin/env python3
"""
Typing Master – Professional typing speed test in your browser.
Features: countdown, timed mode (30s/60s/infinite), live WPM/CPM, accuracy, mistake counter.
"""

import http.server
import socketserver
import webbrowser
import sys

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ Typing Master | Speed & Accuracy Test</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }

        body {
            background: linear-gradient(145deg, #0b1120, #111827);
            font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            max-width: 1000px;
            width: 100%;
            background: rgba(17, 24, 39, 0.8);
            backdrop-filter: blur(12px);
            border-radius: 56px;
            padding: 32px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 25px 45px rgba(0,0,0,0.3);
        }

        h1 {
            text-align: center;
            font-size: 2.2rem;
            background: linear-gradient(135deg, #fbbf24, #ec4899);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
            margin-bottom: 8px;
        }

        .mode-selector {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin: 20px 0;
        }

        .mode-btn {
            background: #1f2937;
            border: none;
            padding: 8px 24px;
            border-radius: 40px;
            color: #9ca3af;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
        }

        .mode-btn.active {
            background: #facc15;
            color: #0f172a;
            box-shadow: 0 0 10px rgba(250,204,21,0.5);
        }

        .stats {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 28px;
            flex-wrap: wrap;
        }

        .stat-card {
            background: #1e293b;
            border-radius: 32px;
            padding: 14px 20px;
            flex: 1;
            text-align: center;
            border-bottom: 2px solid #facc15;
        }

        .stat-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            color: #94a3b8;
            letter-spacing: 1px;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 800;
            color: #facc15;
            line-height: 1;
        }

        .text-display {
            background: #0f172a;
            border-radius: 32px;
            padding: 28px;
            margin: 20px 0;
            font-size: 1.3rem;
            line-height: 1.6;
            color: #cbd5e1;
            font-family: 'Courier New', monospace;
            border: 1px solid #334155;
            min-height: 160px;
        }

        .text-display span {
            transition: all 0.05s;
        }

        .text-display .correct {
            color: #4ade80;
        }

        .text-display .incorrect {
            color: #f87171;
            background: rgba(248,113,113,0.2);
            border-radius: 4px;
        }

        .text-display .current {
            background: #facc15;
            color: #0f172a;
            border-radius: 4px;
            animation: blink 0.8s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .input-area {
            margin: 20px 0;
        }

        textarea {
            width: 100%;
            background: #1e293b;
            border: 2px solid #334155;
            border-radius: 32px;
            padding: 20px;
            font-size: 1.2rem;
            font-family: 'Courier New', monospace;
            color: #f1f5f9;
            resize: none;
            outline: none;
        }

        textarea:focus {
            border-color: #facc15;
            box-shadow: 0 0 0 3px rgba(250,204,21,0.2);
        }

        .controls {
            display: flex;
            gap: 16px;
            justify-content: center;
            margin-top: 24px;
        }

        button {
            background: linear-gradient(135deg, #facc15, #ec4899);
            border: none;
            padding: 12px 28px;
            border-radius: 60px;
            font-weight: 700;
            cursor: pointer;
            transition: 0.2s;
        }

        button:active {
            transform: scale(0.96);
        }

        .reset-btn {
            background: #334155;
            color: white;
        }

        .timer-area {
            text-align: center;
            font-size: 1.8rem;
            font-weight: 800;
            font-family: monospace;
            margin: 16px 0;
            color: #facc15;
        }

        .result {
            text-align: center;
            margin-top: 20px;
            padding: 16px;
            background: #1e293b;
            border-radius: 40px;
            color: #cbd5e1;
        }

        footer {
            text-align: center;
            margin-top: 32px;
            font-size: 0.7rem;
            color: #475569;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>⚡ TYPING MASTER ⚡</h1>
    <div class="mode-selector">
        <button class="mode-btn" data-mode="30">30 sec</button>
        <button class="mode-btn" data-mode="60">60 sec</button>
        <button class="mode-btn active" data-mode="infinite">♾️ Paragraph</button>
    </div>

    <div class="stats">
        <div class="stat-card"><div class="stat-label">WPM</div><div class="stat-value" id="wpm">0</div></div>
        <div class="stat-card"><div class="stat-label">Accuracy</div><div class="stat-value" id="accuracy">100</div><span>%</span></div>
        <div class="stat-card"><div class="stat-label">Mistakes</div><div class="stat-value" id="mistakes">0</div></div>
        <div class="stat-card"><div class="stat-label">CPM</div><div class="stat-value" id="cpm">0</div></div>
    </div>

    <div class="timer-area" id="timerDisplay">⏱️ Ready</div>

    <div class="text-display" id="textDisplay"></div>

    <div class="input-area">
        <textarea id="inputArea" rows="3" placeholder="Click 'Start' then type here..." disabled></textarea>
    </div>

    <div class="controls">
        <button id="startBtn">🚀 Start Test</button>
        <button id="resetBtn" class="reset-btn">⟳ New Text</button>
    </div>

    <div class="result" id="resultArea"></div>
    <footer>✨ backspace allowed · timer starts after countdown · live stats ✨</footer>
</div>

<script>
    // ---------- TEXT LIBRARY ----------
    const texts = [
        "The quick brown fox jumps over the lazy dog near the river bank.",
        "Typing speed is measured in words per minute, counting every five keystrokes as one word.",
        "Practice makes perfect, and consistency is the key to improving your typing skills.",
        "The sun dipped below the horizon, painting the sky in shades of orange and pink.",
        "Technology advances rapidly, bringing new possibilities and challenges every single day.",
        "A journey of a thousand miles begins with a single step, so start typing today.",
        "Curiosity and passion drive innovation, leading to discoveries that change the world.",
        "Silence speaks volumes when words are not enough to express deep emotions.",
        "The gentle rain washed away the dust, leaving the earth fresh and fragrant.",
        "Learning a new skill requires patience, dedication, and a willingness to make mistakes."
    ];

    let currentText = "";
    let mode = "infinite";   // "30", "60", "infinite"
    let timeLeft = 0;
    let timerInterval = null;
    let testActive = false;
    let startTime = null;
    let mistakeCount = 0;
    let totalTyped = 0;

    // DOM elements
    const textDisplay = document.getElementById("textDisplay");
    const inputArea = document.getElementById("inputArea");
    const startBtn = document.getElementById("startBtn");
    const resetBtn = document.getElementById("resetBtn");
    const wpmSpan = document.getElementById("wpm");
    const accuracySpan = document.getElementById("accuracy");
    const mistakesSpan = document.getElementById("mistakes");
    const cpmSpan = document.getElementById("cpm");
    const timerDisplay = document.getElementById("timerDisplay");
    const resultArea = document.getElementById("resultArea");

    function getRandomText() {
        return texts[Math.floor(Math.random() * texts.length)];
    }

    function renderTextWithHighlight(typed) {
        let html = "";
        for (let i = 0; i < currentText.length; i++) {
            let cls = "";
            if (i < typed.length) {
                cls = (typed[i] === currentText[i]) ? "correct" : "incorrect";
            }
            if (i === typed.length && testActive) {
                cls += " current";
            }
            html += `<span class="${cls}">${currentText[i]}</span>`;
        }
        if (typed.length > currentText.length) {
            const extra = typed.slice(currentText.length);
            for (let ch of extra) {
                html += `<span class="incorrect">${ch}</span>`;
            }
        }
        textDisplay.innerHTML = html;
    }

    function updateLiveStats() {
        if (!testActive) return;
        const typed = inputArea.value;
        const elapsed = (Date.now() - startTime) / 1000;
        if (elapsed <= 0) return;
        
        const words = typed.length / 5;
        const minutes = elapsed / 60;
        const wpm = Math.round(words / minutes);
        const cpm = Math.round(typed.length / minutes);
        
        // accuracy and mistakes
        let correct = 0;
        let mistakes = 0;
        for (let i = 0; i < typed.length; i++) {
            if (i < currentText.length) {
                if (typed[i] === currentText[i]) correct++;
                else mistakes++;
            } else {
                mistakes++;
            }
        }
        const total = Math.max(typed.length, currentText.length);
        const accuracy = total === 0 ? 100 : Math.round((correct / total) * 100);
        
        wpmSpan.innerText = wpm;
        cpmSpan.innerText = cpm;
        accuracySpan.innerText = accuracy;
        mistakesSpan.innerText = mistakes;
        mistakeCount = mistakes;
        totalTyped = typed.length;
    }

    function checkCompletion() {
        const typed = inputArea.value;
        if (typed.length >= currentText.length && mode === "infinite" && testActive) {
            finishTest(true);
        }
        renderTextWithHighlight(typed);
        updateLiveStats();
    }

    function finishTest(completed = false) {
        if (!testActive) return;
        testActive = false;
        if (timerInterval) clearInterval(timerInterval);
        inputArea.disabled = true;
        
        const typed = inputArea.value;
        const elapsed = (Date.now() - startTime) / 1000;
        const wpm = Math.round((typed.length / 5) / (elapsed / 60));
        const acc = accuracySpan.innerText;
        let msg = "";
        if (mode !== "infinite" && timeLeft <= 0) {
            msg = `⏰ Time's up! WPM: ${wpm}, Accuracy: ${acc}%, Mistakes: ${mistakeCount}`;
        } else if (completed) {
            msg = `🎉 Paragraph completed! WPM: ${wpm}, Accuracy: ${acc}%, Mistakes: ${mistakeCount}`;
        } else {
            msg = `Test stopped. WPM: ${wpm}, Accuracy: ${acc}%`;
        }
        resultArea.innerHTML = msg;
        startBtn.innerText = "🚀 Start Test";
        timerDisplay.innerText = "✅ Finished";
    }

    function startCountdown() {
        let count = 3;
        timerDisplay.innerText = `⏰ Get ready... ${count}`;
        const countdown = setInterval(() => {
            count--;
            if (count > 0) {
                timerDisplay.innerText = `⏰ Get ready... ${count}`;
            } else {
                clearInterval(countdown);
                timerDisplay.innerText = mode === "infinite" ? "♾️ GO!" : `⏱️ ${timeLeft}s left`;
                beginTest();
            }
        }, 1000);
    }

    function beginTest() {
        testActive = true;
        startTime = Date.now();
        inputArea.disabled = false;
        inputArea.value = "";
        inputArea.focus();
        mistakeCount = 0;
        totalTyped = 0;
        renderTextWithHighlight("");
        updateLiveStats();
        
        if (mode !== "infinite") {
            if (timerInterval) clearInterval(timerInterval);
            timerInterval = setInterval(() => {
                if (!testActive) return;
                timeLeft--;
                timerDisplay.innerText = `⏱️ ${timeLeft}s left`;
                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    finishTest(false);
                }
            }, 1000);
        }
    }

    function startTest() {
        if (testActive) return;
        if (mode !== "infinite") {
            timeLeft = parseInt(mode);
        }
        inputArea.value = "";
        resultArea.innerHTML = "";
        mistakeCount = 0;
        totalTyped = 0;
        wpmSpan.innerText = "0";
        cpmSpan.innerText = "0";
        accuracySpan.innerText = "100";
        mistakesSpan.innerText = "0";
        startCountdown();
    }

    function resetTest() {
        if (testActive) {
            if (timerInterval) clearInterval(timerInterval);
            testActive = false;
        }
        currentText = getRandomText();
        renderTextWithHighlight("");
        inputArea.value = "";
        inputArea.disabled = true;
        wpmSpan.innerText = "0";
        cpmSpan.innerText = "0";
        accuracySpan.innerText = "100";
        mistakesSpan.innerText = "0";
        timerDisplay.innerText = "⏱️ Ready";
        resultArea.innerHTML = "";
        startBtn.innerText = "🚀 Start Test";
    }

    inputArea.addEventListener("input", () => {
        if (testActive) {
            checkCompletion();
            updateLiveStats();
        }
    });

    startBtn.addEventListener("click", startTest);
    resetBtn.addEventListener("click", resetTest);

    // mode selection
    document.querySelectorAll(".mode-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            mode = btn.getAttribute("data-mode");
            resetTest();
        });
    });

    resetTest();
</script>
</body>
</html>
"""

# ---------- FIND AVAILABLE PORT ----------
def find_free_port(start=8888, max_tries=20):
    for port in range(start, start + max_tries):
        try:
            with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as test:
                return port
        except OSError:
            continue
    return None

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def main():
    port = find_free_port()
    if port is None:
        print("❌ No free port found. Please close some applications and try again.")
        sys.exit(1)
    
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        url = f"http://localhost:{port}"
        print(f"\n✅ Typing Master is running!")
        print(f"🌐 Open: {url}\n")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped.")
            httpd.shutdown()

if __name__ == "__main__":
    main()