import bitboard
import move_generator
import evaluate
import order_moves
import tqdm

from typing import Optional

DEFAULT_DEPTH = 4
nodes = 0

generator: Optional[move_generator.Generator] = None


# gives the best move from a position
def search(board: bitboard.Board):
    global nodes, generator

    generator = move_generator.Generator(board)

    moves_list = generator.get_legal_moves()

    nodes = len(moves_list)
    moves_list = order_moves.order(board, moves_list)

    move_score_list = []  # (move, score)

    maximizing = board.colour == 0

    alpha = float("-inf")
    beta = float("inf")

    for move in tqdm.tqdm(moves_list, desc="Searching", ncols=100):

        board.make_move(move)
        # score = __minimax(p_board, DEFAULT_DEPTH - 1, not maximizing, alpha, beta)
        score = negamax(board, DEFAULT_DEPTH - 1, alpha, beta)
        board.unmake_move()
        move_score_list.append((move, score))

        if maximizing:
            if alpha < score:
                alpha = score
        else:
            if beta > score:
                beta = score

    func = max if board.colour == 0 else min
    best_move, value = func(move_score_list, key=lambda pair: pair[1])
    if board.colour == 0:  # as we are using negamax
        value *= -1

    print("value:", value)
    print("nodes:", nodes)
    return best_move


def negamax(board, depth, alpha, beta):
    global nodes

    if depth == 0:
        return evaluate.evaluate(board)

    moves = generator.get_legal_moves()
    if not moves:
        # either a win, loss, or draw
        if generator.check_mask == ~0:  # not in check
            return 0
        else:
            return float("-inf")

    moves = order_moves.order(board, moves)

    for move in moves:
        nodes += 1
        board.make_move(move)
        val = -negamax(board, depth - 1, -beta, -alpha)
        board.unmake_move()
        if val >= beta:  # this move won't get reached in perfect play by opponent
            return beta
        if val > alpha:  # we have found a better move than the current best
            alpha = val
    return alpha  # best possible move from the list that can be reached in perfect play


def quies(board, alpha, beta):  # TODO: reaaallly slow idky and searching through 30x more than the minimax itsef is
    global nodes
    val = evaluate.evaluate(board)
    if val >= beta:  # too good of a position already, opposition wont play it, can be cut off
        return beta
    if val > alpha:  # new best move found, update alpha
        alpha = val

    capture_moves = generator.get_legal_captures(board)
    capture_moves = order_moves.order(board, capture_moves)

    # print(list(map(lambda move: board.positions.get(move.end) is not None, capture_moves)))

    for move in capture_moves:  # same logic as negamax
        # nodes += 1
        board.make_move(move)
        val = -quies(board, -beta, -alpha)
        board.undo_move()
        if val >= beta:
            return beta
        if val > alpha:
            alpha = val
    return alpha
