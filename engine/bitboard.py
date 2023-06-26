from gmpy2 import bit_scan1

from engine import move
from engine import pieces


# TODO merge zobrist hashing

bitset = []
p = 1
for _ in range(64):
    bitset.append(p)
    p <<= 1


right_starting_rooks = [1, 1 << 56]
left_starting_rooks = [1 << 7, 7 << 63]


def printmap(bitmap: int):
    '''
    prints the 64 bits of a bitmap of a bitboard
    '''
    position = 1
    rows = []

    for row in range(8):
        current_row = []
        for col in range(8):
            current_row.append("1" if position & bitmap else ".")
            position <<= 1
        rows.append("".join(current_row[::-1]))
    print("\n".join(rows[::-1]) + "\n")


def get_single_position(x):
    """
    implementation of bitscan-forward for singular bit position maps
    """
    return (x & -x).bit_length()-1



def iter_bitmap(bitmap):
    while bitmap:
        yield get_single_position(bitmap & (-bitmap))
        bitmap &= bitmap - 1


class Log:
    def __init__(self, info):
        '''
        class to store info of a board position to be able to undo a move
        '''
        self.info = info
        self.piece_info = []

    def add_piece(self, piece_type: pieces.Piece, map_position: int):
        '''
        adds a piece type and it's position
        NOTE this position will be ^ed with the board's piece's position.
        '''
        self.piece_info.append((piece_type, map_position))

    def replace(self, board):
        for piece_type, position_map in self.piece_info:
            board.positions[piece_type.colour][piece_type.type] ^= position_map

        board.set_game_state(*self.info)
        board.update_team_positions()


