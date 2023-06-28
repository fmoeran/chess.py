from engine import bitboard
from engine import pieces


piece_worths = [
    100,  # pawn
    300,  # knight
    350,  # bishop
    500,  # rook
    900,  # queen
    0     # king (ignored)
]


piece_square = [[
     # black pawn
         [0, 0, 0, 0, 0, 0, 0, 0,
          50, 50, 50, 50, 50, 50, 50, 50,
          10, 10, 20, 30, 30, 20, 10, 10,
          5, 5, 10, 25, 25, 10, 5, 5,
          0, 0, 0, 20, 20, 0, 0, 0,
          5, -5, -10, 0, 0, -10, -5, 5,
          5, 10, 10, -20, -20, 10, 10, 5,
          0, 0, 0, 0, 0, 0, 0, 0],
    # black knight
         [-50, -40, -30, -30, -30, -30, -40, -50,
          -40, -20, 0, 5, 5, 0, -20, -40,
          -30, 5, 10, 15, 15, 10, 5, -30,
          -30, 0, 15, 20, 20, 15, 0, -30,
          -30, 5, 15, 20, 20, 15, 5, -30,
          -30, 0, 10, 15, 15, 10, 0, -30,
          -40, -20, 0, 0, 0, 0, -20, -40,
          -50, -40, -30, -30, -30, -30, -40, -50],
    # black bishop
         [-20, -10, -10, -10, -10, -10, -10, -20,
          -10, 0, 0, 0, 0, 0, 0, -10,
          -10, 0, 5, 10, 10, 5, 0, -10,
          -10, 5, 5, 10, 10, 5, 5, -10,
          -10, 0, 10, 10, 10, 10, 0, -10,
          -10, 10, 10, 10, 10, 10, 10, -10,
          -10, 5, 0, 0, 0, 0, 5, -10,
          -20, -10, -10, -10, -10, -10, -10, -20],
    # black rook
         [0, 0, 0, 0, 0, 0, 0, 0,
          5, 10, 10, 10, 10, 10, 10, 5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5,
           0, 0, 0, 5, 5, 0, 0, 0],
    # black queen
         [-20, -10, -10, -5, -5, -10, -10, -20,
          -10, 0, 0, 0, 0, 5, 0, -10,
          -10, 0, 5, 5, 5, 5, 5, -10,
          -5, 0, 5, 5, 5, 5, 0, 0,
          -5, 0, 5, 5, 5, 5, 0, -5,
          -10, 0, 5, 5, 5, 5, 0, -10,
          -10, 0, 0, 0, 0, 0, 0, -10,
          -20, -10, -10, -5,-5, -10, -10, -20],
    # black king
         [-30, -40, -40, -50, -50, -40, -40, -30,
          -30, -40, -40, -50, -50, -40, -40, -30,
          -30, -40, -40, -50, -50, -40, -40, -30,
          -30, -40, -40, -50, -50, -40, -40, -30,
          -20, -30, -30, -40, -40, -30, -30, 20,
          -10, -20, -20, -20, -20, -20, -20, -10,
          20, 20, 0, 0, 0, 0, 20, 20,
          20, 30, 10, 0, 0, 10, 30, 20],

]]
# make the black versions
white_piece_squares = [table[::-1] for table in piece_square[0]]
piece_square.insert(pieces.white, white_piece_squares)

def count_1s(num):
    return num.bit_count()

def static_evaluate(board: bitboard.Board): # statically estimates a board's value
    score_sum = 0

    for piece, worth in enumerate(piece_worths):
        white_count = count_1s(board.positions[pieces.white][piece])
        black_count = count_1s(board.positions[pieces.black][piece])
        score_sum += white_count * worth
        score_sum -= black_count * worth

    # the total sum of the value of positions on the board
    position_sum = 0
    mult = 1
    for colour, squares in enumerate(piece_square):
        for piece, square in enumerate(squares):
            for position in bitboard.iter_bitmap(board.positions[colour][piece]):
                position_sum += mult * square[position]
        mult = -1
    total = score_sum + position_sum
    return total

# returns how good the board is for its current colour to play (aka, you always want it to be positive)
def evaluate(board):
    res = static_evaluate(board)
    if board.colour == 1: res = -res
    return res


