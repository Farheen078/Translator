#!/usr/bin/env python3
"""
QR Code Generator – starts a local web server and opens a browser-based QR maker.
No external Python libraries required.
"""

import http.server
import socketserver
import webbrowser
import os

# ---------- HTML PAGE (embedded) ----------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code Generator | instant & free</title>
    <script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 32px;
            padding: 40px;
            max-width: 550px;
            width: 100%;
            box-shadow: 0 25px 45px rgba(0,0,0,0.2);
            text-align: center;
            transition: transform 0.2s;
        }
        h1 {
            font-size: 2rem;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
        }
        .sub {
            color: #6c757d;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 25px;
            text-align: left;
        }
        label {
            font-weight: 600;
            display: block;
            margin-bottom: 8px;
            color: #343a40;
        }
        input {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #e9ecef;
            border-radius: 60px;
            font-size: 1rem;
            transition: 0.2s;
            font-family: monospace;
        }
        input:focus {
            outline: none;
            border-color: #764ba2;
            box-shadow: 0 0 0 3px rgba(118,75,162,0.2);
        }
        .qr-container {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 24px;
            margin: 20px 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 220px;
        }
        #qrcode {
            display: flex;
            justify-content: center;
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            padding: 12px 28px;
            border-radius: 60px;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: 0.2s;
            margin-top: 10px;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
            filter: brightness(1.05);
        }
        .download-btn {
            background: #28a745;
            margin-top: 12px;
        }
        .download-btn:hover {
            background: #218838;
        }
        footer {
            margin-top: 25px;
            font-size: 0.75rem;
            color: #adb5bd;
        }
        .error {
            color: #dc3545;
            font-size: 0.8rem;
            margin-top: 8px;
        }
    </style>
</head>
<body>
<div class="card">
    <h1>✨ QR Code Generator</h1>
    <div class="sub">instant · free · no sign‑up</div>
    
    <div class="input-group">
        <label>📝 Enter text or URL</label>
        <input type="text" id="textInput" placeholder="https:// or any text...">
    </div>
    
    <div class="qr-container">
        <div id="qrcode"></div>
    </div>
    
    <button id="generateBtn">⚡ Generate QR Code</button>
    <button id="downloadBtn" class="download-btn">💾 Download as PNG</button>
    
   
</div>

<script>
    let currentQR = null;
    
    function generateQR(text) {
        const qrDiv = document.getElementById('qrcode');
        qrDiv.innerHTML = '';
        if (!text.trim()) {
            qrDiv.innerHTML = '<div style="color:#adb5bd;">✨ type something above ✨</div>';
            return false;
        }
        try {
            currentQR = new QRCode(qrDiv, {
                text: text,
                width: 200,
                height: 200,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H
            });
            return true;
        } catch(e) {
            qrDiv.innerHTML = '<div class="error">⚠️ text too long or invalid</div>';
            return false;
        }
    }
    
    function downloadQR() {
        const qrCanvas = document.querySelector('#qrcode canvas');
        if (!qrCanvas) {
            alert('Generate a QR code first');
            return;
        }
        const link = document.createElement('a');
        link.download = 'qrcode.png';
        link.href = qrCanvas.toDataURL();
        link.click();
    }
    
    const inputField = document.getElementById('textInput');
    const generateBtn = document.getElementById('generateBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    
    generateBtn.addEventListener('click', () => {
        const text = inputField.value;
        generateQR(text);
    });
    
    downloadBtn.addEventListener('click', downloadQR);
    
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') generateQR(inputField.value);
    });
    
    // demo default
    generateQR('https://github.com');
</script>
</body>
</html>
"""

# ---------- SIMPLE HTTP SERVER ----------
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
    PORT = 8888
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"\n✅ QR Code Generator ready!")
        print(f"🌐 Open your browser: http://localhost:{PORT}\n")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped. Goodbye!")
            httpd.shutdown()

if __name__ == "__main__":
    main()