from engine import bitboard
from engine import move_generator
from engine import evaluate
from engine import tapered_eval
from engine import order_moves
from engine import pieces
from engine import transposition

from typing import Optional

import time

DEFAULT_DEPTH = 3
DEFAULT_TIME_LIMIT = 1  # s
QUIESCENCE = True
USE_TT = True
DEFAULT_TT_SIZE = 1000000

POSITIVE_INFINITY = 9999999
NEGATIVE_INFINITY = -POSITIVE_INFINITY
CHECKMATE_VALUE = -999999


class Bot:
    def __init__(self, move_time_limit=DEFAULT_TIME_LIMIT, tt_size=DEFAULT_TT_SIZE):
        """
        stores functionality to find the "best" move from any board position
        """
        self.generator: Optional[move_generator.Generator] = None
        self.time_limit = move_time_limit
        self.start_time = 0  # reset at self.search
        self.nodes = 0
        self.depth = 0
        self.best_root_move = None
        self.best_root_score = 0
        self.tt = transposition.TranspositionTable(tt_size)
        self.tt_hits = 0

    def should_finish_search(self):
        """
        called during search
        returns whether self.search() has gone of for oo long
        """
        return time.time() - self.start_time > self.time_limit and self.best_root_move is not None

    def search(self, board: bitboard.Board):
        """
        returns the "best" move from a given board position
        """
        self.start_time = time.time()
        self.generator = move_generator.Generator(board)

        self.best_root_move = self.generator.get_legal_moves()[0]
        self.best_root_score = 0

        self.tt_hits = 0

        # iterative deepening
        self.depth = 1
        while self.depth < 1000:
            if self.should_finish_search():
                break
            # updates self.best_root_move/score
            self.negamax_root(board, self.depth)
            self.depth += 1

        if board.colour == pieces.black:
            self.best_root_score *= -1
        print("depth:", self.depth)
        print("value:", self.best_root_score)
        print("tt hits:", self.tt_hits)
        print("nodes:", self.nodes)
        return self.best_root_move

    def negamax_root(self, board, depth):
        moves_list = self.generator.get_legal_moves()
        moves_list = order_moves.order(board, moves_list, self.tt)

        self.nodes += len(moves_list)

        best_score = NEGATIVE_INFINITY
        best_move = None

        for move in moves_list:
            board.make_move(move)
            score = -self.negamax(board, depth - 1, NEGATIVE_INFINITY, -best_score)
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
        if USE_TT:
            if self.tt.contains(board.zobrist, depth, alpha, beta):
                self.tt_hits += 1
                return self.tt[board.zobrist].value

        if depth == 0:
            if QUIESCENCE:
                return self.qsearch(board, depth, alpha, beta)
            else:
                return tapered_eval.evaluate(board)

        moves = self.generator.get_legal_moves()
        if not moves:
            # either a win, loss, or draw
            if self.generator.check_mask == ~0:  # not in check
                return 0
            else:
                return CHECKMATE_VALUE - depth

        moves = order_moves.order(board, moves, self.tt)

        node_type = transposition.NodeType.upper_bound

        best_move = None

        for move in moves:
            self.nodes += 1
            board.make_move(move)
            score = -self.negamax(board, depth - 1, -beta, -alpha)
            board.unmake_move()

            if self.should_finish_search():
                break

            # tif we won't get reached in perfect play by opponent
            if score >= beta:
                node_type = transposition.NodeType.lower_bound
                best_move = move
                alpha = beta
                break
            # if this is the new best move
            if score > alpha:
                node_type = transposition.NodeType.exact
                best_move = move
                alpha = score

        new_entry = transposition.TTEntry(board.zobrist, depth, best_move, alpha, node_type)
        self.tt.replace(new_entry)

        return alpha

    def qsearch(self, board, depth, alpha, beta):
        if USE_TT:
            if self.tt.contains(board.zobrist, depth, alpha, beta):
                self.tt_hits += 1
                return self.tt[board.zobrist].value

        current_eval = tapered_eval.evaluate(board)
        # the best move might not be a capture
        # so we set a baseline evaluation here
        if current_eval >= beta:
            return beta
        if current_eval > alpha:
            alpha = current_eval

        # search only moves that are captures
        moves = self.generator.get_legal_moves(only_captures=True)

        best_move = None
        node_type = transposition.NodeType.lower_bound

        for move in moves:
            self.nodes += 1
            board.make_move(move)
            score = -self.qsearch(board, depth-1, -beta, -alpha)
            board.unmake_move()

            if self.should_finish_search():
                break

            # beta cutoff just like in negamax
            if score >= beta:
                node_type = transposition.NodeType.lower_bound
                best_move = move
                alpha = beta
                break
            # maximise best move score
            if score > alpha:
                node_type = transposition.NodeType.exact
                best_move = move
                alpha = score

        new_entry = transposition.TTEntry(board.zobrist, depth, best_move, alpha, node_type)
        self.tt.replace(new_entry)

        return alpha
