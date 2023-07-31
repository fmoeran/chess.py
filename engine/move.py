from engine import pieces

from enum import Enum

column_letters = ["a", "b", "c", "d", "e", "f", "g", "h"]


class Flags(Enum):
    """
    enum for every type of move.
    e.g.: Flags.en_passent
    """
    none = 0
    promotion = 1
    en_passent = 2
    castle = 3


# a class to hold an instance of a type of move
class Move:
    def __init__(self, start: int, end: int, flag=Flags.none, promotion_piece=0):
        """
        :param start: bitmap of start position
        :param end: bitmap of end position
        :param flag: a flag from Flags(Enum)
        :param promotion_piece: the piece type to promote to if flag = Flags.promotion
        """
        self.start = start
        self.end = end
        self.flag = flag
        self.promotion_piece = promotion_piece

    def notate(self):
        """
        returns a string of the coordinate notation of the move being represented
        e.g. e7e8Q (promotion onto e8 into queen)
        """
        position = 0
        start_pos = 0
        end_pos = 0
        # iterate all positions to find the int positions
        # of the start and end points
        while (1 << position) <= (1 << 63):
            if self.start == 1 << position:
                start_pos = position
            if self.end == 1 << position:
                end_pos = position
            position += 1
        #                            column                    row
        starting = column_letters[7 - start_pos % 8] + str(start_pos // 8 + 1)
        ending = column_letters[7 - end_pos % 8] + str(end_pos // 8 + 1)
        promotion = ""
        # if the move is a promotion add that piece's character onto the end
        if self.flag == Flags.promotion:
            promotion = str(pieces.letters[self.promotion_piece])
        return starting + ending + promotion

    def __repr__(self):
        return self.notate()

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.start == other.start and self.end == other.end and self.promotion_piece == other.promotion_piece and self.flag == other.flag

