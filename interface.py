import engine
from button import Button

import pygame

from enum import Enum
import random


class Screens(Enum):
    menu = 0
    game = 1
    game_over = 2


class PlayerColourChoice(Enum):
    white = 0
    black = 1
    rand = 2


class Interface:
    def __init__(self):

        self.screen = pygame.display.set_mode((900, 720))
        self.game = engine.game.Game(self.screen, size=90, black_is_ai=True)
        self.bot = engine.search.Bot()
        # a list of events that are handed to self.game.update
        self.events = []
        # list of Button objects that are refreshed every frame
        self.buttons = []
        # set to true whilst the window is being displayed
        self.running = False
        # The current part of the GUI that we are displaying
        self.current_screen = Screens.menu

        self.is_holding_mouse = False

        self.bg_clr = (255, 255, 255)

        self.player_colour_choice = PlayerColourChoice.white

        self.bot_depth_display = Button(self.screen, position=(735, 340), area=(145, 70))
        self.bot_eval_display = Button(self.screen, position=(735, 490), area=(145, 70))

    def run(self):
        self.running = True
        while self.running:
            self.events = []
            for event in pygame.event.get():
                self.events.append(event)
                if event.type == pygame.QUIT:
                    self.quit_program()
            self.update()

    def update(self):
        self.screen.fill(self.bg_clr)

        # check whether user clicked this frame
        user_clicked = False
        if pygame.mouse.get_pressed(3)[0]:
            if not self.is_holding_mouse:
                self.is_holding_mouse = True
                user_clicked = True
        else:
            self.is_holding_mouse = False

        # update bot depth display
        self.bot_depth_display.update_text(f"{self.bot.depth}")

        # update bot eval display
        self.bot_eval_display.update_text(f"{self.bot.best_root_score / 100:.1f}")

        # display every button
        for button in self.buttons:
            button.update(user_clicked)

        # display game
        if self.current_screen == Screens.game:
            self.game.update(self.events)

        pygame.display.update()

    def quit_program(self):
        self.running = False

    def undo_move(self):
        if self.game.board.logs:
            self.game.board.unmake_move()
            self.game.current_legal_moves = None

    def set_player_white(self):
        self.player_colour_choice = PlayerColourChoice.white

    def is_player_white(self):
        return self.player_colour_choice == PlayerColourChoice.white

    def set_player_black(self):
        self.player_colour_choice = PlayerColourChoice.black

    def is_player_black(self):
        return self.player_colour_choice == PlayerColourChoice.black

    def set_player_random(self):
        self.player_colour_choice = PlayerColourChoice.rand

    def is_player_random(self):
        return self.player_colour_choice == PlayerColourChoice.rand

    def load_menu_screen(self):
        self.screen = pygame.display.set_mode((1000, 500))
        self.current_screen = Screens.menu
        self.buttons = [
            # play button
            Button(self.screen, position=(15, 15), area=(350, 200), text="PLAY", font_size=80,
                   func=self.load_game_screen),

            # colour choice container
            Button(self.screen, position=(400, 15), area=(580, 200)),
            # white colour choice button
            Button(self.screen, position=(420, 30), area=(170, 170), text="White", func=self.set_player_white,
                   pressed_check=self.is_player_white),
            # black colour choice button
            Button(self.screen, position=(605, 30), area=(170, 170), text="Black", func=self.set_player_black,
                   pressed_check=self.is_player_black),
            # random colour choice button
            Button(self.screen, position=(790, 30), area=(170, 170), text="Random", func=self.set_player_random,
                   pressed_check=self.is_player_random),

        ]

    def load_game_screen(self):
        self.screen = pygame.display.set_mode((900, 720))
        self.current_screen = Screens.game

        self.init_game()

        self.buttons = [
            # undo move button
            Button(self.screen, position=(725, 225), area=(170, 80), text="UNDO", func=self.undo_move),
            # quit button
            Button(self.screen, position=(725, 600), area=(170, 115), text="QUIT", func=self.quit_program),
            # bot status
            Button(self.screen, position=(725, 310), area=(170, 285), text="Bot Info"),
            # depth display
            self.bot_depth_display,
            Button(self.screen, position=(740, 345), area=(45, 15), text="Depth", font_size=16,
                   border_clr=(255, 255, 255)),

            self.bot_eval_display,
            Button(self.screen, position=(740, 495), area=(45, 15), text="Eval", font_size=16,
                   border_clr=(255, 255, 255)),



        ]
        self.update()

    def init_game(self):

        white_is_ai = True
        black_is_ai = True
        if self.player_colour_choice == PlayerColourChoice.white:
            # set player to white
            white_is_ai = False
        elif self.player_colour_choice == PlayerColourChoice.black:
            # set player to black
            black_is_ai = False
        elif self.player_colour_choice == PlayerColourChoice.rand:
            # randomly set player to white or black
            if random.random() < 0.5:
                white_is_ai = False
            else:
                black_is_ai = False

        self.game = engine.game.Game(self.screen, size=90, white_is_ai=white_is_ai, black_is_ai=black_is_ai)
        self.game.set_ai(self.bot.search, engine.pieces.white)
        self.game.set_ai(self.bot.search, engine.pieces.black)


if __name__ == '__main__':
    interface = Interface()
    interface.load_menu_screen()
    interface.run()
