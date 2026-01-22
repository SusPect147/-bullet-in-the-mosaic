import arcade
import random
import time
import math

# ---------------- НАСТРОЙКИ ----------------
WALL = 10
PASSAGE = 40
CELL = WALL + PASSAGE
COLS = 12
ROWS = 12

MAZE_WIDTH = COLS * CELL + WALL
MAZE_HEIGHT = ROWS * CELL + WALL
SCREEN_WIDTH = MAZE_WIDTH
SCREEN_HEIGHT = MAZE_HEIGHT + 90
HUD_HEIGHT = SCREEN_HEIGHT - MAZE_HEIGHT

WINDOW_TITLE = "bullet-in-the-mosaic"

BACKGROUND_COLOR = arcade.color.BLACK
HUD_COLOR = arcade.color.DARK_GRAY
WALL_COLOR = arcade.color.GRAY
START_COLOR = arcade.color.GREEN
END_COLOR = arcade.color.RED
TITLE_COLOR = arcade.color.WHITE
SUBTITLE_COLOR = arcade.color.GRAY

START_SIZE = 20
END_SIZE = 20

BUTTON_COLOR = arcade.color.LIGHT_GRAY
BUTTON_HOVER_COLOR = arcade.color.GRAY
BUTTON_TEXT_COLOR = arcade.color.BLACK

COOLDOWN_MAX = 7  # секунд


def center_to_lbwh(cx, cy, w, h):
    """Конвертируем центр в left-bottom-width-height"""
    return cx - w / 2, cy - h / 2, w, h


def _draw_rectangle_filled_center(cx, cy, w, h, color):
    hw = w / 2
    hh = h / 2
    points = [
        (cx - hw, cy - hh),
        (cx + hw, cy - hh),
        (cx + hw, cy + hh),
        (cx - hw, cy + hh),
    ]
    arcade.draw_polygon_filled(points, color)


