letters = "PNBRQK"
values = {piece_letter: value for value, piece_letter in enumerate(letters)}

coloured_letters = "PNBRQKpnbrqk"
coloured_values = {piece_letter: value for value, piece_letter in enumerate(coloured_letters)}

# piece values
pawn = 0
knight = 1
bishop = 2
rook = 3
queen = 4
king = 5

# colour values
white = 0
black = 1


# A class to encapsulate a piece value and colour
class Piece:
    def __init__(self, type, colour):
        self.type = type
        self.colour = colour

    def __repr__(self):
        """
        returns the character for the represented piece type. e.g. K for white king
        """
        letter = coloured_letters[hash(self)]
        return letter

    def __hash__(self):
        """
        returns the same value as coloured_values[str(self)]
        """
        return self.type + self.colour * 6

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.type == other.type and self.colour == other.colour
