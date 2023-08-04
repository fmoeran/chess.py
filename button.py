import pygame


def void_function():
    pass

def bool_function():
    return False


class Button:
    def __init__(self, screen, text="", position=(0, 0), area=(200, 120),
                 font="arial", font_size=32, font_clr="Black", bg_off_clr=(255,255,255),
                 bg_on_clr=(200,200,200), border_clr=(0,0,0), func=void_function, pressed_check=bool_function):
        """
        A button for the user to interact with
        Parameters:
            screen (pygame.Surface): pygame surface that the button will blit onto
            text (str): text the will be displayed onto the button
            position (Tuple[int, int]): coordinates of the top left corner of the button
            area (Tuple[int, int]): the width and height of the button
            font (str): the name of a pygame available font
            font_size (int): the size of font
            font_clr (str): pygame colour for displaying the text
            bg_off_clr (Tuple[int, int, int]) the colour of the button when it is not on
            bg_on_clr (Tuple[int, int, int]) the colour of the button when it is on
            border_clr (Tuple[int, int, int]) the colour of the button's outline
            func (function): a function that the button will do when pressed
            pressed_check (function): a function that will return True when the button should be on
        """

        self.screen = screen

        self.x, self.y = position
        self.width, self.height = area

        try:
            self.font = pygame.font.SysFont(font, font_size)
        except pygame.error:
            pygame.font.init()
            self.font = pygame.font.SysFont(font, font_size)
        self.font_clr = font_clr
        self.bg_off_clr = bg_off_clr
        self.bg_on_clr = bg_on_clr
        self.border_clr = border_clr
        self.func = func
        self.pressed_check = pressed_check
        self.text = None
        self.text_width = None
        self.text_height = None
        self.text_x = None
        self.text_y = None
        self.text_surface = None
        self.update_text(text)

    def display(self):
        bg_clr = self.bg_on_clr if self.pressed_check() else self.bg_off_clr
        pygame.draw.rect(self.screen, bg_clr, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, self.border_clr, (self.x, self.y, self.width, self.height), 3)
        self.screen.blit(self.text_surface, (self.text_x, self.text_y, self.text_width, self.text_height))


    def is_hovering(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # AABB collision
        if self.x < mouse_x <= self.x + self.width and self.y < mouse_y <= self.y + self.height:
            return True

    def update(self, user_clicked):
        self.display()
        if user_clicked and self.is_hovering():
            self.func()

    def update_text(self, text):
        self.text = text
        self.text_width, self.text_height = self.font.size(text)
        self.text_x, self.text_y = self.x + self.width / 2 - self.text_width / 2, self.y + self.height / 2 - self.text_height / 2
        self.text_surface = self.font.render(self.text, True, self.font_clr)







