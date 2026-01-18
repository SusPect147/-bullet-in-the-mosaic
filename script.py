import arcade

# Размеры окна и зоны игры
SCREEN_WIDTH = 610
SCREEN_HEIGHT = 700
MAZE_HEIGHT = 610
HUD_HEIGHT = SCREEN_HEIGHT - MAZE_HEIGHT

WINDOW_TITLE = "Maze Prototype"

BACKGROUND_COLOR = arcade.color.BLACK
WALL_COLOR = arcade.color.GRAY
HUD_COLOR = arcade.color.DARK_GRAY


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, resizable=False)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.show_welcome = True
        self.room_number = 1

        # Стены лабиринта
        self.walls = arcade.SpriteList()
        self.create_maze_contour()

        # Координаты кнопки "Выйти" (центр кнопки)
        self.exit_button_x = SCREEN_WIDTH - 110
        self.exit_button_y = SCREEN_HEIGHT - HUD_HEIGHT / 2
        self.exit_button_width = 200
        self.exit_button_height = 30

    def create_maze_contour(self):
        """Создаёт контур лабиринта (4 стены). Цвет передаём именованным аргументом."""
        # Левая стена
        left_wall = arcade.SpriteSolidColor(10, MAZE_HEIGHT, color=WALL_COLOR)
        left_wall.left = 0
        left_wall.center_y = MAZE_HEIGHT / 2

        # Правая стена
        right_wall = arcade.SpriteSolidColor(10, MAZE_HEIGHT, color=WALL_COLOR)
        right_wall.right = SCREEN_WIDTH
        right_wall.center_y = MAZE_HEIGHT / 2

        # Нижняя стена
        bottom_wall = arcade.SpriteSolidColor(SCREEN_WIDTH, 10, color=WALL_COLOR)
        bottom_wall.bottom = 0
        bottom_wall.center_x = SCREEN_WIDTH / 2

        # Верхняя стена (под HUD)
        top_wall = arcade.SpriteSolidColor(SCREEN_WIDTH, 10, color=WALL_COLOR)
        top_wall.top = MAZE_HEIGHT
        top_wall.center_x = SCREEN_WIDTH / 2

        self.walls.extend([left_wall, right_wall, bottom_wall, top_wall])

    def on_draw(self):
        self.clear()

        if self.show_welcome:
            self.draw_welcome_screen()
        else:
            self.draw_hud()
            self.walls.draw()

    def draw_welcome_screen(self):
        arcade.draw_text(
            "Добро пожаловать, User",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.WHITE,
            36,
            anchor_x="center",
            anchor_y="center",
        )

        arcade.draw_text(
            "Нажмите любую клавишу или клик мышью",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 60,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
            anchor_y="center",
        )

    def draw_hud(self):
        """Рисует верхнюю панель с текстом и кнопкой.
        Используем функции draw_lbwh_* (левый-нижний угол + ширина + высота)."""
        hud_left = 0
        hud_bottom = SCREEN_HEIGHT - HUD_HEIGHT
        # Фон HUD (левый-нижний угол, ширина, высота)
        arcade.draw_lbwh_rectangle_filled(
            hud_left,
            hud_bottom,
            SCREEN_WIDTH,
            HUD_HEIGHT,
            HUD_COLOR
        )

        # Текст "Комната: N" слева (центруем по вертикали HUD)
        arcade.draw_text(
            f"Комната: {self.room_number}",
            10,
            hud_bottom + HUD_HEIGHT / 2,
            arcade.color.BLACK,
            18,
            anchor_x="left",
            anchor_y="center",
        )


        # Кнопка "Выйти" — вычисляем левый-нижний угол на основе центра
        button_left = self.exit_button_x - self.exit_button_width / 2
        button_bottom = self.exit_button_y - self.exit_button_height / 2

        arcade.draw_lbwh_rectangle_outline(
            button_left,
            button_bottom,
            self.exit_button_width,
            self.exit_button_height,
            arcade.color.WHITE,
            2  # толщина линии
        )

        arcade.draw_text(
            "Выйти на главный экран",
            self.exit_button_x,
            self.exit_button_y,
            arcade.color.BLACK,
            12,
            anchor_x="center",
            anchor_y="center",
        )

    def on_key_press(self, symbol, modifiers):
        if self.show_welcome:
            self.show_welcome = False
        elif symbol == arcade.key.ESCAPE:
            self.close()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_welcome:
            self.show_welcome = False
            return

        if (
            self.exit_button_x - self.exit_button_width / 2 < x < self.exit_button_x + self.exit_button_width / 2
            and self.exit_button_y - self.exit_button_height / 2 < y < self.exit_button_y + self.exit_button_height / 2
        ):
            self.show_welcome = True


def main():
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
