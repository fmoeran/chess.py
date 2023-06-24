from engine.evaluate import piece_worths, piece_square
from engine.bitboard import Board, get_single_position
from engine.move import Move, Flags
from engine.pieces import Piece

# gives a estimated value of how good a move is
def estimate_value(board: Board, move: Move):
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

    start_piece = Piece(start_piece_value, board.colour)

    # if we take a piece, get the worth of that piece - worth of taking piece
    if end_piece_value is not None:
        score += piece_worths[end_piece_value] - piece_worths[start_piece_value]

    # if the move is a promotion
    if move.flag == Flags.promotion:
        score += piece_worths[move.promotion_piece]

    # if it's attacked by a pawn
    # if move.end in board.get_enemy_pawn_attacks():
    #     score -= piece_worths[start_piece.type] + piece_worths[pieces.pawn]


    score -= piece_square[board.colour][start_piece_value][get_single_position(move.start)]
    score += piece_square[board.colour][start_piece_value][get_single_position(move.end)]

    return score


def order(board, moves):
    move_value_pairs = [(move, estimate_value(board, move)) for move in moves]
    move_value_pairs = sorted(move_value_pairs, key=lambda pair: pair[1], reverse=True)
    sorted_list = list(map(lambda pair: pair[0], move_value_pairs))
    return sorted_list
