#!/usr/bin/env python3
"""
Mood Color Canvas – generate abstract SVG art based on your mood.
Run this script, then open http://localhost:8080 in your browser.
"""

import http.server
import socketserver
import webbrowser
import random
import json
from urllib.parse import urlparse, parse_qs

# ---------- MOOD COLOR MAPPING ----------
MOOD_COLORS = {
    "happy": ["#FFD700", "#FFA500", "#FF8C00", "#FFB347", "#FFCC33"],
    "calm": ["#87CEEB", "#98FB98", "#B0E0E6", "#ADD8E6", "#E0FFFF"],
    "energetic": ["#FF4500", "#FF1493", "#FF6347", "#DC143C", "#FF2400"],
    "sad": ["#4A55A2", "#6C5B7B", "#3B3B98", "#5D6D7E", "#2C3E50"],
    "creative": ["#9B59B6", "#3498DB", "#1ABC9C", "#E74C3C", "#F1C40F"],
    "peaceful": ["#A8E6CF", "#D4F1F4", "#FFD3B6", "#FFAAA5", "#FF8B94"],
    "dark": ["#2C3E50", "#34495E", "#1A252F", "#4A5D6B", "#2A3B4C"],
}

def generate_svg(mood):
    """Generate random abstract SVG art based on mood."""
    colors = MOOD_COLORS.get(mood, MOOD_COLORS["calm"])
    num_shapes = random.randint(5, 12)
    shapes = []
    for _ in range(num_shapes):
        shape_type = random.choice(["circle", "rect", "ellipse", "path"])
        color = random.choice(colors)
        if shape_type == "circle":
            cx = random.randint(50, 350)
            cy = random.randint(50, 350)
            r = random.randint(20, 100)
            shapes.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{random.uniform(0.5,0.9)}" />')
        elif shape_type == "rect":
            x = random.randint(20, 300)
            y = random.randint(20, 300)
            w = random.randint(40, 150)
            h = random.randint(40, 150)
            rx = random.randint(0, 30)
            shapes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{color}" opacity="{random.uniform(0.6,0.9)}" />')
        elif shape_type == "ellipse":
            cx = random.randint(50, 350)
            cy = random.randint(50, 350)
            rx = random.randint(30, 100)
            ry = random.randint(20, 80)
            shapes.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{color}" opacity="{random.uniform(0.5,0.9)}" />')
        else:  # path – wavy line
            points = []
            for i in range(4):
                x = 50 + i * 100
                y = random.randint(100, 300)
                points.append(f"{x},{y}")
            path = f'M {points[0]} Q {points[1]} {points[2]} {points[3]}'
            shapes.append(f'<path d="{path}" stroke="{color}" stroke-width="{random.randint(3,8)}" fill="none" opacity="{random.uniform(0.6,0.9)}" />')
    
    svg = f'''<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
        <rect width="400" height="400" fill="#f8f9fa" />
        {"".join(shapes)}
    </svg>'''
    return svg

