# store questions in list
# store answers in list of lists list[0] = ["question", "correct answers", "player answer"]
# the user may answer on a slider
# create "grading" function to give full points for correct, half points for in the right ballpark etc.
# allow user to customize their quiz with question count options and endless mode
# get buttons
# follow tutorial for pypackage or whatever on the arcade website

import arcade
import config
import question_getter
import webbrowser

# constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Politi-Fact or Fiction"
LIST_SIZE = 10


# sprite classes
class Button(arcade.Sprite):
    def __init__(self, x_pos, y_pos, width, height, color, text, name):
        super().__init__(scale=1, hit_box_algorithm="None")
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.position = x_pos, y_pos
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.name = name

    def on_draw(self):
        arcade.draw_rectangle_filled(self.x_pos, self.y_pos, self.width, self.height, self.color, 0)
        arcade.draw_text(self.text, self.x_pos, self.y_pos, arcade.csscolor.BLACK, 14, width=self.width, align="center", anchor_x="center", anchor_y="center")

    def get_name(self):
        return self.name


# game/view classes
class QuizView(arcade.View):
    def __init__(self, total_questions):
        super().__init__()

        self.question_getter = None
        self.question_list = []
        self.current_question_url = None
        self.current_question = None
        self.answered_list = []
        self.asked_list = []
        self.total_questions = total_questions
        self.sprite_list = arcade.SpriteList()
        self.lives = 3
        self.showing_correct = False

    def setup(self):
        self.question_getter = question_getter.QuestionGetter("https://www.politifact.com/factchecks/2021/mar/05/mike-pence/pence-falsely-says-if-hr-1-passes-millions-people-/", config.ANSWER_WHITELIST)
        self.question_list = self.question_getter.generate_url_list(size=self.total_questions, answer_whitelist=config.ANSWER_WHITELIST, order_randomized=True)
        self.answered_list = []
        self.asked_list = []
        self.current_question_url = None
        self.current_question = None
        self.lives = 3
        self.showing_correct = False

        screen_increments = int(SCREEN_WIDTH/6)
        self.sprite_list.append(Button(screen_increments*1, 100, 100, 50, arcade.color.RED, "Pants-on-fire", "pants-fire"))
        self.sprite_list.append(Button(screen_increments*2, 100, 100, 50, arcade.color.CATAWBA, "False", "false"))
        self.sprite_list.append(Button(screen_increments*3, 100, 100, 50, arcade.color.CELESTE, "Barely True", "barely-true"))
        self.sprite_list.append(Button(screen_increments*4, 100, 100, 50, arcade.color.CERULEAN, "Half True", "half-true"))
        self.sprite_list.append(Button(screen_increments*5, 100, 100, 50, arcade.color.CERULEAN_BLUE, "True", "true"))
        self.sprite_list.append(Button(50, SCREEN_HEIGHT-50, 50, 50, arcade.color.WHITE, "End", "end"))
        self.get_question()

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_BLUE)
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        arcade.start_render()
        # arcade.draw_text("Lives: " + str(self.lives), 50, SCREEN_HEIGHT-100, arcade.color.WHITE, 15, width=200, align="center", anchor_x="center", anchor_y="center")
        arcade.draw_text("HOW TRUE IS IT?", SCREEN_WIDTH/2, SCREEN_HEIGHT-50, arcade.color.WHITE, 50, width=SCREEN_WIDTH, align="center", anchor_x="center", anchor_y="center")
        quote = ""
        index = 0
        for char in self.current_question.get_quote():
            quote += str(char)
            index += 1
            if index >= 50:
                if char == " ":
                    index = 0
                    quote += "\n"
        arcade.draw_text(f"{self.current_question.get_person()} {self.current_question.get_quote_context()} \n\"{quote}\"", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 20, width=SCREEN_WIDTH, align="center", anchor_x="center", anchor_y="center")

        if self.showing_correct:
            arcade.draw_text(f"Correct Answer (Click to Continue): {self.current_question.get_truth()}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2-100, arcade.color.WHITE, 25, width=SCREEN_WIDTH, align="center", anchor_x="center", anchor_y="center")

        for button in self.sprite_list:
            button.on_draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        answer_buttons = ["pants-fire", "false", "barely-true", "half-true", "true"]
        try:
            button = [button.get_name() for button in arcade.get_sprites_at_point((_x, _y), self.sprite_list)][0]
        except IndexError:
            button = []

        # buttons = arcade.get_sprites_at_point((_x, _y), self.sprite_list)
        if button in answer_buttons and not self.showing_correct:
            self.showing_correct = True
            self.answered_list.append([self.current_question_url, self.current_question.get_truth(), button])
            print(self.answered_list[-1])
        elif self.showing_correct:
            self.showing_correct = False
            if len(self.answered_list) < self.total_questions:
                self.get_question()
            else:
                end_view = EndView(self.answered_list)
                end_view.setup()
                self.window.show_view(end_view)
        elif button == "end":
            end_view = EndView(self.answered_list)
            end_view.setup()
            self.window.show_view(end_view)

    def get_question(self):
        if len(self.question_list) <= 0:
            self.question_list = self.question_getter.generate_url_list(size=LIST_SIZE, answer_whitelist=config.ANSWER_WHITELIST, link_blacklist=self.asked_list, order_randomized=True)

        self.current_question_url = self.question_list.pop(0)
        print(f"New Question ({len(self.question_list)}) {self.current_question_url}")
        # print("Already Asked", self.asked_list)
        self.asked_list.append(self.current_question_url)
        self.current_question = question_getter.QuestionGetter(self.current_question_url, None)

        print(f"Current Question:\n\t{self.current_question.get_person()} says {self.current_question.get_quote()} and its {self.current_question.get_truth()}")


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.sprite_list = arcade.SpriteList()
        self.title_size = 75
        self.title_strobe = 0.1
        self.questions = 10

    def setup(self):
        self.title_size = 75
        self.title_strobe = 0.1
        self.questions = 10

        self.sprite_list.append(Button(300, 200, 100, 100, arcade.csscolor.BROWN, "Start Game", "start"))
        self.sprite_list.append(Button(500, 250, 150, 50, arcade.csscolor.BROWN, "More Questions", "more"))
        self.sprite_list.append(Button(500, 150, 150, 50, arcade.csscolor.BROWN, "Less Questions", "less"))
        self.sprite_list.append(Button(700, 200, 150, 100, arcade.csscolor.BROWN, "Instructions", "instruct"))

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_BLUE)
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        self.title_size += self.title_strobe
        if self.title_size >= 80 or self.title_size <= 70:
            self.title_strobe *= -1

        arcade.start_render()

        arcade.draw_text("Politi-Fact or Fiction", SCREEN_WIDTH/2, SCREEN_HEIGHT-100, arcade.csscolor.WHITE, self.title_size, width=SCREEN_WIDTH, align="center", anchor_x="center", anchor_y="center")
        if self.questions != 0:
            arcade.draw_text("Questions: " + str(self.questions), 500, 300, arcade.csscolor.WHITE, 20, width=200, align="center", anchor_x="center", anchor_y="center")
        else:
            arcade.draw_text("Questions: endless", 500, 300, arcade.csscolor.WHITE, 20+(75-self.title_size), width=500, align="center", anchor_x="center", anchor_y="center")

        for sprite in self.sprite_list:
            sprite.on_draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # get buttons clicked on
        buttons = [button.get_name() for button in arcade.get_sprites_at_point((_x, _y), self.sprite_list)]
        # buttons = arcade.get_sprites_at_point((_x, _y), self.sprite_list)
        print(buttons)

        if "start" in buttons:
            game_view = QuizView(self.questions)
            game_view.setup()
            self.window.show_view(game_view)

        if "more" in buttons:
            self.questions += 1
        elif "less" in buttons:
            self.questions -= 1
            if self.questions <= 1:
                self.questions = 1

        if "instruct" in buttons:
            instruct_view = InstructionView()
            instruct_view.setup()
            self.window.show_view(instruct_view)


