#!/usr/bin/env python3
"""
Retro Pixel Painter – cross‑platform terminal pixel art editor.
Works on Windows, Linux, and Mac.
"""

import os
import sys
import json
from datetime import datetime

# ---------- COLOR PALETTE ----------
COLORS = {
    '1': ('█', 'black', 0),
    '2': ('█', 'white', 15),
    '3': ('█', 'red', 1),
    '4': ('█', 'green', 2),
    '5': ('█', 'yellow', 3),
    '6': ('█', 'blue', 4),
    '7': ('█', 'magenta', 5),
    '8': ('█', 'cyan', 6),
}
BRUSH_SIZES = [1, 2, 3]

# ---------- CROSS-PLATFORM KEY INPUT ----------
if os.name == 'nt':
    import msvcrt
    def get_key():
        """Windows: get a single keypress without Enter."""
        key = msvcrt.getch()
        if key == b'\xe0':  # arrow keys
            arrow = msvcrt.getch()
            if arrow == b'H': return 'UP'
            if arrow == b'P': return 'DOWN'
            if arrow == b'M': return 'RIGHT'
            if arrow == b'K': return 'LEFT'
            return None
        try:
            return key.decode('ascii').lower()
        except:
            return None
else:
    import termios
    import tty
    def get_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'UP'
                    if ch3 == 'B': return 'DOWN'
                    if ch3 == 'C': return 'RIGHT'
                    if ch3 == 'D': return 'LEFT'
                return 'ESC'
            return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# ---------- PIXEL PAINTER CLASS ----------
class PixelPainter:
    def __init__(self, width=40, height=20):
        self.width = width
        self.height = height
        self.grid = [[{'char': '█', 'color': 0} for _ in range(width)] for _ in range(height)]
        self.cursor_x = width // 2
        self.cursor_y = height // 2
        self.current_color = 15  # white
        self.brush_size = 1
        self.message = ""

    def draw_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x]['color'] = color

    def draw_brush(self, x, y, color):
        half = self.brush_size // 2
        for dx in range(-half, half+1):
            for dy in range(-half, half+1):
                if abs(dx) + abs(dy) <= half + (self.brush_size % 2):
                    self.draw_pixel(x + dx, y + dy, color)

    def set_message(self, msg):
        self.message = msg

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        # header
        print(f"\033[48;5;0;37m Pixel Painter | {self.width}x{self.height} | brush: {self.brush_size} | color: {self._current_color_name()} \033[0m")
        print("")
        # grid
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                color_code = self.grid[y][x]['color']
                char = self.grid[y][x]['char']
                if x == self.cursor_x and y == self.cursor_y:
                    line += f"\033[48;5;7;30m{char}\033[0m"
                else:
                    line += f"\033[48;5;{color_code};38;5;{color_code}m{char}\033[0m"
            print(line)
        # footer
        print("\n" + "─" * self.width)
        print("[1-8] color | [B] brush | [S] save | [L] load | [C] clear | [E] export | [Q] quit")
        print("Arrow keys / WASD move | SPACE / ENTER draw")
        if self.message:
            print(f"\033[93m> {self.message}\033[0m")

    def _current_color_name(self):
        for k, v in COLORS.items():
            if v[2] == self.current_color:
                return v[1]
        return "?"

    def save_to_file(self, filename=None):
        if not filename:
            filename = f"pixelart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pixel"
        data = {
            'width': self.width,
            'height': self.height,
            'grid': [[p['color'] for p in row] for row in self.grid]
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        self.set_message(f"Saved to {filename}")

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.width = data['width']
            self.height = data['height']
            self.grid = [[{'char': '█', 'color': c} for c in row] for row in data['grid']]
            self.cursor_x = min(self.cursor_x, self.width-1)
            self.cursor_y = min(self.cursor_y, self.height-1)
            self.set_message(f"Loaded {filename}")
        except Exception as e:
            self.set_message(f"Error: {e}")

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x]['color'] = 0
        self.set_message("Canvas cleared")

    def export_ascii(self):
        lines = [''.join(self.grid[y][x]['char'] for x in range(self.width)) for y in range(self.height)]
        filename = f"ascii_art_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write('\n'.join(lines))
        self.set_message(f"ASCII export: {filename}")

# ---------- MAIN LOOP ----------
def main():
    painter = PixelPainter(width=40, height=20)
    painter.render()

    while True:
        key = get_key()
        if key is None:
            continue

        if key == 'q':
            painter.set_message("Goodbye!")
            break

        # movement: arrows or WASD
        if key in ('UP', 'w'):
            painter.cursor_y = max(0, painter.cursor_y - 1)
        elif key in ('DOWN', 's'):
            painter.cursor_y = min(painter.height-1, painter.cursor_y + 1)
        elif key in ('LEFT', 'a'):
            painter.cursor_x = max(0, painter.cursor_x - 1)
        elif key in ('RIGHT', 'd'):
            painter.cursor_x = min(painter.width-1, painter.cursor_x + 1)

        # draw
        elif key in (' ', '\r', '\n'):
            painter.draw_brush(painter.cursor_x, painter.cursor_y, painter.current_color)

        # colors 1-8
        elif key in '12345678':
            color_map = {'1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':15, '8':0}
            painter.current_color = color_map[key]
            painter.set_message(f"Color: {COLORS[key][1]}")

        # brush size
        elif key == 'b':
            idx = (BRUSH_SIZES.index(painter.brush_size) + 1) % len(BRUSH_SIZES)
            painter.brush_size = BRUSH_SIZES[idx]
            painter.set_message(f"Brush size = {painter.brush_size}")

        # save
        elif key == 's':
            painter.save_to_file()

        # load
        elif key == 'l':
            print("\nFilename: ", end='')
            sys.stdout.flush()
            if os.name == 'nt':
                fname = input().strip()
            else:
                # restore echo temporarily for Unix
                fd = sys.stdin.fileno()
                old = termios.tcgetattr(fd)
                try:
                    tty.setcbreak(fd)
                    fname = sys.stdin.readline().strip()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
            if fname:
                painter.load_from_file(fname)

        # clear
        elif key == 'c':
            painter.clear()

        # export ASCII
        elif key == 'e':
            painter.export_ascii()

        painter.render()

if __name__ == "__main__":
    main()