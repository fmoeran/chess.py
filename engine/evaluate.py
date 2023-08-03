from engine import bitboard
from engine import pieces

piece_worths = [
    100,  # pawn
    300,  # knight
    350,  # bishop
    500,  # rook
    900,  # queen
    0  # king (ignored)
]

piece_square = [[
    # pawn
    [0, 0, 0, 0, 0, 0, 0, 0,
     50, 50, 50, 50, 50, 50, 50, 50,
     10, 10, 20, 30, 30, 20, 10, 10,
     5, 5, 10, 25, 25, 10, 5, 5,
     0, 0, 0, 20, 20, 0, 0, 0,
     5, -5, -10, 0, 0, -10, -5, 5,
     5, 10, 10, -20, -20, 10, 10, 5,
     0, 0, 0, 0, 0, 0, 0, 0],
    # knight
    [-50, -40, -30, -30, -30, -30, -40, -50,
     -40, -20, 0, 5, 5, 0, -20, -40,
     -30, 5, 10, 15, 15, 10, 5, -30,
     -30, 0, 15, 20, 20, 15, 0, -30,
     -30, 5, 15, 20, 20, 15, 5, -30,
     -30, 0, 10, 15, 15, 10, 0, -30,
     -40, -20, 0, 0, 0, 0, -20, -40,
     -50, -40, -30, -30, -30, -30, -40, -50],
    # bishop
    [-20, -10, -10, -10, -10, -10, -10, -20,
     -10, 0, 0, 0, 0, 0, 0, -10,
     -10, 0, 5, 10, 10, 5, 0, -10,
     -10, 5, 5, 10, 10, 5, 5, -10,
     -10, 0, 10, 10, 10, 10, 0, -10,
     -10, 10, 10, 10, 10, 10, 10, -10,
     -10, 5, 0, 0, 0, 0, 5, -10,
     -20, -10, -10, -10, -10, -10, -10, -20],
    # rook
    [0, 0, 0, 0, 0, 0, 0, 0,
     5, 10, 10, 10, 10, 10, 10, 5,
     -5, 0, 0, 0, 0, 0, 0, -5,
     -5, 0, 0, 0, 0, 0, 0, -5,
     -5, 0, 0, 0, 0, 0, 0, -5,
     -5, 0, 0, 0, 0, 0, 0, -5,
     -5, 0, 0, 0, 0, 0, 0, -5,
     0, 0, 0, 5, 5, 0, 0, 0],
    # queen
    [-20, -10, -10, -5, -5, -10, -10, -20,
     -10, 0, 0, 0, 0, 5, 0, -10,
     -10, 0, 5, 5, 5, 5, 5, -10,
     -5, 0, 5, 5, 5, 5, 0, 0,
     -5, 0, 5, 5, 5, 5, 0, -5,
     -10, 0, 5, 5, 5, 5, 0, -10,
     -10, 0, 0, 0, 0, 0, 0, -10,
     -20, -10, -10, -5, -5, -10, -10, -20],
    #  king
    [-30, -40, -40, -50, -50, -40, -40, -30,
     -30, -40, -40, -50, -50, -40, -40, -30,
     -30, -40, -40, -50, -50, -40, -40, -30,
     -30, -40, -40, -50, -50, -40, -40, -30,
     -20, -30, -30, -40, -40, -30, -30, 20,
     -10, -20, -20, -20, -20, -20, -20, -10,
     20, 20, 0, 0, 0, 0, 20, 20,
     20, 30, 10, 0, 0, 10, 30, 20],

]]
# make the white versions
white_piece_squares = [table[::-1] for table in piece_square[0]]
piece_square.insert(pieces.white, white_piece_squares)


def evaluate(board: bitboard.Board):
    """
    evaluates how good a board is for the board's current colour
    """
    return evaluate_colour(board, board.colour) - evaluate_colour(board, not board.colour)


def evaluate_colour(board, colour):
    res = 0

    for piece, worth in enumerate(piece_worths):
        count = board.positions[colour][piece].bit_count()
        res += count * worth

    # the total sum of the value of positions on the board
    for piece, square in enumerate(piece_square[colour]):
        for position in bitboard.iter_bitmap(board.positions[colour][piece]):
            res += square[position]

    return res
