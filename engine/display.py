import pygame
from engine import pieces
from engine import bitboard


# A button class used for user selection of a promotion piece
class ImgButton:
    def __init__(self, surface: pygame.Surface, image: pygame.Surface, x: int, y: int, size: int,
                 colour):
        self.surface = surface
        self.coords = (x, y)
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.image = image
        self.is_clicked = False
        self.bg_colour = colour
        self.img_position = (x + size / 2 - image.get_width() / 2, y + size / 2 - image.get_height() / 2)

        self.rect_surface = pygame.Surface((self.width, self.height))
        self.rect_surface.fill(self.bg_colour)

    def display(self):
        """
        displays the button the self.surface
        """
        self.surface.blit(self.rect_surface, self.coords)
        self.surface.blit(self.image, self.img_position)

    def update(self):
        """
        checks if the user has clicked on the button, if so it updates the clicked variable
        """
        self.is_clicked = False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed(3)[0]:

            if self.x < mouse_x <= self.x + self.width and self.y < mouse_y <= self.y + self.height:
                self.is_clicked = True


# class used to display a board onto a screen
class BoardDisplay:

    def __init__(self, screen: pygame.Surface, square_size: int, debug: bool, board_pos_x: int, board_pos_y: int):
        pygame.font.init()
        self.square_font = pygame.font.SysFont("Consolas", 16)
        self.square_size = square_size
        # set up screen
        self.board_position_x = board_pos_x
        self.board_position_y = board_pos_y
        self.width = self.square_size * 8
        self.height = self.square_size * 8
        if screen is None:
            self.screen = pygame.display.set_mode((self.width, self.height))
        else:
            self.screen = screen

        # constants
        self.bg_colour = (0, 0, 0)
        self.light_colour = (255, 255, 255)
        # self.light_colour = (240, 217, 181)

        # self.dark_colour = (101, 71, 0)
        self.dark_colour = (112, 62, 4)
        # self.dark_colour = (181,136,99)

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
                if (row + col) % 2 == 1:
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

        # surface to blit to the screen to show legal moves
        # we do it this way to make it transparent
        self.highlight_surface = pygame.Surface((self.square_size, self.square_size))
        self.highlight_surface.set_alpha(self.highglight_alpha)
        self.highlight_surface.fill(self.highlight_colour)


        # promotion GUI
        self.buttons = []
        self.piece_vals = [pieces.queen, pieces.rook, pieces.knight, pieces.bishop]

    # scales all images to the current size (declared in __init__)
    def scale_images(self, scale):
        new_images = {}
        for piece, image in self.images.items():
            if image.get_width != scale and image.get_height != scale:
                new_images[piece] = pygame.transform.scale(image, (scale, scale))
            else:
                new_images[piece] = image
        return new_images

    # draws a piece type
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
    def display_moves(self, highlight_positions):
        for position in highlight_positions:
            row, col = 7 - position // 8, 7 - position % 8
            self.screen.blit(self.highlight_surface,
                             (col * self.square_size + self.board_position_x,
                              row * self.square_size + self.board_position_y))

    # blits the current piece being held
    def display_holding(self, holding, picked_position):
        if holding is not None and picked_position is not None:
            position = bitboard.get_single_position(picked_position)
            position = 63 - position
            self.display_square(position)

            self.draw_piece(holding, pygame.mouse.get_pos())

    def get_mouse_position(self, pos):
        x, y = pos
        row = (y - self.board_position_y) // self.square_size
        col = (x - self.board_position_x) // self.square_size
        board_position = row * 8 + col
        return bitboard.bitset[63 - board_position]

    def start_ask_user_for_promotion_piece(self, colour):
        """
        initialises the promotion butons when the game wants to ask the user for a promotion pieces
        """

        size = self.square_size * 2
        midpoint = self.square_size * 4
        positions = [(midpoint - size, midpoint - size), (midpoint, midpoint - size),
                     (midpoint - size, midpoint), (midpoint, midpoint)]
        colours = [self.dark_colour, self.light_colour, self.light_colour, self.dark_colour]
        self.buttons = [ImgButton(self.screen, self.images[pieces.Piece(piece_val, colour)], x, y, size, bg_clr)
                        for piece_val, (x, y), bg_clr in zip(self.piece_vals, positions, colours)]

    def get_promotion_answer(self):
        pygame.event.get()
        for button, piece_val in zip(self.buttons, self.piece_vals):
            button.display()
            button.update()
            if button.is_clicked:
                self.buttons = []
                return piece_val

    # blits all current pieces to the board
    def display_pieces(self, board: bitboard.Board):
        # create a list of the type of peice at each position
        # None represents no piece
        display_list = [None for _ in range(64)]
        for colour, piece_list in enumerate(board.positions):
            for piece_type, piece_map in enumerate(piece_list):
                for index in bitboard.iter_bitmap(piece_map):
                    display_list[63 - index] = pieces.Piece(piece_type, colour)  # noqa

        # display each piece
        for position, piece in enumerate(display_list):
            if piece is None:
                continue
            row, col = position // 8, position % 8
            pygame.Surface.blit(self.screen, self.images[piece],
                                (self.board_position_x + col * self.square_size,
                                 self.board_position_y + row * self.square_size))

    # calls all display functions and updates pygame screen
    def update_screen(self, board, holding=None, picked_position=0, highlight_positions=[]):

        self.display_squares()
        self.display_moves(highlight_positions)
        self.display_pieces(board)
        self.display_holding(holding, picked_position)


