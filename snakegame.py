import tkinter as tk
import random
import json
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ============================================================
# Constants & Configuration
# ============================================================

GRID_SIZE = 20          # 20x20 grid
CELL_SIZE = 25          # pixels per cell
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE

# Game speeds (delay in milliseconds)
INITIAL_DELAY = 150
MIN_DELAY = 60
SPEED_INCREMENT = 3     # decrease delay by this each time speed increases

# Scoring
REGULAR_FOOD_SCORE = 1
BONUS_FOOD_SCORE = 5

# Bonus food settings
BONUS_FOOD_CHANCE = 0.25        # 25% chance to spawn after eating any food
BONUS_FOOD_LIFESPAN = 4000      # milliseconds (4 seconds)

# Colors (modern, visually appealing)
COLOR_BG = "#1e1e2f"
COLOR_GRID_LINE = "#2a2a3c"
COLOR_SNAKE_HEAD = "#6c5ce7"
COLOR_SNAKE_BODY = "#a29bfe"
COLOR_FOOD = "#e84393"
COLOR_BONUS_FOOD = "#fdcb6e"
COLOR_TEXT = "#dfe6e9"
COLOR_GAME_OVER = "#ff7675"

# File to store high score
HIGHSCORE_FILE = "snake_highscore.json"


# ============================================================
# Data Models
# ============================================================

@dataclass
class Point:
    x: int
    y: int

    def as_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class Snake:
    def __init__(self, start_pos: Point, start_length: int = 3):
        self.segments: List[Point] = []
        # Build snake horizontally
        for i in range(start_length):
            self.segments.append(Point(start_pos.x - i, start_pos.y))
        self.direction = Point(1, 0)      # moving right initially
        self.next_direction = Point(1, 0)

    def head(self) -> Point:
        return self.segments[0]

    def change_direction(self, new_dir: Point) -> None:
        # Prevent 180-degree turns
        if (self.direction.x != -new_dir.x) or (self.direction.y != -new_dir.y):
            self.next_direction = new_dir

    def update_direction(self) -> None:
        self.direction = self.next_direction

    def move(self, grow: bool = False) -> None:
        new_head = Point(
            self.head().x + self.direction.x,
            self.head().y + self.direction.y
        )
        self.segments.insert(0, new_head)
        if not grow:
            self.segments.pop()

    def collides_with_self(self) -> bool:
        head = self.head()
        return any(segment == head for segment in self.segments[1:])

    def get_all_positions(self) -> set:
        return {segment.as_tuple() for segment in self.segments}


# ============================================================
# Game Manager
# ============================================================

class SnakeGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⚡ SNAKE: GOLDEN EDITION ⚡")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        # Canvas for drawing game
        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT, bg=COLOR_BG, highlightthickness=0
        )
        self.canvas.pack(pady=10)

        # Score panel
        self.info_frame = tk.Frame(root, bg=COLOR_BG)
        self.info_frame.pack(pady=(0, 10))

        self.score_label = tk.Label(
            self.info_frame, text="SCORE: 0", font=("Courier", 14, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG
        )
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.highscore_label = tk.Label(
            self.info_frame, text="HIGH: 0", font=("Courier", 14, "bold"),
            fg="#fdcb6e", bg=COLOR_BG
        )
        self.highscore_label.pack(side=tk.LEFT, padx=20)

        self.speed_label = tk.Label(
            self.info_frame, text="SPEED: 1", font=("Courier", 12),
            fg="#81ecec", bg=COLOR_BG
        )
        self.speed_label.pack(side=tk.LEFT, padx=20)

        # Initialize timer IDs (FIX: define them before calling reset_game)
        self.game_loop_id = None
        self.bonus_timer_id = None

        # Game state
        self.reset_game()

        # Bind keys
        self.root.bind("<Up>", lambda e: self.change_direction(Point(0, -1)))
        self.root.bind("<Down>", lambda e: self.change_direction(Point(0, 1)))
        self.root.bind("<Left>", lambda e: self.change_direction(Point(-1, 0)))
        self.root.bind("<Right>", lambda e: self.change_direction(Point(1, 0)))
        self.root.bind("<r>", lambda e: self.restart())
        self.root.bind("<R>", lambda e: self.restart())

        # Start game loop
        self.running = True
        self._schedule_game_loop()

    # --------------------------------------------------------
    # Game State Management
    # --------------------------------------------------------
    def reset_game(self) -> None:
        """Reset all game variables to start a fresh game."""
        # Cancel any pending timers
        if self.bonus_timer_id:
            self.root.after_cancel(self.bonus_timer_id)
            self.bonus_timer_id = None
        if self.game_loop_id:
            self.root.after_cancel(self.game_loop_id)
            self.game_loop_id = None

        # Snake initialization
        start_pos = Point(GRID_SIZE // 2, GRID_SIZE // 2)
        self.snake = Snake(start_pos, start_length=3)
        self.score = 0
        self.current_delay = INITIAL_DELAY
        self.running = True
        self.game_over_flag = False

        # Food & bonus
        self.food: Optional[Point] = None
        self.bonus_food: Optional[Point] = None
        self._generate_food()

        # Update UI
        self._update_score_display()
        self._draw_grid()
        self._draw_all()

    def restart(self) -> None:
        """Public method to restart the game."""
        self.reset_game()
        # ensure game loop is running
        if not self.game_loop_id:
            self._schedule_game_loop()

    def _update_score_display(self) -> None:
        self.score_label.config(text=f"SCORE: {self.score}")
        # Load and update high score
        high = self._load_highscore()
        if self.score > high:
            self._save_highscore(self.score)
            high = self.score
        self.highscore_label.config(text=f"HIGH: {high}")
        # Speed level display
        speed_lvl = max(1, (INITIAL_DELAY - self.current_delay) // SPEED_INCREMENT + 1)
        self.speed_label.config(text=f"SPEED: {speed_lvl}")

    # --------------------------------------------------------
    # Highscore persistence (JSON file, no extra installs)
    # --------------------------------------------------------
    def _load_highscore(self) -> int:
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("highscore", 0)
            except:
                return 0
        return 0

    def _save_highscore(self, value: int) -> None:
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                json.dump({"highscore": value}, f)
        except:
            pass  # Silent fail, not critical

    # --------------------------------------------------------
    # Food Generation Logic
    # --------------------------------------------------------
    def _get_free_cells(self) -> List[Tuple[int, int]]:
        """Return all grid cells not occupied by snake or bonus food (if any)."""
        occupied = self.snake.get_all_positions()
        if self.bonus_food:
            occupied.add(self.bonus_food.as_tuple())
        if self.food:
            occupied.add(self.food.as_tuple())
        free = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if (x, y) not in occupied:
                    free.append((x, y))
        return free

    def _generate_food(self) -> bool:
        """Place regular food at a random free cell. Returns False if no free cells (win)."""
        free_cells = self._get_free_cells()
        if not free_cells:
            self._game_over(victory=True)
            return False
        x, y = random.choice(free_cells)
        self.food = Point(x, y)
        return True

    def _spawn_bonus_food(self) -> None:
        """Spawn bonus food if there's no bonus already and free cells exist."""
        if self.bonus_food is not None:
            return
        free_cells = self._get_free_cells()
        # Exclude current regular food from free cells? Already handled in _get_free_cells.
        if not free_cells:
            return
        x, y = random.choice(free_cells)
        self.bonus_food = Point(x, y)

        # Schedule removal after lifespan
        if self.bonus_timer_id:
            self.root.after_cancel(self.bonus_timer_id)
        self.bonus_timer_id = self.root.after(BONUS_FOOD_LIFESPAN, self._remove_bonus_food)

    def _remove_bonus_food(self) -> None:
        """Remove bonus food and cancel timer."""
        self.bonus_food = None
        self.bonus_timer_id = None

    # --------------------------------------------------------
    # Game Logic (Movement, Collisions, Eating)
    # --------------------------------------------------------
    def _apply_direction_change(self) -> None:
        self.snake.update_direction()

    def _move_snake(self) -> bool:
        """Move snake one step. Returns True if game continues, False if game over."""
        # Determine if we will eat anything on this move
        new_head = Point(
            self.snake.head().x + self.snake.direction.x,
            self.snake.head().y + self.snake.direction.y
        )
        will_eat_regular = (self.food and new_head == self.food)
        will_eat_bonus = (self.bonus_food and new_head == self.bonus_food)

        grow = will_eat_regular or will_eat_bonus
        self.snake.move(grow)

        # Check collisions
        head = self.snake.head()
        # Wall collision
        if not (0 <= head.x < GRID_SIZE and 0 <= head.y < GRID_SIZE):
            self._game_over(victory=False)
            return False
        # Self collision
        if self.snake.collides_with_self():
            self._game_over(victory=False)
            return False

        # Handle eating regular food
        if will_eat_regular:
            self.score += REGULAR_FOOD_SCORE
            self._update_score_display()
            self._adjust_speed()
            if not self._generate_food():
                return False  # Victory triggered inside
            # Chance to spawn bonus food
            if random.random() < BONUS_FOOD_CHANCE:
                self._spawn_bonus_food()

        # Handle eating bonus food
        if will_eat_bonus:
            self.score += BONUS_FOOD_SCORE
            self._update_score_display()
            self._adjust_speed()
            # Remove bonus food and cancel its timer
            if self.bonus_timer_id:
                self.root.after_cancel(self.bonus_timer_id)
                self.bonus_timer_id = None
            self.bonus_food = None
            # Bonus eating doesn't generate new regular food, but we can still try bonus spawn again
            if random.random() < BONUS_FOOD_CHANCE:
                self._spawn_bonus_food()

        return True

    def _adjust_speed(self) -> None:
        """Increase game speed as score increases."""
        # Every 5 points, increase speed (decrease delay)
        target_delay = INITIAL_DELAY - (self.score // 5) * SPEED_INCREMENT
        if target_delay < MIN_DELAY:
            target_delay = MIN_DELAY
        self.current_delay = target_delay
        self._update_score_display()

    def _game_over(self, victory: bool = False) -> None:
        """Handle game over state."""
        if not self.running:
            return
        self.running = False
        self.game_over_flag = True
        # Cancel bonus timer if active
        if self.bonus_timer_id:
            self.root.after_cancel(self.bonus_timer_id)
            self.bonus_timer_id = None

        # Draw game over message
        self.canvas.create_rectangle(
            0, HEIGHT//2 - 40, WIDTH, HEIGHT//2 + 40,
            fill="#2d2d44", outline="", stipple="gray50"
        )
        msg = "✨ YOU WIN! ✨" if victory else "💀 GAME OVER 💀"
        self.canvas.create_text(
            WIDTH//2, HEIGHT//2 - 15, text=msg,
            fill=COLOR_GAME_OVER, font=("Courier", 20, "bold")
        )
        self.canvas.create_text(
            WIDTH//2, HEIGHT//2 + 20, text="Press  R  to restart",
            fill=COLOR_TEXT, font=("Courier", 12)
        )

    # --------------------------------------------------------
    # Drawing (Grid, Snake, Food)
    # --------------------------------------------------------
    def _draw_grid(self) -> None:
        """Draw subtle grid lines."""
        self.canvas.delete("grid")
        for x in range(0, WIDTH, CELL_SIZE):
            self.canvas.create_line(x, 0, x, HEIGHT, fill=COLOR_GRID_LINE, tags="grid")
        for y in range(0, HEIGHT, CELL_SIZE):
            self.canvas.create_line(0, y, WIDTH, y, fill=COLOR_GRID_LINE, tags="grid")

    def _draw_snake(self) -> None:
        for idx, segment in enumerate(self.snake.segments):
            x1 = segment.x * CELL_SIZE
            y1 = segment.y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            color = COLOR_SNAKE_HEAD if idx == 0 else COLOR_SNAKE_BODY
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=color, outline=COLOR_BG, width=2, tags="snake"
            )

    def _draw_food(self) -> None:
        if self.food:
            x1 = self.food.x * CELL_SIZE
            y1 = self.food.y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_oval(
                x1+2, y1+2, x2-2, y2-2, fill=COLOR_FOOD, outline="#d63031", width=1, tags="food"
            )

    def _draw_bonus(self) -> None:
        if self.bonus_food:
            x1 = self.bonus_food.x * CELL_SIZE
            y1 = self.bonus_food.y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            # Star shape illusion (just a diamond-like fill)
            self.canvas.create_rectangle(
                x1+3, y1+3, x2-3, y2-3, fill=COLOR_BONUS_FOOD, outline="#e17055", width=2, tags="bonus"
            )
            # Glow effect
            self.canvas.create_text(
                x1 + CELL_SIZE//2, y1 + CELL_SIZE//2,
                text="⭐", fill="#2d3436", font=("Arial", 14), tags="bonus"
            )

    def _draw_all(self) -> None:
        """Redraw entire game scene."""
        self.canvas.delete("snake", "food", "bonus")
        self._draw_snake()
        self._draw_food()
        self._draw_bonus()

    # --------------------------------------------------------
    # Game Loop & Event Handling
    # --------------------------------------------------------
    def change_direction(self, new_dir: Point) -> None:
        if self.running and not self.game_over_flag:
            self.snake.change_direction(new_dir)

    def _game_step(self) -> None:
        """One iteration of the game loop."""
        if not self.running:
            return

        self._apply_direction_change()
        continue_game = self._move_snake()
        self._draw_all()

        if continue_game:
            self._schedule_game_loop()
        else:
            self.game_loop_id = None  # game over, loop stopped

    def _schedule_game_loop(self) -> None:
        """Schedule the next game step using current delay."""
        if self.running:
            self.game_loop_id = self.root.after(self.current_delay, self._game_step)


# ============================================================
# Application Entry Point
# ============================================================

def main():
    root = tk.Tk()
    game = SnakeGame(root)
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (WIDTH // 2)
    y = (root.winfo_screenheight() // 2) - (HEIGHT // 2) - 50
    root.geometry(f"{WIDTH}x{HEIGHT+80}+{x}+{y}")
    root.mainloop()


if __name__ == "__main__":
    main()