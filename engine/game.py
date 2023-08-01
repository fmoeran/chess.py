import pygame
import random
import time

from engine import move
from engine import display
from engine import bitboard
from engine import move_generator
from engine import pieces

pygame.init()

starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w QKqk - 0 1"


# class with the game loop that activates each move and contains a board display and board
class Game:

    def __init__(self, screen: pygame.Surface = None, size=90,
                 white_is_ai=False, black_is_ai=False, debug=False, coords: tuple[int, int] = None):

        self.debug = debug

        if coords is None:
            coords = (0, 0)
        self.board_position_x, self.board_position_y = coords
        # the display to show the board
        self.display: display.BoardDisplay = display.BoardDisplay(screen, size, debug=self.debug,
                                                                  board_pos_x=self.board_position_x,
                                                                  board_pos_y=self.board_position_y,)

        self.square_size = size

        # which players (if either) are AI
        self.white_is_ai = white_is_ai
        self.black_is_ai = black_is_ai

        # to check if the process (multiprocessing.process) is still running
        self.ai_running = False

        self.board: bitboard.Board = bitboard.Board.from_fen(starting_fen)

        self.generator = move_generator.Generator(self.board)

        # True on the frame that they occur
        self.mouse_pressed = False

        # the current piece that the player is holding
        self.holding = None
        # where the player picked up their holding from ( if they are holding)
        self.picked_up_position = None

        # holds all the current legal moves for the player whose move it is
        self.current_legal_moves = None
        # positions to pass to self.display to highlight when holding a piece
        self.highlight_positions = []

    # updates self.current_moves to a set with every legal move the current team can make
    def update_current_moves(self):  # runs the first frame a player's move function is called
        self.current_legal_moves = self.generator.get_legal_moves()

    # returns a legal Move class (THIS IS WHERE PROMOTION IS DONE ON THE PLAYERS SIDE)
    # NOTE this requires current_legal_moves to be updated
    def generate_move(self, start, end):
        new_move = move.Move(start, end)

        # checks if the normal move is legal
        moves = self.current_legal_moves
        if new_move in moves:
            return new_move

        if start & self.board.positions[self.board.colour][pieces.king]:
            # checks if the move is a castle
            new_move = move.Move(start, end, flag=move.Flags.castle)
            if new_move in moves:
                return new_move
        elif start & self.board.positions[self.board.colour][pieces.pawn]:
            # checks for en passent
            new_move = move.Move(start, end, flag=move.Flags.en_passent)
            if new_move in moves:
                return new_move
            # checks if any promotion is legal
            queen = pieces.queen
            new_move = move.Move(start, end, flag=move.Flags.promotion, promotion_piece=queen)
            if new_move in moves:
                promotion_piece = self.display.ask_user_for_promotion_piece(self.board.colour)
                return move.Move(start, end, flag=move.Flags.promotion, promotion_piece=promotion_piece)

        # will return None if there aere no legal moves with those positions

    # attempts to move a piece via calling outside function (mke_move). If it is illegal, raise an exception
    def move_piece(self, move):
        if move not in self.current_legal_moves:
            raise Exception(f"{move.start}-{move.end} is not in legal moves")
        self.board.make_move(move)
        self.current_legal_moves = None  # resets legal moves

    def update_move_highlights(self):
        self.highlight_positions = []
        for new_move in self.current_legal_moves:
            if new_move.start == self.picked_up_position:
                self.highlight_positions.append(bitboard.get_single_position(new_move.end))



    # activates the mouse "holding" a piece
    def grab_position(self, pos_map):
        for piece_type, piece_map in enumerate(self.board.positions[self.board.colour]):
            if piece_map & pos_map:
                piece = pieces.Piece(piece_type, self.board.colour)
                break
        else:  # no friendly piece on square
            return

        self.holding = piece
        self.picked_up_position = pos_map
        self.update_move_highlights()

    # places down the current held piece
    def place_holding(self, pos):
        position = self.display.get_mouse_position(pos)
        move = self.generate_move(self.picked_up_position, position)

        if move in self.current_legal_moves:
            self.move_piece(move)
        self.holding = None
        self.picked_up_position = None
        self.highlight_positions = []

    def mouse_is_on_board(self):
        pos = pygame.mouse.get_pos()
        if (self.board_position_x <= pos[0] <= self.board_position_x + 8 * self.square_size and
                self.board_position_y <= pos[1] <= self.board_position_y + 8 * self.square_size):
            return True
        else:
            return False

    # ---------------------------------------------------------------------------------
    # MOVE FUNCTIONS
    # activates each frame it is a player's turn to move
    def player_move(self):
        mouse_button = pygame.mouse.get_pressed(3)[0]
        if mouse_button and not self.mouse_pressed:
            self.mouse_pressed = True
            if self.mouse_is_on_board():
                self.grab_position(self.display.get_mouse_position(pygame.mouse.get_pos()))

        if not mouse_button and self.mouse_pressed:
            self.mouse_pressed = False
            if self.mouse_is_on_board():
                if self.holding is not None and self.picked_up_position is not None:
                    self.place_holding(pygame.mouse.get_pos())

    # activates each frame it is an AI's turn to move (by default it is set to random)
    # can be changed via self.set_ai(self, function)
    def ai_move(self):
        if self.board.colour == 0:
            new_move = self.white_ai_move(self.board.copy())
        else:
            new_move = self.black_ai_move(self.board.copy())
        self.move_piece(new_move)

    def black_ai_move(self, p_board):
        time.sleep(0.1)
        legal_moves = self.generator.get_legal_moves()
        return random.choice(list(legal_moves))

    def white_ai_move(self, p_board):
        time.sleep(0.1)
        legal_moves = self.generator.get_legal_moves()
        return random.choice(list(legal_moves))

    def set_ai(self, func, colour=1):
        if colour == 1:
            self.black_ai_move = func
        elif colour == 0:
            self.white_ai_move = func

    # updates the current moves(if not already) and then accesses the current player's move function
    def move(self):
        if self.current_legal_moves is None:
            self.update_current_moves()
            if not self.current_legal_moves:
                return self.board.colour

        if self.board.colour == pieces.white:
            if self.white_is_ai:
                self.ai_move()
            else:
                self.player_move()
        else:
            if self.black_is_ai:
                self.ai_move()
            else:
                self.player_move()

    # ----------------------------------------------------------------------------------
    # the main loop for the game
    def run(self):  # returns 0 for white win, 1 for black win, None for draw
        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        if self.debug and self.board.logs:
                            self.board.unmake_move()
                            self.current_legal_moves = None
                            if self.board.logs:
                                self.display.update_screen(self.board)
                                time.sleep(0.05)
                                self.board.unmake_move()

            self.update()

    def update(self):
        self.display.update_screen(self.board, holding=self.holding,
                                   picked_position=self.picked_up_position,
                                   highlight_positions=self.highlight_positions)
        made_move = self.move()

        if made_move is not None:
            if self.generator.get_attack_map() & self.board.positions[self.board.colour][pieces.king]:
                return 1 - self.board.colour
            else:
                return None


if __name__ == "__main__":
    game = Game(debug=True, white_is_ai=False, black_is_ai=False, size=90)
    result = game.run()
    print(result)