# ---------- HTML PAGE TEMPLATE ----------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mood Color Canvas</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Inter, system-ui, sans-serif;
            background: linear-gradient(145deg, #f0f2f5 0%, #e9ecef 100%);
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            width: 100%;
            background: white;
            border-radius: 48px;
            box-shadow: 0 25px 45px rgba(0,0,0,0.1);
            overflow: hidden;
            padding: 30px;
        }
        h1 {
            text-align: center;
            font-weight: 600;
            margin: 0 0 8px 0;
            background: linear-gradient(135deg, #6c5ce7, #a8a4ff);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
        }
        .sub {
            text-align: center;
            color: #6c757d;
            margin-bottom: 30px;
        }
        .mood-selector {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
            margin-bottom: 30px;
        }
        .mood-btn {
            background: #f1f3f5;
            border: none;
            padding: 12px 24px;
            border-radius: 60px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            color: #495057;
        }
        .mood-btn:hover {
            transform: translateY(-2px);
            background: #e9ecef;
        }
        .mood-btn.active {
            background: #6c5ce7;
            color: white;
            box-shadow: 0 8px 16px rgba(108,92,231,0.3);
        }
        .canvas-area {
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        .svg-container {
            background: #f8f9fa;
            border-radius: 24px;
            padding: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        }
        svg {
            display: block;
            margin: 0 auto;
            border-radius: 16px;
        }
        .info {
            flex: 1;
            min-width: 200px;
        }
        .info h3 {
            margin: 0 0 12px 0;
        }
        .color-palette {
            display: flex;
            gap: 12px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .color-swatch {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        button.refresh {
            background: #6c5ce7;
            color: white;
            border: none;
            padding: 12px 28px;
            border-radius: 40px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 16px;
            transition: 0.2s;
        }
        button.refresh:hover {
            background: #5a4bd1;
            transform: scale(1.02);
        }
        footer {
            text-align: center;
            margin-top: 40px;
            font-size: 0.75rem;
            color: #adb5bd;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🎨 Mood Color Canvas</h1>
    <div class="sub">select your mood → generate abstract art & color palette</div>
    
    <div class="mood-selector" id="moodSelector">
        <button class="mood-btn" data-mood="happy">😊 Happy</button>
        <button class="mood-btn" data-mood="calm">🍃 Calm</button>
        <button class="mood-btn" data-mood="energetic">⚡ Energetic</button>
        <button class="mood-btn" data-mood="sad">🌧️ Sad</button>
        <button class="mood-btn" data-mood="creative">🎨 Creative</button>
        <button class="mood-btn" data-mood="peaceful">🌸 Peaceful</button>
        <button class="mood-btn" data-mood="dark">🌙 Dark</button>
    </div>
    
    <div class="canvas-area">
        <div class="svg-container" id="svgContainer">
            <!-- SVG will be inserted here -->
        </div>
        <div class="info">
            <h3>Color Palette</h3>
            <div id="colorPalette" class="color-palette"></div>
            <button class="refresh" id="refreshBtn">⟳ Generate new art</button>
            <p style="margin-top: 20px; font-size: 0.85rem; color: #6c757d;">Each click creates a unique abstract composition based on your mood.</p>
        </div>
    </div>
    <footer>✨ local generative art · no data leaves your browser ✨</footer>
</div>

<script>
    // Mood color mappings (same as server)
    const moodColors = {
        happy: ["#FFD700", "#FFA500", "#FF8C00", "#FFB347", "#FFCC33"],
        calm: ["#87CEEB", "#98FB98", "#B0E0E6", "#ADD8E6", "#E0FFFF"],
        energetic: ["#FF4500", "#FF1493", "#FF6347", "#DC143C", "#FF2400"],
        sad: ["#4A55A2", "#6C5B7B", "#3B3B98", "#5D6D7E", "#2C3E50"],
        creative: ["#9B59B6", "#3498DB", "#1ABC9C", "#E74C3C", "#F1C40F"],
        peaceful: ["#A8E6CF", "#D4F1F4", "#FFD3B6", "#FFAAA5", "#FF8B94"],
        dark: ["#2C3E50", "#34495E", "#1A252F", "#4A5D6B", "#2A3B4C"]
    };
    
    let currentMood = "calm";
    
    function generateSVG(mood) {
        const colors = moodColors[mood];
        const numShapes = Math.floor(Math.random() * 8) + 5;
        let shapes = [];
        for (let i = 0; i < numShapes; i++) {
            const shapeType = randomItem(["circle", "rect", "ellipse", "path"]);
            const color = randomItem(colors);
            const opacity = (Math.random() * 0.4 + 0.5).toFixed(2);
            if (shapeType === "circle") {
                const cx = Math.random() * 350 + 25;
                const cy = Math.random() * 350 + 25;
                const r = Math.random() * 80 + 20;
                shapes.push(`<circle cx="${cx}" cy="${cy}" r="${r}" fill="${color}" opacity="${opacity}" />`);
            } else if (shapeType === "rect") {
                const x = Math.random() * 300 + 20;
                const y = Math.random() * 300 + 20;
                const w = Math.random() * 130 + 40;
                const h = Math.random() * 130 + 40;
                const rx = Math.random() * 30;
                shapes.push(`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${color}" opacity="${opacity}" />`);
            } else if (shapeType === "ellipse") {
                const cx = Math.random() * 350 + 25;
                const cy = Math.random() * 350 + 25;
                const rx = Math.random() * 70 + 30;
                const ry = Math.random() * 60 + 20;
                shapes.push(`<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${color}" opacity="${opacity}" />`);
            } else {
                // path: wavy line
                let points = [];
                for (let j = 0; j < 4; j++) {
                    points.push(`${50 + j * 100},${Math.random() * 200 + 100}`);
                }
                const strokeWidth = Math.floor(Math.random() * 6) + 3;
                shapes.push(`<path d="M ${points[0]} Q ${points[1]} ${points[2]} ${points[3]}" stroke="${color}" stroke-width="${strokeWidth}" fill="none" opacity="${opacity}" />`);
            }
        }
        return `<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
            <rect width="400" height="400" fill="#f8f9fa" />
            ${shapes.join("")}
        </svg>`;
    }
    
    function randomItem(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }
    
    function updateArt() {
        const svgString = generateSVG(currentMood);
        document.getElementById("svgContainer").innerHTML = svgString;
        // update color palette display
        const colors = moodColors[currentMood];
        const paletteDiv = document.getElementById("colorPalette");
        paletteDiv.innerHTML = colors.map(c => `<div class="color-swatch" style="background: ${c};"></div>`).join("");
    }
    
    // mood selection
    document.querySelectorAll('.mood-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMood = btn.getAttribute('data-mood');
            updateArt();
        });
    });
    
    document.getElementById('refreshBtn').addEventListener('click', () => {
        updateArt();
    });
    
    // initial load
    updateArt();
    document.querySelector('.mood-btn[data-mood="calm"]').classList.add('active');
</script>
</body>
</html>
"""

# ---------- HTTP REQUEST HANDLER ----------
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        else:
            super().do_GET()

# ---------- START SERVER ----------
def main():
    PORT = 8080
    Handler = CustomHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n✨ Mood Color Canvas is running!")
        print(f"🌐 Open your browser to: http://localhost:{PORT}\n")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped. Goodbye!")
            httpd.shutdown()

if __name__ == "__main__":
    main()