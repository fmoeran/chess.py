letters = ["P", "N", "B", "R", "Q", "K"]
values = {piece_letter: value for value, piece_letter in enumerate(letters)}

coloured_letters = "PNBRQKpnbrqk"
coloured_values = {piece_letter: value for value, piece_letter in enumerate(coloured_letters)}


pawn = 0
knight = 1
bishop = 2
rook = 3
queen = 4
king = 5

white = 0
black = 1


class Piece:
    def __init__(self, type, colour):
        self.type = type
        self.colour = colour

    def __repr__(self):
        letter = letters[self.type]
        if self.colour == black:
            letter = letter.lower()
        return letter

    def __hash__(self):
        return self.type + self.colour*6

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.type == other.type and self.colour == other.colour
