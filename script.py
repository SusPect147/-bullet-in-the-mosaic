import arcade

SCREEN_WIDTH = 610
SCREEN_HEIGHT = 610
WINDOW_TITLE = "Приветствие"

class WelcomeWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.welcome_text = "Добро пожаловать, User"
        self.show_welcome = True

    def on_draw(self):
        self.clear()

        if self.show_welcome:
            arcade.draw_text(
                self.welcome_text,
                self.width / 2,
                self.height / 2,
                arcade.color.WHITE,
                36,
                anchor_x="center",
                anchor_y="center",
            )

            arcade.draw_text(
                "Нажмите любую клавишу или клик мышью",
                self.width / 2,
                self.height / 2 - 60,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
                anchor_y="center",
            )
        else:
            arcade.draw_text(
                "Основной экран",
                self.width / 2,
                self.height / 2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center",
            )

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.close()
        else:
            self.show_welcome = False

    def on_mouse_press(self, x, y, button, modifiers):
        self.show_welcome = False


def main():
    window = WelcomeWindow()
    arcade.run()


if __name__ == "__main__":
    main()
