import pygame
import pieces
import bitboard

# A button class used for user selection of a promotion piece
class ImgButton:
    def __init__(self, surface: pygame.Surface, image: pygame.Surface, x: int, y: int):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = image
        self.is_clicked = False
        self.bg_colour = (150, 150, 150)
        self.buffer = 3
        self.curve_buffer = 7
        self.circles = (
            (self.x + self.curve_buffer + self.buffer, self.y + self.curve_buffer + self.buffer),
            (self.x + self.width - self.curve_buffer - self.buffer, self.y + self.curve_buffer + self.buffer),
            (self.x + self.curve_buffer + self.buffer, self.y + self.height - self.curve_buffer - self.buffer),
            (self.x + self.width - self.curve_buffer - self.buffer,
             self.y + self.height - self.curve_buffer - self.buffer)
        )

    # blits the image to the screen
    def display(self):

        pygame.draw.rect(self.surface, self.bg_colour,
                         (self.x + self.curve_buffer + self.buffer, self.y + self.buffer,
                          self.width - self.curve_buffer * 2 - self.buffer * 2, self.height - self.buffer * 2))
        pygame.draw.rect(self.surface, self.bg_colour,
                         (self.x + self.buffer, self.y + self.curve_buffer + self.buffer, self.width - self.buffer * 2,
                          self.height - self.curve_buffer * 2 - self.buffer * 2))
        for circle in self.circles:
            pygame.draw.circle(self.surface, self.bg_colour, circle, self.curve_buffer)

        self.surface.blit(self.image, (self.x, self.y))

        pygame.display.update()

    # checks if the user has clicked on the button, if so it updates the clicked variable
    def update(self):
        self.is_clicked = False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed(3)[0]:

            if self.x < mouse_x <= self.x + self.width and self.y < mouse_y <= self.y + self.height:
                self.is_clicked = True


