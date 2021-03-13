# create a question getter
# store questions in list
# store answers in list of lists list[0] = ["question", "correct answers", "player answer"]
# the user may answer on a slider
# create "grading" function to give full points for correct, half points for in the right ballpark etc.
# allow user to customize their quiz with question count options and endless mode

import arcade
import config
import question_getter

# constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Politi-Fact or Fiction"
LIST_SIZE = 10


# game
class QuizGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.DARK_BLUE)

        self.qg = None
        self.question_list = []
        self.answered_list = []  # will be used as a url blacklist to store questions already asked, maybe later a dict to store answers or something for a right/wrong review

    def setup(self):
        self.qg = question_getter.QuestionGetter("https://www.politifact.com/factchecks/2021/mar/05/mike-pence/pence-falsely-says-if-hr-1-passes-millions-people-/", config.ANSWER_WHITELIST)
        self.answered_list = []
        self.question_list = self.qg.generate_url_list(size=LIST_SIZE, answer_whitelist=config.ANSWER_WHITELIST, order_randomized=True)

    def on_draw(self):
        arcade.start_render()


# make game here not in quiz game
class QuizView(arcade.View):
    def __init__(self):
        super().__init__()


class StartView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_BLUE)
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        arcade.start_render()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = QuizView()
        # game_view.setup()
        self.window.show_view(game_view)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    # start_view.setup()
    arcade.run()


if __name__ == "__main__":
    main()


'''
To generate the question lists

'''
