from engine import move

from enum import Enum


# types of alpha beta tree search nodes
class NodeType(Enum):
    exact = 0
    lower_bound = 1
    upper_bound = 2


class TTEntry:
    def __init__(self, zobrist, depth, move, value, node_type):
        # the zobrist hash of the board
        self.zobrist = zobrist
        # the depth that the TTEntry was evaluated at
        self.depth = depth
        # the best move the was found for the position during search
        self.move = move
        # the value of the position evaluated to a depth of self.depth
        self.value = value
        # the type of node cutoff during alpha beta search
        self.node_type = node_type


class TranspositionTable:
    def __init__(self, size):
        self.size = size
        self.table = [TTEntry(0, -99999, move.Move(0, 0), 0, NodeType.exact) for _ in range(size)]

    def __getitem__(self, zobrist):
        return self.table[zobrist % self.size]

    def contains(self, zobrist, depth, alpha, beta):
        """
        whether calling TT[zobrist] would return an entry that is correct for the current situation
        """
        entry = self[zobrist]
        if entry.zobrist == zobrist and entry.depth >= depth and \
                (entry.node_type == NodeType.exact or
                entry.node_type == NodeType.lower_bound and entry.value >= beta or
                entry.node_type == NodeType.upper_bound and entry.value <= alpha):
            return True
        else:
            return False

    def replace(self, entry):
        self.table[entry.zobrist % self.size] = entry



