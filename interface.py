import engine
from button import Button

import pygame
from enum import Enum


class Screens(Enum):
    menu = 0
    game = 1
    game_over = 2


class Interface:
    def __init__(self):

        self.screen = pygame.display.set_mode((900, 720))
        self.game = engine.game.Game(self.screen, size=90)
        # a list of events that are handed to self.game.update
        self.events = []
        # list of Button objects that are refreshed every frame
        self.buttons = []
        # set to true whilst the window is being displayed
        self.running = False
        # The current part of the GUI that we are displaying
        self.current_screen = Screens.menu

        self.is_holding_mouse = False

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

        user_clicked = False
        if pygame.mouse.get_pressed(3)[0]:
            if not self.is_holding_mouse:
                self.is_holding_mouse = True
                user_clicked = True
        else:
            self.is_holding_mouse = False

        for button in self.buttons:
            button.update(user_clicked)

        if self.current_screen == Screens.game:
            self.game.update(self.events)

        pygame.display.update()

    def quit_program(self):
        self.running = False

    def undo_move(self):
        if self.game.board.logs:
            self.game.board.unmake_move()
            self.game.current_legal_moves = None


    def load_game_screen(self):
        self.current_screen = Screens.game
        self.buttons.clear()
        self.buttons = [
            # undo move button
            Button(self.screen, position=(725, 225), area=(170, 80), text="UNDO", func=self.undo_move),
            # quit button
            Button(self.screen, position=(725, 600), area=(170, 115), text="QUIT", func=self.quit_program),

            ]




if __name__ == '__main__':
    interface = Interface()
    interface.load_game_screen()
    interface.run()
