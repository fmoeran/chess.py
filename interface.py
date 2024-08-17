import engine
from button import Button
from move_display import MoveDisplay

import pygame

from enum import Enum
import random
import time


class Screens(Enum):
    menu = 0
    game = 1
    game_over = 2


class PlayerColourChoice(Enum):
    white = 0
    black = 1
    rand = 2


class Difficulty(Enum):
    easy = 1
    medium = 2
    hard = 3


class Enemy(Enum):
    player = 0
    bot = 1


class Interface:
    def __init__(self):

        self.screen = pygame.display.set_mode((900, 720))
        self.game = engine.game.Game(self.screen, size=90, black_is_ai=True)
        self.bot = engine.search.Bot()
        self.difficulty = Difficulty.hard
        self.enemy = Enemy.bot
        # whether we want to display the bot's info in the game screen
        # if this is true AND enemy is a bot then the info will be displayed
        self.display_info = True
        # a list of events that are handed to self.game.update
        self.events = []
        # list of Button objects that are refreshed every frame
        self.buttons = []
        # set to true whilst the window is being displayed
        self.running = False
        # The current part of the GUI that we are displaying
        self.current_screen = Screens.menu

        self.game_state = engine.game.GameState.unfinished

        self.is_holding_mouse = False

        self.bg_clr = (255, 255, 255)

        self.player_colour_choice = PlayerColourChoice.white

        self.bot_depth_display = Button(self.screen, position=(735, 340), area=(145, 70))
        self.bot_eval_display = Button(self.screen, position=(735, 490), area=(145, 70), text="N/A")

        self.move_display = MoveDisplay(self.screen)

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

        # bot info displays
        if self.displaying_bot_info():
            # update bot depth display
            self.bot_depth_display.update_text(f"{self.bot.depth}")

            # update bot eval display
            self.bot_eval_display.update_text(f"{self.bot.best_root_score / 100:.1f}")
        else:
            self.bot_depth_display.update_text("N/A")
            self.bot_eval_display.update_text("N/A")

        # display every button
        for button in self.buttons:
            button.update(user_clicked)

        # display game
        if self.current_screen == Screens.game:
            # update move_display
            if len(self.move_display.move_texts) != len(self.game.board.past_moves):
                self.move_display.add_move(self.game.board.past_moves[-1].notate())

            self.move_display.update()
            self.game_state = self.game.update(self.events)

            # if the game has finished
            if self.game_state != engine.game.GameState.unfinished:
                pygame.display.update()
                time.sleep(0.3)
                self.load_game_over_screen()

        pygame.display.update()

    def quit_program(self):
        self.running = False

    def undo_move(self):
        if self.game.board.logs:
            self.game.board.unmake_move()
            self.game.current_legal_moves = None
            self.move_display.pop_move()

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

    def set_difficulty_easy(self):
        self.difficulty = Difficulty.easy
        self.bot.use_tt = False
        self.bot.use_quiescence = False
        self.bot.eval_function = engine.evaluate.evaluate

    def is_difficulty_easy(self):
        return self.difficulty == Difficulty.easy

    def set_difficulty_medium(self):
        self.difficulty = Difficulty.medium
        self.bot.use_tt = False
        self.bot.use_quiescence = True
        self.bot.eval_function = engine.evaluate.evaluate

    def is_difficulty_medium(self):
        return self.difficulty == Difficulty.medium

    def set_difficulty_hard(self):
        self.difficulty = Difficulty.hard
        self.bot.use_tt = True
        self.bot.use_quiescence = True
        self.bot.eval_function = engine.tapered_eval.evaluate

    def is_difficulty_hard(self):
        return self.difficulty == Difficulty.hard

    def set_enemy_bot(self):
        self.enemy = Enemy.bot

    def is_enemy_bot(self):
        return self.enemy == Enemy.bot

    def set_enemy_human(self):
        self.enemy = Enemy.player

    def is_enemy_human(self):
        return self.enemy == Enemy.player

    def toggle_display_info(self):
        # we should not be able to toggle the button when the enemy is a player
        if self.enemy == Enemy.bot:
            self.display_info = not self.display_info

    def displaying_bot_info(self):
        return self.display_info and self.enemy == Enemy.bot

    def load_menu_screen(self):
        self.screen = pygame.display.set_mode((1000, 465))
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
            # bot difficulty container
            Button(self.screen, position=(15, 250), area=(320, 200), text="Difficulty", font_size=48,
                   text_offset=(0, -50)),
            # bot difficulty 1 button
            Button(self.screen, position=(30, 350), area=(90, 90), text="1", func=self.set_difficulty_easy,
                   pressed_check=self.is_difficulty_easy),
            # bot difficulty 2 button
            Button(self.screen, position=(130, 350), area=(90, 90), text="2", func=self.set_difficulty_medium,
                   pressed_check=self.is_difficulty_medium),
            # bot difficulty 3 button
            Button(self.screen, position=(230, 350), area=(90, 90), text="3", func=self.set_difficulty_hard,
                   pressed_check=self.is_difficulty_hard),
            # versus button container
            Button(self.screen, position=(350, 250), area=(400, 200), text="Versus", font_size=48, text_offset=(0, -50)),
            # versus player button
            Button(self.screen, position=(390, 330), area=(150, 110), text="Player", func=self.set_enemy_human, pressed_check=self.is_enemy_human),
            # versus bot button
            Button(self.screen, position=(560, 330), area=(150, 110), text="Bot", func=self.set_enemy_bot, pressed_check=self.is_enemy_bot),
            # display bot info
            Button(self.screen, position=(780, 250), area=(200, 200), text="Bot Info", func=self.toggle_display_info, pressed_check=self.displaying_bot_info),


        ]

    def load_game_screen(self):
        self.screen = pygame.display.set_mode((900, 720))
        self.current_screen = Screens.game

        self.move_display = MoveDisplay(self.screen, position=(725, 5), area=(170, 215))

        self.init_game()

        self.buttons = [
            # undo move button
            Button(self.screen, position=(725, 225), area=(170, 80), text="UNDO", func=self.undo_move),
            # quit button
            Button(self.screen, position=(725, 600), area=(170, 115), text="MENU", func=self.load_menu_screen),
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

    def load_game_over_screen(self):
        self.screen = pygame.display.set_mode((900,700))
        self.current_screen = Screens.game_over

        message = ""
        if self.game_state == engine.game.GameState.white_win:
            message = "White Wins"
        elif self.game_state == engine.game.GameState.black_win:
            message = "Black Wins"
        elif self.game_state == engine.game.GameState.draw:
            message = "Draw"
        self.buttons = [
            # game over message
            Button(self.screen, position=(0,0), area=(900, 200), text="GAME OVER", font_size=100, border_clr=self.bg_clr),
            # game state message
            Button(self.screen, position=(0,200), area=(900, 50), text=message, font_size=86, border_clr=self.bg_clr),
            # rematch button
            Button(self.screen, position=(25, 300), area=(850, 110), text="REMATCH", font_size=50, func=self.load_game_screen),
            # menu button
            Button(self.screen, position=(25, 420), area=(850, 110), text="MENU", font_size=50, func=self.load_menu_screen),
            # exit button
            Button(self.screen, position=(25, 540), area=(850, 110), text="EXIT", font_size=50, func=self.quit_program)

        ]

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

        if self.enemy == Enemy.player:
            white_is_ai = False
            black_is_ai = False

        self.game = engine.game.Game(self.screen, size=90, white_is_ai=white_is_ai, black_is_ai=black_is_ai)
        self.game.set_ai(self.bot.search, engine.pieces.white)
        self.game.set_ai(self.bot.search, engine.pieces.black)




