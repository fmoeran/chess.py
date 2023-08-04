import pygame


class MoveDisplay:
    def __init__(self, screen, position=(0, 0), area=(170, 250), font="arial", font_size=16,
                 bg_clr=(255,255,255), border_clr=(0,0,0), font_clr="Black"):
        self.screen = screen
        self.x, self.y = position
        self.width, self.height = area
        try:
            self.font = pygame.font.SysFont(font, font_size)
        except pygame.error:
            pygame.font.init()
            self.font = pygame.font.SysFont(font, font_size)
        self.font_clr = font_clr
        self.bg_clr = bg_clr
        self.border_clr = border_clr

        # list of move notations
        # each item only holds one move string
        self.move_texts = []

    def load_text_surface(self, text):
        return self.font.render(text, True, self.font_clr)

    def add_move(self, move_text):
        self.move_texts.append(move_text)

    def pop_move(self):
        self.move_texts.pop()

    def update(self):
        # draw background
        pygame.draw.rect(self.screen, self.bg_clr, (self.x, self.y, self.width, self.height))
        # draw border
        pygame.draw.rect(self.screen, self.border_clr, (self.x, self.y, self.width, self.height), 3)
        # draw text surfaces
        text_x = self.x + self.width/4
        starting_ind = max(0, len(self.move_texts) - 20 - len(self.move_texts) % 2)
        for row, ind in enumerate(range(starting_ind, len(self.move_texts), 2), 1):
            string = str(ind//2 + 1) + ". " + self.move_texts[ind]
            if len(self.move_texts) > ind+1:
                string += " " + self.move_texts[ind+1]
            text_surface = self.load_text_surface(string)
            text_y = row * self.height/12
            self.screen.blit(text_surface, (text_x, text_y, text_surface.get_width(), text_surface.get_height()))