class EndView(arcade.View):
    def __init__(self, answered_list):
        super().__init__()
        self.sprite_list = None
        self.answered_list = answered_list
        self.wrong_list = []
        self.correct = 0
        self.review_mode = False
        self.wrong_index = 0

    def setup(self):
        self.correct = 0
        self.sprite_list = arcade.SpriteList()
        false_answers = ["pants-fire", "false"]
        true_answers = ["barely-true", "half-true", "true"]
        for question in self.answered_list:
            if question[1] == question[2]:
                self.correct += 1
            elif question[1] in false_answers and question[2] in false_answers:
                print("Partial Correct", question)
                self.correct += 0.5
            elif question[1] in true_answers and question[2] in true_answers:
                print("Partial Correct", question)
                self.correct += 0.5
            else:
                self.wrong_list.append(question)
        self.score = (self.correct/len(self.answered_list))*100

        if not self.review_mode:
            self.sprite_list.append(Button(SCREEN_WIDTH/3, 100, 100, 100, arcade.color.BROWN, "Play Again", "again"))
            if len(self.wrong_list) <= 0:
                self.sprite_list.append(Button(SCREEN_WIDTH*2/3, 100, 100, 100, arcade.color.BROWN, "Perfect Score", "view"))
            else:
                self.sprite_list.append(Button(SCREEN_WIDTH*2/3, 100, 300, 100, arcade.color.BROWN, "View Incorrect Answers", "view"))
        else:
            self.sprite_list.append(Button(SCREEN_WIDTH/5, 100, 100, 100, arcade.color.BROWN, "Previous", "prev"))
            self.sprite_list.append(Button(SCREEN_WIDTH*2/5, 100, 100, 100, arcade.color.BROWN, "Next", "next"))
            self.sprite_list.append(Button(SCREEN_WIDTH*3/5, 100, 100, 100, arcade.color.BROWN, "Open", "open"))
            self.sprite_list.append(Button(SCREEN_WIDTH*4/5, 100, 100, 100, arcade.color.BROWN, "Exit", "exit"))

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_BLUE)
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        arcade.start_render()
        if not self.review_mode:
            arcade.draw_text(f"Score {self.score}%", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.csscolor.WHITE, 50, width=SCREEN_WIDTH, align="center", anchor_x="center", anchor_y="center")
        else:
            arcade.draw_text(f"Score {self.score}%", SCREEN_WIDTH/2, SCREEN_HEIGHT-50, arcade.csscolor.WHITE, 20, width=SCREEN_WIDTH, align="center", anchor_x="center", anchor_y="center")
            quote = ""
            index = 0
            current_question = question_getter.QuestionGetter(self.wrong_list[self.wrong_index][0], None)
            for char in current_question.get_quote():
                quote += str(char)
                index += 1
                if index >= 50:
                    if char == " ":
                        index = 0
                        quote += "\n"
            arcade.draw_text(f"{current_question.get_person()} {current_question.get_quote_context()} \n\"{quote}\"\nYou Answered {self.wrong_list[self.wrong_index][2]} the correct answer is {self.wrong_list[self.wrong_index][1]}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 20, width=SCREEN_WIDTH, align="center", anchor_x="center", anchor_y="center")

        for button in self.sprite_list:
            button.on_draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # get buttons clicked on
        buttons = [button.get_name() for button in arcade.get_sprites_at_point((_x, _y), self.sprite_list)]
        # buttons = arcade.get_sprites_at_point((_x, _y), self.sprite_list)
        print(buttons)

        if "again" in buttons:
            start_view = StartView()
            start_view.setup()
            self.window.show_view(start_view)

        if "view" in buttons and len(self.wrong_list) >= 1:
            self.review_mode = True
            self.setup()

        if "next" in buttons:
            self.wrong_index += 1
        elif "prev" in buttons:
            self.wrong_index -= 1

        if "next" in buttons or "prev" in buttons:
            if self.wrong_index >= len(self.wrong_list):
                self.wrong_index = 0
            elif self.wrong_index <= 0:
                self.wrong_index = len(self.wrong_list) - 1

        if "open" in buttons:
            webbrowser.open(self.wrong_list[self.wrong_index][0], new=2, autoraise=True)

        if "exit" in buttons:
            self.review_mode = False
            self.setup()


class InstructionView(arcade.View):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.append(Button(SCREEN_WIDTH/2, 50, 100, 100, arcade.color.WHITE, "Back", "back"))

    def on_show(self):
        arcade.set_background_color(arcade.csscolor.DARK_BLUE)
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        arcade.start_render()
        instruction_text = "Welcome to Politi-Fact or Fiction\nIn this game you will be presented a question and be asked to determine \nnot just if it is true but how true it is.\n"\
                           "You will earn 1 point for a completely correct answer \nand a half point for answering in the right direction\n"\
                           "At the end of the game you will be able to view the questions you got wrong \nand read up on the facts behind them\n"\
                           "This is meant to illustrate that determining the truth of the matter from small snippets is difficult"
        arcade.draw_text(instruction_text, SCREEN_WIDTH/2, SCREEN_HEIGHT/2+100, arcade.color.BLACK, 20, width=SCREEN_WIDTH, align="center", anchor_x="center", anchor_y="center")
        for button in self.sprite_list:
            button.on_draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # get buttons clicked on
        buttons = [button.get_name() for button in arcade.get_sprites_at_point((_x, _y), self.sprite_list)]
        # buttons = arcade.get_sprites_at_point((_x, _y), self.sprite_list)
        print(buttons)
        if "back" in buttons:
            start_view = StartView()
            start_view.setup()
            self.window.show_view(start_view)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    start_view.setup()
    arcade.run()


if __name__ == "__main__":
    main()


'''
To generate the question lists

'''
