from engine import bitboard
from engine import move_generator
from engine import evaluate
from engine import order_moves
from engine import pieces

from typing import Optional

import time

DEFAULT_DEPTH = 3
DEFAULT_TIME_LIMIT = 0.5 # s
QUIESCENCE = True


class Bot:
    def __init__(self, move_time_limit=DEFAULT_TIME_LIMIT):
        """
        stores functionality to find the "best" move from any board position
        """
        self.generator: Optional[move_generator.Generator] = None
        self.time_limit = move_time_limit
        self.start_time = 0  # reset at self.search
        self.nodes = 0
        self.best_root_move = None
        self.best_root_score = None

    def should_finish_search(self):
        """
        called during search
        returns whether self.search() has gone of for oo long
        """
        return time.time() - self.start_time > self.time_limit

    def search(self, board: bitboard.Board):
        """
        returns the "best" move from a given board position
        """
        self.start_time = time.time()
        self.generator = move_generator.Generator(board)

        # iterative deepening
        for depth in range(1, 1000):
            if self.should_finish_search():
                break
            # updates self.best_root_move/score
            self.negamax_root(board, DEFAULT_DEPTH)

        print("value:", self.best_root_score)
        print("nodes:", self.nodes)
        print("time:", time.time()-self.start_time)
        return self.best_root_move


    def negamax_root(self, board, depth):
        moves_list = self.generator.get_legal_moves()
        moves_list = order_moves.order(board, moves_list)

        self.nodes += len(moves_list)

        best_score = float("-inf")
        best_move = None

        for move in moves_list:
            board.make_move(move)
            score = -self.negamax(board, depth - 1, float("-inf"), -best_score)
            board.unmake_move()

            if self.should_finish_search():
                return

            if score > best_score:
                best_score = score
                best_move = move

        # only update root values when we have done a full search
        self.best_root_move = best_move
        self.best_root_score = best_score

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
            score = -self.negamax(board, depth - 1, -beta, -alpha)
            board.unmake_move()

            if self.should_finish_search():
                break

            # tif we won't get reached in perfect play by opponent
            if score >= beta:
                return beta
            # if this is the new best move
            if score > alpha:
                alpha = score
        return alpha


class GoodBot:
    def __init__(self):
        """
        stores functionality to find the "best" move from any board position
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

        for move in moves_list:
            board.make_move(move)
            score = -self.negamax(board, DEFAULT_DEPTH - 1, -beta, -alpha)
            board.unmake_move()
            move_score_list.append((move, score))

            if score > alpha:
                alpha = score

        best_move, value = max(move_score_list, key=lambda pair: pair[1])
        if board.colour == pieces.black:  # as we are using negamax
            value *= -1
        print(move_score_list)
        print("value:", value)
        print("nodes:", self.nodes)
        return best_move

    def negamax(self, board, depth, alpha, beta):

        if depth == 0:
            if QUIESCENCE:
                return self.quiescence(board, -beta, -alpha)
            else:
                return evaluate.evaluate(board)

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
        return best

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
