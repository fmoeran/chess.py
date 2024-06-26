from random import randint, seed
from time import time

from engine import move
from engine import pieces

right_starting_rooks = [1, 1 << 56]
left_starting_rooks = [1 << 7, 7 << 63]

# zobrist hashing numbers
max_zob = (1 << 65) - 1

seed(1)

def make_zobrist():
    return randint(0, max_zob)


zobrist_pieces = [[[make_zobrist() for i in range(64)] for j in range(6)] for k in range(2)]
zobrist_team = make_zobrist()
zobrist_right_castles = [make_zobrist(), make_zobrist()]
zobrist_left_castles = [make_zobrist(), make_zobrist()]
zobrist_ep = [make_zobrist() for i in range(8)]

seed(time())

bitset = []
p = 1
for _ in range(64):
    bitset.append(p)
    p <<= 1


def printmap(bitmap: int):
    '''
    prints the 64 bits of a bitmap of a bitboard
    '''

    # position starts at a8
    position = 1 << 63
    for i in range(64):
        # print a 1 when we find a set bit
        print("1" if position & bitmap else ".", end="")
        # we reached the end of a row
        if i % 8 == 7:
            print()
        position >>= 1
    print()


def get_single_position(bitmap):
    """
    implementation of bitscan-forward for singular bit position maps
    """
    return (bitmap & -bitmap).bit_length() - 1


def iter_bitmap(bitmap):
    """
    A generator to loop through the indexes of every set bit in a bitmap
    """
    while bitmap:
        yield get_single_position(bitmap & (-bitmap))
        bitmap &= bitmap - 1


