import arcade
import random
import time
import math

WALL = 10
PASSAGE = 40
CELL = WALL + PASSAGE
COLS = 12
ROWS = 12

WALL_OVERLAP = 1.5

MAZE_WIDTH = COLS * CELL + WALL
MAZE_HEIGHT = ROWS * CELL + WALL
SCREEN_WIDTH = MAZE_WIDTH
SCREEN_HEIGHT = MAZE_HEIGHT + 90
HUD_HEIGHT = SCREEN_HEIGHT - MAZE_HEIGHT

WINDOW_TITLE = "bullet in the mosaic"

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

COOLDOWN_MAX = 7


def center_to_lbwh(cx, cy, w, h):
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

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)


class GameWindow(arcade.Window):
    def __init__(self):
        self.paused = False
        self.pause_start_time = time.time()

        self.bounce_sound = arcade.load_sound("assets/song2.mp3")
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
        arcade.set_background_color(BACKGROUND_COLOR)

        
        self.show_start_screen = True
        self.room_number = 1

        
        self.level_start_time = time.time()
        self.level_time = 0

        
        self.hud_y = MAZE_HEIGHT + HUD_HEIGHT // 2

        self.room_text_pos = (20, self.hud_y)

        
        self.timer_pos = (200, self.hud_y)

        
        self.shield_button = (250, self.hud_y - 15, 130, 30)
        self.menu_button = (400, self.hud_y - 15, 150, 30)


        
        self.start_continue_button = (
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 + 10,
            300,
            45,
        )
        self.start_new_button = (
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 - 55,
            300,
            45,
        )

        
        self.vertical_walls = []
        self.horizontal_walls = []

        self.start_rect = None
        self.end_rect = None

        self.bullet = None
        self.bullet_active = False
        self.aim_line = None

        
        self.cooldown = 0
        self.last_shield_time = 0
        self.shield_active = False

        
        self._mouse_x = 0
        self._mouse_y = 0

        self.generate_maze()

    

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
                    self.vertical_walls.append(
                        center_to_lbwh(
                            c * CELL + WALL / 2, r * CELL + CELL / 2, WALL, CELL
                        )
                    )

        for r in range(ROWS + 1):
            for c in range(COLS):
                if h_walls[r][c]:
                    self.horizontal_walls.append(
                        center_to_lbwh(
                            c * CELL + CELL / 2, r * CELL + WALL / 2, CELL, WALL
                        )
                    )

        self.start_rect = center_to_lbwh(
            WALL + PASSAGE / 2, WALL + PASSAGE / 2, START_SIZE, START_SIZE
        )
        self.end_rect = center_to_lbwh(
            MAZE_WIDTH - WALL - PASSAGE / 2,
            MAZE_HEIGHT - WALL - PASSAGE / 2,
            END_SIZE,
            END_SIZE,
        )

        self.room_text = f"Комната: {self.room_number}"
        self.bullet_active = False
        self.bullet = None
        self.aim_line = None
        self.shield_active = False

        
        self.level_start_time = time.time()
        self.level_time = 0


    def on_draw(self):
        self.clear()

        
        if self.show_start_screen:
            arcade.draw_text(
                "bullet in the mosaic",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 90,
                TITLE_COLOR,
                36,
                anchor_x="center",
            )

            
            self.draw_button(self.start_continue_button, "Продолжить прохождение")
            self.draw_button(self.start_new_button, "Начать заново")
            return

        
        _draw_rectangle_filled_center(
            SCREEN_WIDTH // 2,
            self.hud_y,
            SCREEN_WIDTH,
            HUD_HEIGHT,
            HUD_COLOR,
        )

        
        arcade.draw_text(
            f"Комната: {self.room_number}",
            *self.room_text_pos,
            arcade.color.BLACK,
            16,
            anchor_y="center",
        )

        
        arcade.draw_text(
            f"{self.level_time:.1f} сек",
            *self.timer_pos,
            arcade.color.BLACK,
            16,
            anchor_x="center",
            anchor_y="center",
        )

        
        shield_text = (
            f"Стоп пуля ({self.get_cooldown()})"
            if self.cooldown > 0
            else "Остановить пулю"
        )

        self.draw_button(self.shield_button, shield_text)
        self.draw_button(self.menu_button, "Главное меню")

        
        for x, y, w, h in self.vertical_walls + self.horizontal_walls:
            _draw_rectangle_filled_center(x + w / 2, y + h / 2, w, h, WALL_COLOR)

        
        sx, sy, sw, sh = self.start_rect
        _draw_rectangle_filled_center(sx + sw / 2, sy + sh / 2, sw, sh, START_COLOR)

        ex, ey, ew, eh = self.end_rect
        _draw_rectangle_filled_center(ex + ew / 2, ey + eh / 2, ew, eh, END_COLOR)

        
        if self.aim_line:
            arcade.draw_line(*self.aim_line, arcade.color.RED, 3)

        
        if self.bullet_active and self.bullet:
            self.bullet.draw()



    def draw_button(self, rect, text):
        x, y, w, h = rect
        color = BUTTON_COLOR
        if x < self._mouse_x < x + w and y < self._mouse_y < y + h:
            color = BUTTON_HOVER_COLOR
        _draw_rectangle_filled_center(x + w / 2, y + h / 2, w, h, color)
        arcade.draw_text(
            text,
            x + w / 2,
            y + h / 2,
            BUTTON_TEXT_COLOR,
            14,
            anchor_x="center",
            anchor_y="center",
        )

    def play_bounce(self):
        speed = math.hypot(self.bullet.dx, self.bullet.dy)
        volume = min(0.2 + speed / 50, 0.6)
        arcade.play_sound(self.bounce_sound, volume=volume)



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

    def on_update(self, delta_time):

        if self.show_start_screen or self.paused:
            return


        self.level_time = time.time() - self.level_start_time

        sx, sy, sw, sh = self.start_rect
        start_x = sx + sw / 2
        start_y = sy + sh / 2
        mx, my = self._mouse_x, self._mouse_y

        raw_dx = mx - start_x
        raw_dy = my - start_y
        raw_dist = math.hypot(raw_dx, raw_dy)
        if raw_dist == 0:
            unit_dx, unit_dy = 1.0, 0.0
        else:
            unit_dx, unit_dy = raw_dx / raw_dist, raw_dy / raw_dist

        max_distance = 5000.0
        closest_t = max_distance
        hit_x = start_x + unit_dx * max_distance
        hit_y = start_y + unit_dy * max_distance

        walls = self.vertical_walls + self.horizontal_walls
        for wx, wy, ww, wh in walls:
            wall_left = wx
            wall_right = wx + ww
            wall_bottom = wy
            wall_top = wy + wh

            if abs(unit_dx) > 1e-9:
                for x_side in (wall_left, wall_right):
                    t = (x_side - start_x) / unit_dx
                    if t > 0 and t < closest_t:
                        y_hit = start_y + unit_dy * t
                        if wall_bottom - 1e-6 <= y_hit <= wall_top + 1e-6:
                            closest_t = t
                            hit_x = x_side
                            hit_y = y_hit

            if abs(unit_dy) > 1e-9:
                for y_side in (wall_bottom, wall_top):
                    t = (y_side - start_y) / unit_dy
                    if t > 0 and t < closest_t:
                        x_hit = start_x + unit_dx * t
                        if wall_left - 1e-6 <= x_hit <= wall_right + 1e-6:
                            closest_t = t
                            hit_x = x_hit
                            hit_y = y_side

        self.aim_line = (start_x, start_y, hit_x, hit_y)

        if self.bullet_active and self.bullet:
            b = self.bullet
            new_x = b.x
            new_y = b.y

            tentative_x = b.x + b.dx
            tentative_y = b.y + b.dy

            radius = b.radius

            nearest_x_collision = None
            nearest_x_dist = float("inf")
            if b.dx > 0:
                for wx, wy, ww, wh in walls:
                    wall_left = wx
                    wall_right = wx + ww
                    wall_bottom = wy
                    wall_top = wy + wh
                    if new_y + radius > wall_bottom and new_y - radius < wall_top:
                        collision_x = wall_left - radius
                        if new_x < collision_x <= tentative_x:
                            dist = collision_x - new_x
                            if dist < nearest_x_dist:
                                nearest_x_dist = dist
                                nearest_x_collision = (
                                    collision_x,
                                    wall_left,
                                    wall_right,
                                    wall_bottom,
                                    wall_top,
                                )
            elif b.dx < 0:
                for wx, wy, ww, wh in walls:
                    wall_left = wx
                    wall_right = wx + ww
                    wall_bottom = wy
                    wall_top = wy + wh
                    if new_y + radius > wall_bottom and new_y - radius < wall_top:
                        collision_x = wall_right + radius
                        if tentative_x <= collision_x < new_x:
                            dist = new_x - collision_x
                            if dist < nearest_x_dist:
                                nearest_x_dist = dist
                                nearest_x_collision = (
                                    collision_x,
                                    wall_left,
                                    wall_right,
                                    wall_bottom,
                                    wall_top,
                                )

            if nearest_x_collision:

                (
                    col_x,
                    wall_left,
                    wall_right,
                    wall_bottom,
                    wall_top,
                ) = nearest_x_collision
                new_x = col_x
                b.dx *= -1
                self.play_bounce()
            else:
                new_x = tentative_x

            nearest_y_collision = None
            nearest_y_dist = float("inf")
            if b.dy > 0:
                for wx, wy, ww, wh in walls:
                    wall_left = wx
                    wall_right = wx + ww
                    wall_bottom = wy
                    wall_top = wy + wh
                    if new_x + radius > wall_left and new_x - radius < wall_right:
                        collision_y = wall_bottom - radius
                        if new_y < collision_y <= tentative_y:
                            dist = collision_y - new_y
                            if dist < nearest_y_dist:
                                nearest_y_dist = dist
                                nearest_y_collision = (
                                    collision_y,
                                    wall_left,
                                    wall_right,
                                    wall_bottom,
                                    wall_top,
                                )
            elif b.dy < 0:
                for wx, wy, ww, wh in walls:
                    wall_left = wx
                    wall_right = wx + ww
                    wall_bottom = wy
                    wall_top = wy + wh
                    if new_x + radius > wall_left and new_x - radius < wall_right:
                        collision_y = wall_top + radius
                        if tentative_y <= collision_y < new_y:
                            dist = new_y - collision_y
                            if dist < nearest_y_dist:
                                nearest_y_dist = dist
                                nearest_y_collision = (
                                    collision_y,
                                    wall_left,
                                    wall_right,
                                    wall_bottom,
                                    wall_top,
                                )

            if nearest_y_collision:
                (
                    col_y,
                    wall_left,
                    wall_right,
                    wall_bottom,
                    wall_top,
                ) = nearest_y_collision
                new_y = col_y
                b.dy *= -1
                self.play_bounce()
            else:
                new_y = tentative_y

            pushed_out = False
            for wx, wy, ww, wh in walls:
                wall_left = wx
                wall_right = wx + ww
                wall_bottom = wy
                wall_top = wy + wh
                if (
                    new_x + radius > wall_left
                    and new_x - radius < wall_right
                    and new_y + radius > wall_bottom
                    and new_y - radius < wall_top
                ):
                    overlap_left = abs((new_x + radius) - wall_left)
                    overlap_right = abs(wall_right - (new_x - radius))
                    overlap_bottom = abs((new_y + radius) - wall_bottom)
                    overlap_top = abs(wall_top - (new_y - radius))
                    min_overlap = min(
                        overlap_left, overlap_right, overlap_bottom, overlap_top
                    )
                    if min_overlap == overlap_left:
                        new_x = wall_left - radius
                        b.dx = -abs(b.dx)
                    elif min_overlap == overlap_right:
                        new_x = wall_right + radius
                        b.dx = abs(b.dx)
                    elif min_overlap == overlap_bottom:
                        new_y = wall_bottom - radius
                        b.dy = -abs(b.dy)
                    else:
                        new_y = wall_top + radius
                        b.dy = abs(b.dy)
                    pushed_out = True

            if not pushed_out:
                b.x = new_x
                b.y = new_y
            else:
                b.x = new_x
                b.y = new_y

            ex, ey, ew, eh = self.end_rect
            if ex <= b.x <= ex + ew and ey <= b.y <= ey + eh:
                self.room_number += 1
                self.generate_maze()
                self.bullet_active = False
                self.bullet = None

    def on_key_press(self, key, modifiers):

        if self.show_start_screen:
            self.show_start_screen = False
            pause_duration = time.time() - self.pause_start_time
            self.level_start_time += pause_duration
            self.paused = False

            return
        if key == arcade.key.SPACE:
            self.room_number += 1
            self.generate_maze()
        if key == arcade.key.ESCAPE:
            self.close()

    def on_mouse_press(self, x, y, button, modifiers):

        if self.show_start_screen:
            
            if self.point_in_rect(x, y, self.start_continue_button):
                self.show_start_screen = False
                pause_duration = time.time() - self.pause_start_time
                self.level_start_time += pause_duration
                self.paused = False

            elif self.point_in_rect(x, y, self.start_new_button):
                self.room_number = 1
                self.generate_maze()
                self.show_start_screen = False
                pause_duration = time.time() - self.pause_start_time
                self.level_start_time += pause_duration
                self.paused = False

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
            self.paused = True
            self.pause_start_time = time.time()
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