# class used to display a board onto a screen
class BoardDisplay:

    def __init__(self, square_size, debug, board_pos_x, board_pos_y):
        pygame.font.init()
        self.fps_font = pygame.font.SysFont("Consolas", 24)
        self.square_font = pygame.font.SysFont("Consolas", 16)
        self.square_size = square_size
        # set up screen
        self.board_position_x = board_pos_x
        self.board_position_y = board_pos_y
        self.width = self.square_size * 8
        self.height = self.square_size * 8
        self.screen = pygame.display.set_mode((self.width, self.height))

        # constants
        self.bg_colour = (0, 0, 0)
        self.light_colour = (255, 255, 255)
        #self.light_colour = (240, 217, 181)

        # self.dark_colour = (101, 71, 0)
        self.dark_colour = (112, 62, 4)
        #self.dark_colour = (181,136,99)

        # whether to display dfebug numbers
        self.debug = debug

        # cached squares (colour, rect)
        self.squares = []
        # cached nums
        self.debug_nums = []

        # cache the squares
        for row in range(8):
            for col in range(8):
                colour = self.light_colour
                dcolour = self.dark_colour
                if (row % 2 + col) % 2 == 0:
                    colour = self.dark_colour
                    dcolour = self.light_colour
                self.squares.append((colour, pygame.Rect(self.board_position_x + col * self.square_size,
                                                         self.board_position_y + row * self.square_size,
                                                         self.square_size, self.square_size)))
                text = self.square_font.render(str(63 - (row * 8 + col)), True, dcolour)
                self.debug_nums.append((text, (self.board_position_x + col * self.square_size,
                                               self.board_position_y + row * self.square_size)))

        try:
            self.images = {
                # lights
                pieces.Piece(pieces.bishop, pieces.white): pygame.image.load("../piece_images/wB.png"),
                pieces.Piece(pieces.king, pieces.white): pygame.image.load("../piece_images/wK.png"),
                pieces.Piece(pieces.knight, pieces.white): pygame.image.load("../piece_images/wN.png"),
                pieces.Piece(pieces.pawn, pieces.white): pygame.image.load("../piece_images/wP.png"),
                pieces.Piece(pieces.queen, pieces.white): pygame.image.load("../piece_images/wQ.png"),
                pieces.Piece(pieces.rook, pieces.white): pygame.image.load("../piece_images/wR.png"),

                # darks
                pieces.Piece(pieces.bishop, pieces.black): pygame.image.load("../piece_images/bB.png"),
                pieces.Piece(pieces.king, pieces.black): pygame.image.load("../piece_images/bK.png"),
                pieces.Piece(pieces.knight, pieces.black): pygame.image.load("../piece_images/bN.png"),
                pieces.Piece(pieces.pawn, pieces.black): pygame.image.load("../piece_images/bP.png"),
                pieces.Piece(pieces.queen, pieces.black): pygame.image.load("../piece_images/bQ.png"),
                pieces.Piece(pieces.rook, pieces.black): pygame.image.load("../piece_images/bR.png"),
            }
        except FileNotFoundError:
            self.images = {
                # lights
                pieces.Piece(pieces.bishop, pieces.white): pygame.image.load("engine/piece_images/wB.png"),
                pieces.Piece(pieces.king, pieces.white): pygame.image.load("engine/piece_images/wK.png"),
                pieces.Piece(pieces.knight, pieces.white): pygame.image.load("engine/piece_images/wN.png"),
                pieces.Piece(pieces.pawn, pieces.white): pygame.image.load("engine/piece_images/wP.png"),
                pieces.Piece(pieces.queen, pieces.white): pygame.image.load("engine/piece_images/wQ.png"),
                pieces.Piece(pieces.rook, pieces.white): pygame.image.load("engine/piece_images/wR.png"),

                # darks
                pieces.Piece(pieces.bishop, pieces.black): pygame.image.load("engine/piece_images/bB.png"),
                pieces.Piece(pieces.king, pieces.black): pygame.image.load("engine/piece_images/bK.png"),
                pieces.Piece(pieces.knight, pieces.black): pygame.image.load("engine/piece_images/bN.png"),
                pieces.Piece(pieces.pawn, pieces.black): pygame.image.load("engine/piece_images/bP.png"),
                pieces.Piece(pieces.queen, pieces.black): pygame.image.load("engine/piece_images/bQ.png"),
                pieces.Piece(pieces.rook, pieces.black): pygame.image.load("engine/piece_images/bR.png"),
            }

        # make instance's scaled images
        self.images = self.scale_images(self.square_size)

        # colour square for showing the legal moves for a piece
        self.highlight_colour = (184, 21, 0)
        self.highglight_alpha = 210
        self.highlight_positions = 0  # map of what positions to highlight

        # surface to blit to the screen to show legal moves
        # we do it this way to make it transparent
        self.highlight_surface = pygame.Surface((self.square_size, self.square_size))
        self.highlight_surface.set_alpha(self.highglight_alpha)
        self.highlight_surface.fill(self.highlight_colour)

    # scales all images to the current size (declared in __init__)
    def scale_images(self, scale):
        new_images = {}
        for piece, image in self.images.items():
            if image.get_width != scale and image.get_height != scale:
                new_images[piece] = pygame.transform.scale(image, (scale, scale))
            else:
                new_images[piece] = image
        return new_images

    # draws a piece type to a row&col
    def draw_piece(self, piece: pieces.Piece, coord):
        x, y = map(lambda i: i - self.square_size // 2, coord)
        pygame.Surface.blit(self.screen, self.images[piece], (x, y))

    # blits one square to the screen
    def display_square(self, pos):
        square = self.squares[pos]
        pygame.draw.rect(self.screen, *square)
        if self.debug:
            text = self.debug_nums[pos]
            pygame.Surface.blit(self.screen, *text)

    # shows the squares of the board
    def display_squares(self):
        for i in range(64):
            self.display_square(i)

    # displays all possible moves for the current held piece
    def display_moves(self):
        if not self.highlight_positions:
            return
        position_map = 1
        for position in range(64):
            if position_map & self.highlight_positions:

                row, col = 7-position // 8, 7-position % 8
                self.screen.blit(self.highlight_surface, (col*self.square_size, row*self.square_size))
                # pygame.draw.rect(self.screen, self.highlight_colour,
                #                  (col * self.square_size, row * self.square_size, self.square_size, self.square_size))
            position_map <<= 1

    # blits the current piece being held
    def display_holding(self, holding, picked_position):
        if holding is not None and picked_position is not None:
            position = 0
            while 1 << position != picked_position:
                position += 1
            position = 63 - position
            self.display_square(position)

            self.draw_piece(holding, pygame.mouse.get_pos())

    def ask_user_for_promotion_piece(self, colour):
        piece_vals = [pieces.queen, pieces.rook, pieces.knight, pieces.bishop]
        size = self.square_size
        midpoint = self.square_size * 4
        positions = [(midpoint - size, midpoint - size), (midpoint, midpoint - size),
                     (midpoint - size, midpoint), (midpoint, midpoint)]
        buttons = [ImgButton(self.screen, self.images[pieces.Piece(piece_val, colour)], x, y)
                   for piece_val, (x, y) in zip(piece_vals, positions)]

        while True:
            pygame.event.get()
            for button, piece_val in zip(buttons, piece_vals):
                button.display()
                button.update()
                if button.is_clicked:
                    return piece_val

    # blits all current pieces to the board
    def display_pieces(self, board: bitboard.Board):
        # create a list of the type of peice at each position, top left = 0, bottom right = 63
        display_list = [None for _ in range(64)]
        for colour, piece_list in enumerate(board.positions):
            for piece_type, piece_map in enumerate(piece_list):
                position = 1
                for index in range(64):
                    if piece_map & position:
                        display_list[index] = pieces.Piece(piece_type, colour) # noqa
                    position <<= 1

        # reverse the list because the bitboard represents the 0th element at the bottom right
        display_list.reverse()
        # display each piece
        for position, piece in enumerate(display_list):
            if piece is None:
                continue
            row, col = position // 8, position % 8
            pygame.Surface.blit(self.screen, self.images[piece],
                                (self.board_position_x + col * self.square_size,
                                 self.board_position_y + row * self.square_size))

    # duh
    def display_fps(self, fps):

        img = self.fps_font.render(str(int(fps)), True, (20, 255, 30))
        self.screen.blit(img, (0, 0))

    # calls all display functions and updates pygame screen
    def update_screen(self, board, holding=None, fps=0.0, show_fps=False, picked_position=0):

        self.display_squares()
        self.display_moves()
        self.display_pieces(board)
        self.display_holding(holding, picked_position)

        if show_fps:
            self.display_fps(fps)
        pygame.display.update()
