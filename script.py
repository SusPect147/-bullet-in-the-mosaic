import arcade

SCREEN_WIDTH = 610
SCREEN_HEIGHT = 610
WINDOW_TITLE = "Maze Prototype"

BACKGROUND_COLOR = arcade.color.BLACK
WALL_COLOR = arcade.color.GRAY


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.show_welcome = True

        # Список стен
        self.walls = arcade.SpriteList()
        self.create_maze_contour()

    def create_maze_contour(self):
        # Левая стена
        left_wall = arcade.SpriteSolidColor(10, 600, WALL_COLOR)
        left_wall.center_x = 5
        left_wall.center_y = SCREEN_HEIGHT / 2

        # Правая стена
        right_wall = arcade.SpriteSolidColor(10, 600, WALL_COLOR)
        right_wall.center_x = SCREEN_WIDTH - 5
        right_wall.center_y = SCREEN_HEIGHT / 2

        # Нижняя стена
        bottom_wall = arcade.SpriteSolidColor(600, 10, WALL_COLOR)
        bottom_wall.center_x = SCREEN_WIDTH / 2
        bottom_wall.center_y = 5

        # Верхняя стена
        top_wall = arcade.SpriteSolidColor(600, 10, WALL_COLOR)
        top_wall.center_x = SCREEN_WIDTH / 2
        top_wall.center_y = SCREEN_HEIGHT - 5

        self.walls.extend([
            left_wall,
            right_wall,
            bottom_wall,
            top_wall
        ])

    def on_draw(self):
        self.clear()

        if self.show_welcome:
            self.draw_welcome_screen()
        else:
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

    def on_key_press(self, symbol, modifiers):
        if self.show_welcome:
            self.show_welcome = False
        elif symbol == arcade.key.ESCAPE:
            self.close()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_welcome:
            self.show_welcome = False


def main():
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