class Log:
    def __init__(self, board):
        '''
        class to store info of a board position to be able to undo a move
        '''
        self.info = board.get_game_state()
        self.zobrist = board.zobrist
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
        board.zobrist = self.zobrist


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
        if self.colour == pieces.black:
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

    def create_zobrist(self):
        zob = 0
        for i, team in enumerate(self.positions):
            for j, piece_positions in enumerate(team):
                selector = 1
                for k in range(64):
                    if selector & piece_positions:
                        zob ^= zobrist_pieces[i][j][k]
                    selector <<= 1
        zob ^= zobrist_team * self.colour

        return zob

    def alter_zobrist_pieces(self):
        """
        updates self.zobrist according to the data inside self.currently_altering
        """
        for piece, pos_map in self.currently_altering:
            int_position = get_single_position(pos_map)
            self.zobrist ^= zobrist_pieces[piece.colour][piece.type][int_position]

    def toggle_team_zobrist(self):
        self.zobrist ^= zobrist_team

    def toggle_ep_zobrist(self, pos_map):
        position = get_single_position(pos_map)
        ind = position % 8
        self.zobrist ^= zobrist_ep[ind]

    def toggle_left_castle_zobrist(self, colour):
        self.zobrist ^= zobrist_left_castles[colour]

    def toggle_right_castle_zobrist(self, colour):
        self.zobrist ^= zobrist_right_castles[colour]

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

        # a stack of the past moves that the board has made
        self.past_moves = []

        self.set_positions(wp, wn, wb, wr, wq, wk, bp, bn, bb, br, bq, bk)
        self.set_game_state(ep, wlc, wrc, blc, brc, move_count, hm, colour)

        # stores a list of piece positions that will be toggled when a move is made.
        # altered and reset each make_move call
        self.currently_altering = []  # (Piece, position_map)

        self.logs: list[Log] = []

        self.zobrist = self.create_zobrist()

    def __repr__(self):
        current_pieces = self.positions[0] + self.positions[1]
        string = ""
        position = 1 << 63
        for sq in range(64):
            for i, piece in enumerate(current_pieces):

                if position & piece:
                    string += pieces.coloured_letters[i]
                    break
            else:
                string += "."
            if sq % 8 == 7:
                string += "\n"
            position >>= 1
        return string

    def __hash__(self):
        return self.zobrist

    def copy(self):
        return Board(*self.positions[0], *self.positions[1], *self.get_game_state())

    def make_move(self, p_move: move.Move):
        '''
        Makes a move on the board and updates logic (e.g. current_move)
        NOTE this does not take legality into account.
        '''

        self.past_moves.append(p_move)

        new_log = Log(self)
        self.currently_altering = []

        start, end = p_move.start, p_move.end
        # map of the position the piece starts at

        for ind, map in enumerate(self.positions[self.colour]):
            if map & start:
                start_piece_type = ind
                break
        else:
            raise Exception("Cannot move from an empty or enemy square")

        if p_move.flag == move.Flags.none:
            self.move_piece_default(start, end, start_piece_type)
        elif p_move.flag == move.Flags.en_passent:
            self.move_piece_ep(start, end)

        elif p_move.flag == move.Flags.promotion:
            self.move_piece_promotion(start, end, p_move.promotion_piece)

        elif p_move.flag == move.Flags.castle:
            self.move_piece_castle(start, end)

        # map of the position the piece ends at
        end_piece_type = None
        for ind, bitmap in enumerate(self.positions[not self.colour]):
            if bitmap & end:
                end_piece_type = ind
                break

        if end_piece_type is not None:  # if we are taking another piece
            self.take_piece(end, end_piece_type)



        # update ep_map
        if self.ep_map:
            self.toggle_ep_zobrist(self.ep_map)
            self.ep_map = 0

        if start_piece_type == pieces.pawn:
            self.update_ep_map(start, end)

        # remove castle rights
        if start_piece_type == pieces.king:
            if self.right_castles[self.colour]:
                self.right_castles[self.colour] = False
                self.toggle_left_castle_zobrist(self.colour)
            if self.left_castles[self.colour]:
                self.left_castles[self.colour] = False
                self.toggle_right_castle_zobrist(self.colour)

        for alter in self.currently_altering:
            new_log.add_piece(*alter)

        self.logs.append(new_log)

        self.alter_zobrist_pieces()
        self.toggle_team_zobrist()

        self.currently_altering.clear()

        self.increment_game_state()
        self.update_team_positions()

        if end_piece_type is not None or start_piece_type == pieces.pawn:
            self.half_moves = 0

    def remove_single_castle(self, rook_position, colour):
        """
        removes a castling right when a rook is moved
        """
        if rook_position & left_starting_rooks[colour]:
            self.left_castles[colour] = False
            self.toggle_left_castle_zobrist(colour)
        elif rook_position & right_starting_rooks[colour]:
            self.right_castles[colour] = False
            self.toggle_right_castle_zobrist(colour)

    def move_piece_default(self, start, end, piece_type):
        '''
        moves the piece type from the start to end.
        NOTE team_peices must be a direct reference to the memory location of self.whites/blacks
        '''
        self.positions[self.colour][piece_type] ^= start | end

        altering = pieces.Piece(piece_type, self.colour)
        self.currently_altering.append((altering, start))
        self.currently_altering.append((altering, end))

        if piece_type == pieces.rook:
            self.remove_single_castle(start, self.colour)

    def move_piece_ep(self, start, end):
        '''
        does the same as move_piece_default but also removes an enpassent pawn behind the end position
        '''
        self.move_piece_default(start, end, pieces.pawn)
        if self.colour == pieces.white:
            ep_pos = end >> 8
        else:
            ep_pos = end << 8

        self.take_piece(ep_pos, pieces.pawn)


    def move_piece_promotion(self, start, end, promotion_piece_type):
        '''
            does the same as move_piece_default but places the promotion type piece onto the board
        '''
        self.positions[self.colour][pieces.pawn] ^= start
        self.positions[self.colour][promotion_piece_type] |= end

        # pawn's original position
        self.currently_altering.append((pieces.Piece(pieces.pawn, self.colour), start))
        # promotion new position
        self.currently_altering.append((pieces.Piece(promotion_piece_type, self.colour), end))

    def move_piece_castle(self, start, end):
        '''
        does the same as move_piece_default but also removes an enpassent pawn behind the end position
        NOTE this only needs a start and end position, as it assumes it is a king that has been moved
        '''
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

        self.move_piece_default(start, end, pieces.king)
        self.move_piece_default(rstart, rend, pieces.rook)

    def take_piece(self, position, piece_type):
        """
        the opposite of move_piece_default, takes a piece away from the
        """
        self.positions[not self.colour][piece_type] ^= position
        # castle rights removal
        if piece_type == pieces.rook:
            self.remove_single_castle(position, not self.colour)

        altering = pieces.Piece(piece_type, not self.colour)
        self.currently_altering.append((altering, position))

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


        # toggle this new ep_map into our zobrist hash
        self.toggle_ep_zobrist(self.ep_map)


    def unmake_move(self):
        self.past_moves.pop()
        log = self.logs.pop()
        log.replace(self)

    @classmethod
    def from_fen(cls, fen: str):
        """
        returns a fully initialized instance of a Board from a FEN string
        :param fen: FEN string of board to initialize
        :return: initialized Board
        """

        data = fen.split(" ")
        # add empty values into the data if we are given too few
        while len(data) < 6:
            data.append("-")

        layout, colour, castles, pawn_move, half_move, full_move = data

        # getting positions
        init_pieces = [0 for _ in range(12)]  # wp, wn, wb, wr etc...
        position = 1 << 63  # will be right shifted to access each position
        for char in layout:
            if char == "/":
                continue
            elif "0" < char <= "9":
                # skip forward n times
                position >>= int(char)
            else:
                # add the position to the respective piece
                piece_val = pieces.coloured_values[char]
                init_pieces[piece_val] |= position
                position >>= 1

        # colour
        init_colour = pieces.white if colour == "w" else pieces.black
        # castling rights
        wlc, wrc, blc, brc = "Q" in castles, "K" in castles, "q" in castles, "k" in castles
        # en passent bitmap
        ep = 0
        if pawn_move != "-":
            # last_move_end = column + 8 * row
            last_move_end = ((7 - move.column_letters.index(pawn_move[0])) + 8 * (int(pawn_move[1]) - 1))
            ep = bitset[last_move_end]

        # half and full move counts
        hm = 0
        if half_move != "-":
            hm = int(half_move)
        moves = init_colour
        if full_move != "-":
            moves = int(full_move)

        return cls(*init_pieces, ep, wlc, wrc, blc, brc, moves, hm, init_colour)


