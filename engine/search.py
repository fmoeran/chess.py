from engine import bitboard
from engine import move_generator
from engine import evaluate
from engine import order_moves
from engine import pieces

import tqdm

from typing import Optional

DEFAULT_DEPTH = 4
QUIESCENCE = True


class Bot:
    def __init__(self):
        """
        stores functionality to find the "best" move from any board position
        :param depth: the depth that the minimax search will go to
        """
        self.generator: Optional[move_generator.Generator] = None
        self.nodes = 0

    def search(self, board: bitboard.Board):
        self.generator = move_generator.Generator(board)

        moves_list = self.generator.get_legal_moves()

        self.nodes = len(moves_list)
        moves_list = order_moves.order(board, moves_list)

        move_score_list = []  # (move, score)


        alpha = float("-inf")
        beta = float("inf")

        for move in tqdm.tqdm(moves_list, desc="Searching", ncols=100):
        #for move in moves_list:
            board.make_move(move)
            score = -self.negamax(board, DEFAULT_DEPTH - 1, -beta, -alpha)
            board.unmake_move()
            move_score_list.append((move, score))

            if score > alpha:
                alpha = score

        best_move, value = max(move_score_list, key=lambda pair: pair[1])
        if board.colour == pieces.black:  # as we are using negamax
            value *= -1
        #print(move_score_list)
        print("value:", value)
        print("nodes:", self.nodes)
        print("evals:", evaluate.count)
        return best_move

    def negamax(self, board, depth, alpha, beta):

        if depth == 0:
            if QUIESCENCE: return self.quiescence(board, -beta, -alpha)
            else: return evaluate.evaluate(board)

        moves = self.generator.get_legal_moves()
        if not moves:
            # either a win, loss, or draw
            if self.generator.check_mask == ~0:  # not in check
                return 0
            else:
                return float("-inf")

        moves = order_moves.order(board, moves)

        best = float("-inf")

        for move in moves:
            self.nodes += 1
            board.make_move(move)
            score = -self.negamax(board, depth - 1, -beta, -alpha)
            board.unmake_move()
            if score >= beta:  # this move won't get reached in perfect play by opponent
                return beta
            if score > best:
                best = score
                if score > alpha:  # we have found a better move than the current best
                    alpha = score
        return best  # best possible move from the list that can be reached in perfect play

    def quiescence(self, board, alpha, beta):
        current_eval = evaluate.evaluate(board)
        if current_eval >= beta:
            return beta
        if current_eval > alpha:
            alpha = current_eval

        moves = self.generator.get_legal_moves(only_captures=True)


        for move in moves:
            self.nodes += 1
            board.make_move(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.unmake_move()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
