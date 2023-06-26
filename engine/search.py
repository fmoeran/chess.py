from engine import bitboard
from engine import move_generator
from engine import evaluate
from engine import order_moves

import tqdm

from typing import Optional

DEFAULT_DEPTH = 4


class Bot:
    def __init__(self, depth=DEFAULT_DEPTH):
        """
        stores functionality to find the "best" move from any board position
        :param depth: the depth that the minimax search will go to
        """
        self.depth = depth
        self.generator: Optional[move_generator.Generator] = None
        self.nodes = 0

    def search(self, board: bitboard.Board):
        self.generator = move_generator.Generator(board)

        moves_list = self.generator.get_legal_moves()

        self.nodes = len(moves_list)
        moves_list = order_moves.order(board, moves_list)

        move_score_list = []  # (move, score)

        maximizing = board.colour == 0

        alpha = float("-inf")
        beta = float("inf")

        for move in tqdm.tqdm(moves_list, desc="Searching", ncols=100):
        #for move in moves_list:
            board.make_move(move)
            # score = __minimax(p_board, DEFAULT_DEPTH - 1, not maximizing, alpha, beta)
            score = self.negamax(board, DEFAULT_DEPTH - 1, alpha, beta)
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
        print("nodes:", self.nodes)
        return best_move

    def negamax(self, board, depth, alpha, beta):

        if depth == 0:
            return evaluate.evaluate(board)

        moves = self.generator.get_legal_moves()
        if not moves:
            # either a win, loss, or draw
            if self.generator.check_mask == ~0:  # not in check
                return 0
            else:
                return float("-inf")

        moves = order_moves.order(board, moves)

        for move in moves:
            self.nodes += 1
            board.make_move(move)
            val = -self.negamax(board, depth - 1, -beta, -alpha)
            board.unmake_move()
            if val >= beta:  # this move won't get reached in perfect play by opponent
                return beta
            if val > alpha:  # we have found a better move than the current best
                alpha = val
        return alpha  # best possible move from the list that can be reached in perfect play