class Bullet:
    def __init__(self, x, y, dx, dy, radius=5, color=arcade.color.WHITE):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.color = color

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.show_start_screen = True
        self.room_number = 1

        self.vertical_walls = []
        self.horizontal_walls = []

        self.start_rect = None
        self.end_rect = None

        # HUD
        self.room_text = f"Комната: {self.room_number}"

        # Кнопки
        self.cooldown = 0
        self.last_shield_time = 0
        self.shield_active = False
        self.shield_button = (SCREEN_WIDTH / 2 - 90, MAZE_HEIGHT + HUD_HEIGHT / 2 - 20, 180, 40)
        self.menu_button = (SCREEN_WIDTH - 190, MAZE_HEIGHT + HUD_HEIGHT / 2 - 20, 180, 40)

        # Пуля
        self.bullet = None
        self.bullet_active = False

        # Линия при наведении
        self.aim_line = None

        # Координаты мыши
        self._mouse_x = 0
        self._mouse_y = 0

        self.generate_maze()

    # ---------------- ГЕНЕРАЦИЯ ЛАБИРИНТА ----------------
    def generate_maze(self):
        self.vertical_walls.clear()
        self.horizontal_walls.clear()

        v_walls = [[True for _ in range(COLS + 1)] for _ in range(ROWS)]
        h_walls = [[True for _ in range(COLS)] for _ in range(ROWS + 1)]
        visited = [[False for _ in range(COLS)] for _ in range(ROWS)]

        def dfs(r, c):
            visited[r][c] = True
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and not visited[nr][nc]:
                    if dr == 0 and dc == 1:
                        v_walls[r][c + 1] = False
                    elif dr == 0 and dc == -1:
                        v_walls[r][c] = False
                    elif dr == 1 and dc == 0:
                        h_walls[r + 1][c] = False
                    elif dr == -1 and dc == 0:
                        h_walls[r][c] = False
                    dfs(nr, nc)

        dfs(0, 0)

        for r in range(ROWS):
            for c in range(COLS + 1):
                if v_walls[r][c]:
                    self.vertical_walls.append(center_to_lbwh(c * CELL + WALL / 2, r * CELL + CELL / 2, WALL, CELL))
        for r in range(ROWS + 1):
            for c in range(COLS):
                if h_walls[r][c]:
                    self.horizontal_walls.append(center_to_lbwh(c * CELL + CELL / 2, r * CELL + WALL / 2, CELL, WALL))

        self.start_rect = center_to_lbwh(WALL + PASSAGE / 2, WALL + PASSAGE / 2, START_SIZE, START_SIZE)
        self.end_rect = center_to_lbwh(MAZE_WIDTH - WALL - PASSAGE / 2, MAZE_HEIGHT - WALL - PASSAGE / 2, END_SIZE,
                                       END_SIZE)

        self.room_text = f"Комната: {self.room_number}"
        self.bullet_active = False
        self.bullet = None

    # ---------------- ОТРИСОВКА ----------------
    def on_draw(self):
        self.clear()

        if self.show_start_screen:
            arcade.draw_text("bullet-in-the-mosaic", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40,
                             TITLE_COLOR, 36, anchor_x="center", anchor_y="center")
            arcade.draw_text("нажмите любую клавишу или кнопку мыши, чтобы начать играть",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20, SUBTITLE_COLOR, 14,
                             anchor_x="center", anchor_y="center")
            return

        _draw_rectangle_filled_center(SCREEN_WIDTH / 2, MAZE_HEIGHT + HUD_HEIGHT / 2, SCREEN_WIDTH, HUD_HEIGHT, HUD_COLOR)
        arcade.draw_text(self.room_text, 10, MAZE_HEIGHT + HUD_HEIGHT / 2, arcade.color.BLACK, 18, anchor_y="center")

        self.draw_button(self.shield_button,
                         f"Остановить пулю (КД: {self.get_cooldown()})" if self.cooldown > 0 else "Остановить пулю")
        self.draw_button(self.menu_button, "Главное меню")

        for x, y, w, h in self.vertical_walls + self.horizontal_walls:
            _draw_rectangle_filled_center(x + w / 2, y + h / 2, w, h, WALL_COLOR)

        sx, sy, sw, sh = self.start_rect
        _draw_rectangle_filled_center(sx + sw / 2, sy + sh / 2, sw, sh, START_COLOR)
        ex, ey, ew, eh = self.end_rect
        _draw_rectangle_filled_center(ex + ew / 2, ey + eh / 2, ew, eh, END_COLOR)

        if self.aim_line:
            arcade.draw_line(*self.aim_line, arcade.color.RED, 4)

        if self.bullet_active and self.bullet:
            self.bullet.draw()

    def draw_button(self, rect, text):
        x, y, w, h = rect
        color = BUTTON_COLOR
        if x < self._mouse_x < x + w and y < self._mouse_y < y + h:
            color = BUTTON_HOVER_COLOR
        _draw_rectangle_filled_center(x + w / 2, y + h / 2, w, h, color)
        arcade.draw_text(text, x + w / 2, y + h / 2, BUTTON_TEXT_COLOR, 14, anchor_x="center", anchor_y="center")

    def get_cooldown(self):
        if self.cooldown == 0:
            self.shield_active = False
            return 0
        elapsed = time.time() - self.last_shield_time
        remaining = max(0, int(self.cooldown - elapsed))
        if remaining == 0:
            self.cooldown = 0
            self.shield_active = False
        return remaining

    # ---------------- ЛОГИКА ПУЛИ ----------------
    def on_update(self, delta_time):
        sx, sy, sw, sh = self.start_rect
        start_x = sx + sw / 2
        start_y = sy + sh / 2
        mx, my = self._mouse_x, self._mouse_y

        # направление линии
        dx = mx - start_x
        dy = my - start_y
        length = math.hypot(dx, dy)
        if length == 0:
            length = 1
        dx /= length
        dy /= length

        max_distance = 5000  # линия до "бесконечности"
        end_x = start_x + dx * max_distance
        end_y = start_y + dy * max_distance

        # находим ближайшее пересечение с любой стеной
        for wx, wy, ww, wh in self.vertical_walls + self.horizontal_walls:
            wall_left = wx
            wall_right = wx + ww
            wall_bottom = wy
            wall_top = wy + wh

            # проверяем пересечение с вертикальными стенами
            if dx != 0:
                t1 = (wall_left - start_x) / dx
                t2 = (wall_right - start_x) / dx
                for t in [t1, t2]:
                    if t > 0:
                        y_hit = start_y + dy * t
                        if wall_bottom <= y_hit <= wall_top:
                            if t * length < math.hypot(end_x - start_x, end_y - start_y):
                                end_x = start_x + dx * t
                                end_y = y_hit

            # проверяем пересечение с горизонтальными стенами
            if dy != 0:
                t1 = (wall_bottom - start_y) / dy
                t2 = (wall_top - start_y) / dy
                for t in [t1, t2]:
                    if t > 0:
                        x_hit = start_x + dx * t
                        if wall_left <= x_hit <= wall_right:
                            if t * length < math.hypot(end_x - start_x, end_y - start_y):
                                end_x = x_hit
                                end_y = start_y + dy * t

        self.aim_line = (start_x, start_y, end_x, end_y)

        # ---------------- движение пули ----------------
        if self.bullet_active and self.bullet:
            next_x = self.bullet.x + self.bullet.dx
            next_y = self.bullet.y + self.bullet.dy

            collided = False
            for wx, wy, ww, wh in self.vertical_walls + self.horizontal_walls:
                wall_left = wx
                wall_right = wx + ww
                wall_bottom = wy
                wall_top = wy + wh

                if wall_left - self.bullet.radius <= next_x <= wall_right + self.bullet.radius and \
                        wall_bottom - self.bullet.radius <= next_y <= wall_top + self.bullet.radius:
                    collided = True
                    dist_left = abs(next_x - wall_left)
                    dist_right = abs(next_x - wall_right)
                    dist_bottom = abs(next_y - wall_bottom)
                    dist_top = abs(next_y - wall_top)
                    min_dist = min(dist_left, dist_right, dist_bottom, dist_top)

                    if min_dist == dist_left or min_dist == dist_right:
                        self.bullet.dx *= -1
                        next_x = self.bullet.x
                    else:
                        self.bullet.dy *= -1
                        next_y = self.bullet.y

            if not collided:
                self.bullet.x = next_x
                self.bullet.y = next_y
            else:
                self.bullet.x = next_x
                self.bullet.y = next_y

            # Попадание в красный куб
            ex, ey, ew, eh = self.end_rect
            if ex <= self.bullet.x <= ex + ew and ey <= self.bullet.y <= ey + eh:
                self.room_number += 1
                self.generate_maze()
                self.bullet_active = False
                self.bullet = None

    # ---------------- ВВОД ----------------
    def on_key_press(self, key, modifiers):
        if self.show_start_screen:
            self.show_start_screen = False
            return
        if key == arcade.key.SPACE:
            self.room_number += 1
            self.generate_maze()
        if key == arcade.key.ESCAPE:
            self.close()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_start_screen:
            self.show_start_screen = False
            return

        if self.point_in_rect(x, y, self.shield_button) and self.cooldown == 0:
            if self.bullet_active and self.bullet:
                cx, cy, w, h = self.start_rect
                self.start_rect = center_to_lbwh(self.bullet.x, self.bullet.y, w, h)
                self.bullet_active = False
                self.bullet = None

            self.cooldown = COOLDOWN_MAX
            self.last_shield_time = time.time()
            self.shield_active = True

        elif self.point_in_rect(x, y, self.menu_button):
            self.show_start_screen = True
        else:
            if not self.bullet_active:
                sx, sy, sw, sh = self.start_rect
                start_x = sx + sw / 2
                start_y = sy + sh / 2
                dx = x - start_x
                dy = y - start_y
                length = math.hypot(dx, dy)
                if length != 0:
                    dx /= length
                    dy /= length
                    speed = 10
                    self.bullet = Bullet(start_x, start_y, dx * speed, dy * speed)
                    self.bullet_active = True
                    self.aim_line = None

    def on_mouse_motion(self, x, y, dx, dy):
        self._mouse_x = x
        self._mouse_y = y

    @staticmethod
    def point_in_rect(px, py, rect):
        x, y, w, h = rect
        return x <= px <= x + w and y <= py <= y + h


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
