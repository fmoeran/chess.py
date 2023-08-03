from engine.evaluate import piece_worths, piece_square
from engine.bitboard import Board, get_single_position
from engine.move import Move, Flags
from engine.transposition import TranspositionTable


# gives an estimated value of how good a move is
def estimate_value(board: Board, move: Move, best_move):
    score = 0
    start_piece_value, end_piece_value = None, None

    for piece, pos_map in enumerate(board.positions[board.colour]):
        if move.start & pos_map:
            start_piece_value = piece
            break
    for piece, pos_map in enumerate(board.positions[not board.colour]):
        if move.start & pos_map:
            end_piece_value = piece
            break

    # if we take a piece, get the worth of that piece - worth of taking piece
    if end_piece_value is not None:
        score += piece_worths[end_piece_value] - piece_worths[start_piece_value] / 10

    # if the move is a promotion
    if move.flag == Flags.promotion:
        score += piece_worths[move.promotion_piece]

    score -= piece_square[board.colour][start_piece_value][get_single_position(move.start)]
    score += piece_square[board.colour][start_piece_value][get_single_position(move.end)]

    if move == best_move:
        score += 10000

    return score


def order(board: Board, moves: list[Move], table: TranspositionTable):
    """
    roughly orders a list of moves in a given board.
    better moves are placed first
    """
    best_move = table[board.zobrist].move
    move_value_pairs = [(move, estimate_value(board, move, best_move)) for move in moves]
    move_value_pairs = sorted(move_value_pairs, key=lambda pair: pair[1], reverse=True)
    sorted_list = list(map(lambda pair: pair[0], move_value_pairs))
    return sorted_list