class Board:

    def set_positions(self, wp, wn, wb, wr, wq, wk, bp, bn, bb, br, bq, bk):
        """
        initializes the position maps of pieces. called by __init__ and moving methods
        also initializes the positions list (used for iterating over the board)
        """
        self.positions = [[wp, wn, wb, wr, wq, wk], [bp, bn, bb, br, bq, bk]]
        self.team_maps = [wp | wn | wb | wr | wq | wk, bp | bn | bb | br | bq | bk]

        self.all = self.team_maps[0] | self.team_maps[1]

    def set_game_state(self, ep, wlc, wrc, blc, brc, move_count, hm, colour):
        '''
        initializes every game state but not the actual positions
        '''
        self.ep_map = ep
        self.right_castles = [wrc, brc]
        self.left_castles = [wlc, blc]
        self.current_move = move_count
        self.colour = colour
        self.half_moves = hm

    def get_game_state(self):
        """
        retrieves the current game state items in the order they get called in set_game state
        used for initialising Log
        """
        return [self.ep_map, self.left_castles[0], self.right_castles[0], self.left_castles[1], self.right_castles[1],
                self.current_move, self.half_moves, self.colour]

    def increment_game_state(self):
        self.current_move += 1
        self.half_moves += 1
        self.colour = 1 - self.colour

    def update_team_positions(self):
        """
        updates wmap, bmap and all map
        """
        self.team_maps[pieces.white] = 0
        for m in self.positions[pieces.white]:
            self.team_maps[pieces.white] |= m
        self.team_maps[pieces.black] = 0
        for m in self.positions[pieces.black]:
            self.team_maps[pieces.black] |= m
        self.all = self.all = self.team_maps[0] | self.team_maps[1]

    def __init__(self, wp, wn, wb, wr, wq, wk, bp, bn, bb, br, bq, bk, ep, wlc, wrc, blc, brc, move_count, hm,
                 colour=None):
        '''
        NOTE this should not usually be used to start up a game, instead use from_fen
        initializes the bitmaps for every type of piece, the colours, the en passent pawn, the rules for castling,
        the current move and colour.
        The en passent pawn is actually the position that another pawn can take it at, not its position but one behind it
        '''

        # lists of bitmaps for each piece type
        self.positions = None
        # bitmaps for all pieces
        self.team_maps = None
        self.all = None
        # bitmap for the takeable en passent position
        self.ep_map = None
        # bools for castling rights
        self.right_castles = None
        self.left_castles = None
        # int for current ply
        self.current_move = None
        # 0 = white, 1 = black (pieces.white/pieces.white)
        self.colour = None
        self.half_moves = None

        self.set_positions(wp, wn, wb, wr, wq, wk, bp, bn, bb, br, bq, bk)
        self.set_game_state(ep, wlc, wrc, blc, brc, move_count, hm, colour)

        self.logs: list[Log] = []

    def __repr__(self):
        current_pieces = self.positions[0] + self.positions[1]
        string = ""
        position = 1
        for row in range(64):
            for i, piece in enumerate(current_pieces):

                if position & piece:
                    string += pieces.coloured_letters[i]
                    break
            else:
                string += "."
            position <<= 1
            if row % 8 == 7:
                string += "\n"
        return string[::-1].strip() + "\n"

    def copy(self):
        return Board(*self.positions[0], *self.positions[1], *self.get_game_state())

    def remove_single_castle(self, rook_position, colour):
        """
        removes a castling right when a rook is moved
        """
        if rook_position & left_starting_rooks[colour]:
            self.left_castles[colour] = False
        elif rook_position & right_starting_rooks[colour]:
            self.right_castles[colour] = False

    def move_piece_default(self, start, end, piece_type):
        '''
        moves the piece type from the start to end.
        NOTE team_peices must be a direct reference to the memory location of self.whites/blacks
        '''
        self.positions[self.colour][piece_type] ^= start | end

        if piece_type == pieces.rook:
            self.remove_single_castle(start, self.colour)

    def move_piece_ep(self, start, end, piece_type, new_log):
        '''
        does the same as move_piece_default but also removes an enpassent pawn behind the end position
        '''
        self.move_piece_default(start, end, piece_type)
        if self.colour == pieces.white:
            ep_pos = end >> 8
        else:
            ep_pos = end << 8
        self.positions[not self.colour][pieces.pawn] ^= ep_pos

        # log handling
        new_log.add_piece(pieces.Piece(pieces.pawn, not self.colour), ep_pos)

    def move_piece_promotion(self, start, end, promotion_piece_type, new_log):
        '''
            does the same as move_piece_default but places the promotion type piece onto the board
        '''
        self.positions[self.colour][pieces.pawn] ^= start
        self.positions[self.colour][promotion_piece_type] |= end

        # log handling
        new_log.piece_info.pop()  # this will be the position the pawn moved to
        # now replaced with the new type
        new_log.add_piece(pieces.Piece(promotion_piece_type, self.colour), end)

    def move_piece_castle(self, start, end, new_log):
        '''
        does the same as move_piece_default but also removes an enpassent pawn behind the end position
        NOTE this only needs a start and end position, as it assumes it is a king that has been moved
        '''
        self.positions[self.colour][pieces.king] = end
        rstart, rend = 0, 0
        if self.colour == pieces.white:  # white
            if end < start:
                rstart, rend = 1, end << 1
            elif end > start:
                rstart, rend = 1 << 7, end >> 1
        elif self.colour == pieces.black:
            if end < start:
                rstart, rend = 1 << 56, end << 1
            elif end > start:
                rstart, rend = 1 << 63, end >> 1

        self.positions[self.colour][pieces.rook] ^= rstart & self.positions[self.colour][pieces.rook] | rend

        # log handling for rook (king done in main function)
        piece_type = pieces.Piece(pieces.rook, self.colour)
        new_log.add_piece(piece_type, rstart)
        new_log.add_piece(piece_type, rend)

    def take_piece(self, position, piece_type):
        """
        the oposite of move_piece_default, takes a piece away from the
        """
        self.positions[not self.colour][piece_type] ^= position
        # castle rights removal
        if piece_type == pieces.rook:
            self.remove_single_castle(position, not self.colour)

    def update_ep_map(self, start, end):
        """
        updates the ep_map after a pawn move
        """
        # get the position between start and end
        if self.colour == pieces.white:

            if end >> 10 < start:  # end is not far away enough for move to have been double
                return
            self.ep_map = end >> 8

        else:
            if end << 10 > start:  # end is not far away enough for move to have been double
                return
            self.ep_map = end << 8

    def make_move(self, p_move: move.Move):
        '''
        Makes a move on the board and updates logic (e.g. current_move)
        NOTE this does not take legality into account.
        '''

        new_log = Log(self.get_game_state())

        start, end = p_move.start, p_move.end
        # map of the position the piece starts at

        for ind, map in enumerate(self.positions[self.colour]):
            if map & start:
                start_piece_type = ind
                piece_type = pieces.Piece(start_piece_type, self.colour)
                # add piece setting to log
                new_log.add_piece(piece_type, start)
                # add piece removal to log
                new_log.add_piece(piece_type, end)
                break
        else:
            raise Exception("Cannot move from an empty square")

        if p_move.flag == move.Flags.none:
            self.move_piece_default(start, end, start_piece_type)
        elif p_move.flag == move.Flags.en_passent:
            self.move_piece_ep(start, end, start_piece_type, new_log)

        elif p_move.flag == move.Flags.promotion:
            self.move_piece_promotion(start, end, p_move.promotion_piece, new_log)

        elif p_move.flag == move.Flags.castle:
            self.move_piece_castle(start, end, new_log)

        # map of the position the piece ends at
        end_piece_type = None
        for ind, bitmap in enumerate(self.positions[not self.colour]):
            if bitmap & end:
                end_piece_type = ind
                new_log.add_piece(pieces.Piece(end_piece_type, not self.colour), end)
                break

        if end_piece_type is not None:  # if we are taking another piece
            self.take_piece(end, end_piece_type)

        if end_piece_type is None and p_move.flag != move.Flags.en_passent:
            self.half_moves = 0

        # update ep_map
        self.ep_map = 0
        if start_piece_type == pieces.pawn:
            self.update_ep_map(start, end)

        # remove castle rights
        if start_piece_type == pieces.king:
            self.right_castles[self.colour] = False
            self.left_castles[self.colour] = False

        self.increment_game_state()
        self.update_team_positions()
        self.logs.append(new_log)

    def unmake_move(self):
        log = self.logs.pop()
        log.replace(self)

    @classmethod
    def from_fen(cls, fen: str):
        '''
        returns a fully initialized instance of a Board from a FEN string
        :param fen: FEN string of board to initialize
        :return: initialized Board
        '''
        data = fen.split()
        while len(data) < 6:
            data.append("-")
        layout, colour, castles, pawn_move, half_move, full_move = data

        # getting positions
        init_pieces = [0 for _ in pieces.coloured_values]  # wp, wn, wb, wr etc...
        position = 1  # will be left shifted to access each position
        for char in layout[::-1]:
            if char == "/":
                continue
            elif "0" < char <= "9":
                position <<= int(char)
            else:
                piece_val = pieces.coloured_values[char]
                init_pieces[piece_val] |= position
                position <<= 1

        # colour
        init_colour = pieces.white if colour == "w" else pieces.black
        # castling rights
        wlc, wrc, blc, brc = "Q" in castles, "K" in castles, "q" in castles, "k" in castles
        # en passent bitmap
        ep = 0
        if pawn_move != "-":
            last_move_end = ((8 - move.column_letters.index(pawn_move[0])) + 8 * (int(pawn_move[1]) - 1)) - 1
            if init_colour == pieces.white:
                ep = 1 << last_move_end >> 8
            else:
                ep = 1 << last_move_end << 8

        # half and full move counts
        hm = 0
        if half_move != "-":
            hm = int(half_move)
        moves = init_colour
        if full_move != "-":
            moves = int(full_move)
        return cls(*init_pieces, ep, wlc, wrc, blc, brc, moves, hm, init_colour)

