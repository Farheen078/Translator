#!/usr/bin/env python3
"""
Google Translate Clone – run this script, open browser, and translate text.
Requires: pip install flask deep-translator
"""

import subprocess
import sys
import os

# Auto-install missing packages
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from flask import Flask, request, jsonify, render_template_string
    from deep_translator import GoogleTranslator
except ImportError as e:
    print("📦 Missing required packages. Installing...")
    install_package("flask")
    install_package("deep-translator")
    from flask import Flask, request, jsonify, render_template_string
    from deep_translator import GoogleTranslator

app = Flask(__name__)

# Language mapping (full names)
LANGUAGES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian', 'az': 'Azerbaijani',
    'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
    'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)',
    'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English',
    'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino', 'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian',
    'gl': 'Galician', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole',
    'ha': 'Hausa', 'haw': 'Hawaiian', 'iw': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian',
    'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese',
    'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer', 'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)',
    'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish',
    'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori',
    'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian',
    'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian',
    'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona',
    'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish',
    'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish', 'tg': 'Tajik', 'ta': 'Tamil', 'te': 'Telugu',
    'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'uz': 'Uzbek', 'vi': 'Vietnamese',
    'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 Translate Master | Free Language Translator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0f172a, #1e1b4b);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            width: 100%;
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(12px);
            border-radius: 48px;
            padding: 32px;
            border: 1px solid rgba(255,255,255,0.15);
            box-shadow: 0 25px 45px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            font-size: 2rem;
            background: linear-gradient(135deg, #fbbf24, #ec4899);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
            margin-bottom: 8px;
        }
        .sub { text-align: center; color: #94a3b8; margin-bottom: 32px; }
        .translator-box {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        @media (max-width: 800px) {
            .translator-box { grid-template-columns: 1fr; gap: 20px; }
            .swap-icon { transform: rotate(90deg); margin: 10px 0; }
        }
        .panel {
            background: #1e293b;
            border-radius: 32px;
            padding: 20px;
            border: 1px solid #334155;
        }
        .language-selector {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            gap: 12px;
        }
        select {
            background: #0f172a;
            color: #f1f5f9;
            border: 1px solid #475569;
            border-radius: 40px;
            padding: 8px 16px;
            font-size: 0.9rem;
            cursor: pointer;
            flex: 1;
        }
        textarea {
            width: 100%;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 24px;
            padding: 16px;
            font-size: 1rem;
            color: #f1f5f9;
            font-family: inherit;
            resize: vertical;
            outline: none;
        }
        textarea:focus { border-color: #facc15; }
        .action-buttons { display: flex; gap: 12px; margin-top: 12px; justify-content: flex-end; }
        .icon-btn {
            background: #334155;
            border: none;
            padding: 8px 12px;
            border-radius: 40px;
            cursor: pointer;
            color: #cbd5e1;
            transition: 0.2s;
        }
        .icon-btn:hover { background: #facc15; color: #0f172a; }
        .swap-icon {
            background: #334155;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: 0.2s;
            margin-top: 40px;
        }
        .swap-icon:hover { background: #facc15; transform: scale(1.05); }
        .footer { text-align: center; margin-top: 32px; font-size: 0.75rem; color: #64748b; }
    </style>
</head>
<body>
<div class="container">
    <h1><i class="fas fa-language"></i> Translate Master</h1>
    <div class="sub">free & instant · powered by Google Translate</div>

    <div class="translator-box">
        <div class="panel">
            <div class="language-selector">
                <select id="sourceLang">
                    <option value="auto">🔍 Detect Language</option>
                </select>
                <div class="action-buttons">
                    <button class="icon-btn" id="clearSource"><i class="fas fa-eraser"></i></button>
                    <button class="icon-btn" id="speakSource"><i class="fas fa-volume-up"></i></button>
                </div>
            </div>
            <textarea id="sourceText" rows="6" placeholder="Enter text to translate..."></textarea>
        </div>

        <div class="swap-icon" id="swapBtn">
            <i class="fas fa-arrows-alt-h"></i>
        </div>

        <div class="panel">
            <div class="language-selector">
                <select id="targetLang"></select>
                <div class="action-buttons">
                    <button class="icon-btn" id="copyTarget"><i class="fas fa-copy"></i></button>
                    <button class="icon-btn" id="speakTarget"><i class="fas fa-volume-up"></i></button>
                </div>
            </div>
            <textarea id="targetText" rows="6" readonly placeholder="Translation will appear here..."></textarea>
        </div>
    </div>

    <div class="footer">
        <i class="fas fa-globe"></i> supports 100+ languages · real-time translation
    </div>
</div>

<script>
    const languages = {{ languages|tojson }};
    const languageList = Object.entries(languages).map(([code, name]) => ({ code, name }));
    languageList.sort((a,b) => a.name.localeCompare(b.name));

    const sourceSelect = document.getElementById('sourceLang');
    const targetSelect = document.getElementById('targetLang');

    languageList.forEach(lang => {
        const opt1 = document.createElement('option');
        opt1.value = lang.code;
        opt1.textContent = lang.name;
        sourceSelect.appendChild(opt1);
        const opt2 = document.createElement('option');
        opt2.value = lang.code;
        opt2.textContent = lang.name;
        targetSelect.appendChild(opt2);
    });
    sourceSelect.value = 'auto';
    targetSelect.value = 'en';

    const sourceText = document.getElementById('sourceText');
    const targetText = document.getElementById('targetText');
    const swapBtn = document.getElementById('swapBtn');
    const clearSource = document.getElementById('clearSource');
    const copyTarget = document.getElementById('copyTarget');
    const speakSource = document.getElementById('speakSource');
    const speakTarget = document.getElementById('speakTarget');

    let debounceTimer;

    function translate() {
        const text = sourceText.value;
        if (!text.trim()) {
            targetText.value = '';
            return;
        }
        const sourceLang = sourceSelect.value;
        const targetLang = targetSelect.value;

        fetch('/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, source: sourceLang, target: targetLang })
        })
        .then(res => res.json())
        .then(data => {
            if (data.translated) targetText.value = data.translated;
            else targetText.value = 'Error: ' + (data.error || 'Translation failed');
        })
        .catch(() => targetText.value = 'Network error');
    }

    sourceText.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(translate, 500);
    });
    sourceSelect.addEventListener('change', translate);
    targetSelect.addEventListener('change', translate);

    swapBtn.addEventListener('click', () => {
        const srcLang = sourceSelect.value;
        const tgtLang = targetSelect.value;
        const srcText = sourceText.value;
        const tgtText = targetText.value;
        sourceSelect.value = tgtLang;
        targetSelect.value = srcLang;
        sourceText.value = tgtText;
        targetText.value = '';
        translate();
    });

    clearSource.addEventListener('click', () => {
        sourceText.value = '';
        targetText.value = '';
        translate();
    });

    copyTarget.addEventListener('click', () => {
        targetText.select();
        document.execCommand('copy');
        alert('Copied to clipboard!');
    });

    speakSource.addEventListener('click', () => {
        const text = sourceText.value;
        if (text) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = sourceSelect.value === 'auto' ? 'en' : sourceSelect.value;
            window.speechSynthesis.speak(utterance);
        }
    });

    speakTarget.addEventListener('click', () => {
        const text = targetText.value;
        if (text) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = targetSelect.value;
            window.speechSynthesis.speak(utterance);
        }
    });

    translate();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, languages=LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get('text', '')
    source = data.get('source', 'auto')
    target = data.get('target', 'en')
    
    if not text.strip():
        return jsonify({'translated': ''})
    
    try:
        # Use deep-translator (more reliable)
        if source == 'auto':
            translator = GoogleTranslator(source='auto', target=target)
        else:
            translator = GoogleTranslator(source=source, target=target)
        translated = translator.translate(text)
        return jsonify({'translated': translated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    import webbrowser
    import threading
    import time
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    print("\n✅ Translate Master is running!")
    print("🌐 Opening browser at http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()