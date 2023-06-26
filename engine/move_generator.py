from time import time

from engine import bitboard
from engine import move
from engine import pieces
from engine import magics


def map_to_moves(pos, map, tag=move.Flags.none, promotion_piece=0):
    """
    converts a bitmap of the positions a piece can go to into a set of moves
    """
    start_map = bitboard.bitset[pos]
    moves = []
    while map:
        # https://www.youtube.com/watch?v=ZRNO-ewsNcQ 4:33
        end_map = map & -map
        moves.append(move.Move(start_map, end_map, tag, promotion_piece))
        map = map & (map - 1)

    return moves


def generate_king_pseudo_moves():
    """
    generates a lookup table for the pseudo moveable positions of a king in that position
    """

    table = []
    for pos in range(64):
        row, col = pos // 8, 7 - pos % 8
        neighbours = []
        neighbour_map = 0
        if row > 0:
            neighbours.append(pos - 8)              # down
            if col > 0: neighbours.append(pos - 7)  # down & left
            if col < 7: neighbours.append(pos - 9)  # down & right
        if row < 7:
            neighbours.append(pos + 8)              # up
            if col > 0: neighbours.append(pos + 9)  # up & left
            if col < 7: neighbours.append(pos + 7)  # up & right
        if col > 0: neighbours.append(pos + 1)      # left
        if col < 7: neighbours.append(pos - 1)      # right

        for neighbour in neighbours:
            neighbour_map |= bitboard.bitset[neighbour]
        table.append(neighbour_map)
    return table


def generate_knight_pseudo_moves():
    table = []
    for pos in range(64):
        row, col = pos // 8, 7 - pos % 8
        neighbours = []
        neighbour_map = 0
        if row > 0:  # not on bottom row
            if col < 6:  # no right overflow
                neighbours.append(pos - 10)
            if col > 1:  # no left overflow
                neighbours.append(pos - 6)
        if row > 1:  # not second bottom row
            if col < 7:
                neighbours.append(pos - 17)
            if col > 0:
                neighbours.append(pos - 15)
        if row < 7:  # not on top row
            if col < 6:  # no right overflow
                neighbours.append(pos + 6)
            if col > 1:  # no left overflow
                neighbours.append(pos + 10)
        if row < 6:
            if col < 7:
                neighbours.append(pos + 15)
            if col > 0:
                neighbours.append(pos + 17)

        for neighbour in neighbours:
            neighbour_map |= bitboard.bitset[neighbour]
        table.append(neighbour_map)

    return table


def generate_pawn_push_pseudo_moves():
    white_table, black_table = [], []
    for pos in range(64):
        pos_map = bitboard.bitset[pos]
        white_table.append(pos_map << 8)
        black_table.append(pos_map >> 8)
    return white_table, black_table


def generate_pawn_attack_pseudo_moves():
    white_table, black_table = [], []
    for pos in range(64):
        col = 7 - pos % 8  # a = 0, h = 7
        pos_map = bitboard.bitset[pos]
        white_map, black_map = 0, 0
        if col != 7:  # not far right
            white_map |= pos_map << 7
            black_map |= pos_map >> 9
        if col != 0:  # not far left
            white_map |= pos_map << 9
            black_map |= pos_map >> 7
        white_table.append(white_map)
        black_table.append(black_map)

    return white_table, black_table


def generate_rook_attack_pseudo_moves():
    """
    creates a list for the 64 positions, each holding a magic.MagicLookup table
    """
    magic_nums = []
    with open("rooks_magics.txt", "r") as file:
        for line in file:
            magic_num = int(line.strip(), 16)
            magic_nums.append(magic_num)
    lookups = []
    with open("rook_lookups.txt", "r") as file:
        for line in file:
            lookup = list(map(int, line.strip().split()))
            lookups.append(lookup)
    tables = []
    for sq, (magic, lookup) in enumerate(zip(magic_nums, lookups)):
        tables.append(magics.MagicLookup(sq, magic, lookup, False))
    return tables


def generate_bishop_attack_pseudo_moves():
    """
    same as rook attack but for a bishop
    """
    magic_nums = []
    with open("bishops_magics.txt", "r") as file:
        for line in file:
            magic_num = int(line.strip(), 16)
            magic_nums.append(magic_num)
    lookups = []
    with open("bishop_lookups.txt", "r") as file:
        for line in file:
            lookup = list(map(int, line.strip().split()))
            lookups.append(lookup)
    tables = []
    for sq, (magic, lookup) in enumerate(zip(magic_nums, lookups)):
        tables.append(magics.MagicLookup(sq, magic, lookup, True))
    return tables


# pseudo move lookups
king_pseudo_lookup = generate_king_pseudo_moves()
knight_pseudo_lookup = generate_knight_pseudo_moves()

pawn_push_lookups = generate_pawn_push_pseudo_moves()
# the rows in front of the starting rows
#                           white       black
pawn_end_rows = (0xff << 48, 0xff << 8)
pawn_double_step_rows = (0xff << 16, 0xff << 40)
pawn_ep_rows = (0xff << 32, 0xff << 24)
pawn_step_sizes = (8, -8)  # only used when getting double steps

pawn_attack_lookups = generate_pawn_attack_pseudo_moves()

# NOTE this is why the startup is long
rook_attack_lookups = generate_rook_attack_pseudo_moves()

bishop_attack_lookups = generate_bishop_attack_pseudo_moves()

promotion_pieces = (pieces.knight, pieces.bishop, pieces.rook, pieces.queen)


class Generator:

    def pseudo_king(self, pos):  # NOQA
        return king_pseudo_lookup[pos]

    def pseudo_knight(self, pos):  # NOQA
        return knight_pseudo_lookup[pos]

    def pseudo_pawn(self, pos):

        nall = ~self.board.all
        forward_map = pawn_push_lookups[self.board.colour][pos]
        forward_map &= nall  # cannot be stepping on another piece

        if forward_map & pawn_double_step_rows[self.board.colour]:  # if we are able to double step

            forward_map |= pawn_push_lookups[self.board.colour][pos + pawn_step_sizes[self.board.colour]] & nall
        attack_map = pawn_attack_lookups[self.board.colour][pos] & self.board.all

        return forward_map | attack_map

    def pseudo_rook(self, pos):
        return rook_attack_lookups[pos][self.board.all]

    def pseudo_bishop(self, pos):
        return bishop_attack_lookups[pos][self.board.all]

    def pseudo_queen(self, pos):
        # just gets both bishop and rook
        return self.pseudo_rook(pos) | self.pseudo_bishop(pos)

    def __init__(self, board: bitboard.Board):
        '''
        a class for retrieving the possible moves at a position, etc...
        NOTE self.board is a reference to a board, so will change along with the board in game changeing
        '''
        self.not_team_map = None
        self.pin_masks = None
        self.check_mask = None
        self.attack_map = None
        self.board = board
        # the methods that should be called to get the pseudo legal moves for each piece type
        # this is only used in get_attack_map
        self.pseudo_methods = [self.pseudo_pawn, self.pseudo_knight, self.pseudo_bishop,
                               self.pseudo_rook, self.pseudo_queen, self.pseudo_king]

        self.timer = 0

    def get_attack_map(self):
        """
        sets self.attack_map to all the positions attacked by the opposition
        IMPORTANT it ignores the friendly king's position
        only used for king and castle moves
        :return:
        """
        temp_king = self.board.positions[self.board.colour][pieces.king]
        # we remove the king to allow for pinning a king to itself
        self.board.positions[self.board.colour][pieces.king] = 0
        # also have to remove it from the board.all
        self.board.all ^= temp_king


        result = 0
        for piece_type, position_maps in enumerate(self.board.positions[not self.board.colour]):
            for position in bitboard.iter_bitmap(position_maps):
                if piece_type == pieces.pawn:  # we want to deal only with their attacks, not pushes
                    continue
                result |= self.pseudo_methods[piece_type](position) # noqa

        # add pawns
        pawn_map = self.board.positions[not self.board.colour][pieces.pawn]
        for position in bitboard.iter_bitmap(pawn_map):
            result |= pawn_attack_lookups[1 - self.board.colour][position]

        self.board.all |= temp_king
        self.board.positions[self.board.colour][pieces.king] = temp_king

        return result

    def get_check_mask(self):
        king_map = self.board.positions[self.board.colour][pieces.king]
        king_pos = bitboard.bitset.index(king_map)

        result = ~0
        already_checked = False

        enemies = self.board.positions[not self.board.colour]

        # positions of every knight attacking the king
        knight_map = self.pseudo_knight(king_pos) & enemies[pieces.knight]
        num_knights = magics.count_1s(knight_map)
        if num_knights >= 2:  # being in check twice means there's no legal move apart from the king
            return 0
        elif num_knights == 1:
            result = knight_map
            already_checked = True

        # pawns
        pawn_map = pawn_attack_lookups[self.board.colour][king_pos] & enemies[pieces.pawn]
        num_pawns = magics.count_1s(pawn_map)
        if num_pawns >= 2 or (num_pawns == 1 and already_checked):
            return 0
        elif num_pawns == 1:
            already_checked = True
            result = pawn_map

        # rooks
        rook_map = self.pseudo_rook(king_pos) & (enemies[pieces.rook] | enemies[pieces.queen])
        num_rooks = magics.count_1s(rook_map)
        if num_rooks >= 2 or (num_rooks == 1 and already_checked):  # 2 or more checks
            return 0
        elif num_rooks == 1:
            already_checked = True
            if king_map > rook_map:  # rook to the right or below king
                if king_map >> 8 < rook_map:  # same row
                    result = ((king_map<<1) - 1) ^ (rook_map-1)
                else:
                    result = 0
                    pos = king_map
                    while pos != rook_map:
                        pos >>= 8
                        result |= pos
            else:  # rook on the left of above king
                if king_map << 8 > rook_map:  # same row
                    result = ((rook_map<<1) - 1) ^ ((king_map<<1) - 1)
                else:
                    result = 0
                    pos = king_map
                    while pos != rook_map:
                        pos <<= 8
                        result |= pos
        # bishops
        bishop_map = self.pseudo_bishop(king_pos) & (enemies[pieces.bishop] | enemies[pieces.queen])

        num_bishops = magics.count_1s(bishop_map)

        if num_bishops >= 2 or (num_bishops == 1 and already_checked):  # 2 or more checks

            return 0
        elif num_bishops == 1:
            already_checked = True
            bishop_pos = bitboard.bitset.index(bishop_map)
            br, bc = bishop_pos // 8, 7 - bishop_pos % 8  # A1 = 0, 0
            kr, kc = king_pos // 8, 7 - king_pos % 8
            if king_map > bishop_map:  # bishop is to the right of the king (below)
                result = 0
                dif = 9 if bc > kc else 7
                pos = king_map
                while pos != bishop_map:
                    pos >>= dif
                    result |= pos
            else:
                result = 0
                dif = 7 if bc > kc else 9
                pos = king_map
                while pos != bishop_map:
                    pos <<= dif
                    result |= pos

        return result

    def get_pin_masks(self, king_pos):
        nzero = ~0
        masks = [nzero for _ in range(64)]

        rook_pos = self.board.positions[not self.board.colour][pieces.rook]
        bishop_pos = self.board.positions[not self.board.colour][pieces.bishop]
        queen_pos = self.board.positions[not self.board.colour][pieces.queen]

        rook_pseudo = rook_attack_lookups[king_pos][self.board.all]
        team_rook_pseudo = rook_pseudo & self.board.team_maps[self.board.colour]
        team_rook_iterator = team_rook_pseudo  # we will be using this to iterate through the positions
        while team_rook_iterator:
            new_position = team_rook_iterator & -team_rook_iterator  # get the next position in team_rook_pseudo
            team_rook_iterator &= team_rook_iterator - 1  # iterate through team_rook_iterator
            # get the pseudo moves but ignoring the position
            new_rook_pseudo = rook_attack_lookups[king_pos][self.board.all ^ new_position]
            if new_rook_pseudo & (rook_pos | queen_pos) & ~rook_pseudo:
                new_pos = bitboard.get_single_position(new_position)
                new_position_pseudo = rook_attack_lookups[new_pos][self.board.all]
                masks[new_pos] &= new_position_pseudo & new_rook_pseudo

        # now the same for bishops

        bishop_pseudo = bishop_attack_lookups[king_pos][self.board.all]
        team_bishop_pseudo = bishop_pseudo & self.board.team_maps[self.board.colour]
        team_bishop_iterator = team_bishop_pseudo
        while team_bishop_iterator:
            new_position = team_bishop_iterator & -team_bishop_iterator  # get the next position in team_bishop_pseudo
            team_bishop_iterator &= team_bishop_iterator - 1  # iterate through team_rook_iterator
            # get the pseudo moves but ignoring the position
            new_bishop_pseudo = bishop_attack_lookups[king_pos][self.board.all ^ new_position]
            if new_bishop_pseudo & (bishop_pos | queen_pos) & ~bishop_pseudo:
                new_pos = bitboard.get_single_position(new_position)
                new_position_pseudo = bishop_attack_lookups[new_pos][self.board.all]
                masks[new_pos] &= new_position_pseudo & new_bishop_pseudo

        return masks

    def is_pinned(self, pos_map):
        king_pos = bitboard.get_single_position(self.board.positions[self.board.colour][pieces.king])
        rook_pos = self.board.positions[not self.board.colour][pieces.rook]
        bishop_pos = self.board.positions[not self.board.colour][pieces.bishop]
        queen_pos = self.board.positions[not self.board.colour][pieces.queen]

        rook_pseudo = rook_attack_lookups[king_pos][self.board.all]
        # pseudo moves without that position in place
        new_rook_pseudo = rook_attack_lookups[king_pos][self.board.all ^ pos_map]
        # the new pseudo contains rooks or queens and they are not already there
        if new_rook_pseudo & (rook_pos | queen_pos) & ~rook_pseudo:
            return True

        bishop_pseudo = bishop_attack_lookups[king_pos][self.board.all]
        # pseudo moves without that position in place
        new_bishop_pseudo = bishop_attack_lookups[king_pos][self.board.all ^ pos_map]
        # the new pseudo contains rbishop or queens and they are not already there
        if new_bishop_pseudo & (bishop_pos | queen_pos) & ~bishop_pseudo:
            return True

        return False

    def get_legal_pawn_moves(self):
        moves = []
        position_map = self.board.positions[self.board.colour][pieces.pawn]
        end_row = pawn_end_rows[self.board.colour]
        position_map &= ~end_row

        for position in bitboard.iter_bitmap(position_map):

            pin_mask = self.pin_masks[position]

            pseudo_moves = self.pseudo_pawn(position)

            legal_moves = pseudo_moves & self.check_mask & pin_mask & self.not_team_map
            moves.extend(map_to_moves(position, legal_moves))


        return moves

    def get_legal_knight_moves(self):
        moves = []
        position_map = self.board.positions[self.board.colour][pieces.knight]
        for position in bitboard.iter_bitmap(position_map):
            pin_mask = self.pin_masks[position]
            pseudo_moves = knight_pseudo_lookup[position]
            legal_moves = pseudo_moves & self.check_mask & pin_mask & self.not_team_map
            moves.extend(map_to_moves(position, legal_moves))
        return moves

    def get_legal_bishop_moves(self):
        moves = []
        position_map = self.board.positions[self.board.colour][pieces.bishop]
        for position in bitboard.iter_bitmap(position_map):
            pin_mask = self.pin_masks[position]
            pseudo_moves = self.pseudo_bishop(position)
            legal_moves = pseudo_moves & self.check_mask & pin_mask & self.not_team_map
            moves.extend(map_to_moves(position, legal_moves))
        return moves

    def get_legal_rook_moves(self):
        moves = []
        position_map = self.board.positions[self.board.colour][pieces.rook]
        for position in bitboard.iter_bitmap(position_map):
            pin_mask = self.pin_masks[position]
            pseudo_moves = self.pseudo_rook(position)
            legal_moves = pseudo_moves & self.check_mask & pin_mask & self.not_team_map
            moves.extend(map_to_moves(position, legal_moves))
        return moves

    def get_legal_queen_moves(self):
        moves = []
        position_map = self.board.positions[self.board.colour][pieces.queen]
        for position in bitboard.iter_bitmap(position_map):
            pin_mask = self.pin_masks[position]
            pseudo_moves = self.pseudo_queen(position)
            legal_moves = pseudo_moves & self.check_mask & pin_mask & self.not_team_map
            moves.extend(map_to_moves(position, legal_moves))
        return moves

    def get_castling_moves(self):
        result = []
        king_pos = self.board.positions[self.board.colour][pieces.king]
        other_positions = self.board.all & ~king_pos

        if self.board.right_castles[self.board.colour] is True:
            covered_positions = king_pos | king_pos >> 1 | king_pos >> 2
            if not (covered_positions & self.attack_map) and not (covered_positions & other_positions):
                result.extend(map_to_moves(bitboard.get_single_position(king_pos), king_pos >> 2, move.Flags.castle))
        if self.board.left_castles[self.board.colour] is True:
            covered_positions = king_pos | king_pos << 1 | king_pos << 2 | king_pos << 3
            no_attack_positions = king_pos | king_pos << 1 | king_pos << 2
            if not (no_attack_positions & self.attack_map) and not (covered_positions & other_positions):
                result.extend(map_to_moves(bitboard.get_single_position(king_pos), king_pos << 2, move.Flags.castle))
        return result

    def get_promotion_moves(self):
        moves = []
        end_row = pawn_end_rows[self.board.colour]
        position_map = self.board.positions[self.board.colour][pieces.pawn]
        position_map &= end_row
        for position in bitboard.iter_bitmap(position_map):
            pin_mask = self.pin_masks[position]
            pseudo_moves = self.pseudo_pawn(position)
            legal_moves = pseudo_moves & self.check_mask & pin_mask & self.not_team_map
            for piece in promotion_pieces:
                moves.extend(map_to_moves(position, legal_moves, tag=move.Flags.promotion, promotion_piece=piece))

        return moves

    def get_en_passent_moves(self):
        result = []
        if not self.board.ep_map:
            return result

        ep_map = self.board.ep_map
        if self.board.colour == pieces.white:
            attack_positions = ep_map >> 9 | ep_map >> 7
            pawn_position = ep_map >> 8
        else:
            attack_positions = ep_map << 9 | ep_map << 7
            pawn_position = ep_map << 8

        attack_positions &= pawn_ep_rows[self.board.colour]
        attack_positions &= self.board.positions[self.board.colour][pieces.pawn]
        if not attack_positions:
            return result

        # allow the ep position into the check mask IF the pawn being attacked is checking the king
        altered_check_mask = self.check_mask
        if pawn_position == altered_check_mask:
            altered_check_mask ^= ep_map
        while attack_positions:
            pos_map = attack_positions & -attack_positions
            attack_positions &= attack_positions - 1
            # check if taking pawn is pinned
            pin_mask = self.pin_masks[bitboard.get_single_position(pos_map)]

            # check if taken pawn is pinned
            self.board.all ^= pos_map
            pinned = self.is_pinned(pawn_position)
            self.board.all ^= pos_map

            # if the taken piece is pinned or if the move is just illegal anyway
            if pinned or not pin_mask & ep_map & altered_check_mask:
                continue

            pos = bitboard.get_single_position(pos_map)
            result.extend(map_to_moves(pos, ep_map, move.Flags.en_passent))

        return result

    def get_legal_king_moves(self):
        # position = next(iter(self.board.int_positions[self.board.colour][pieces.king]))
        position = bitboard.get_single_position(self.board.positions[self.board.colour][pieces.king])
        pseudo_legal = self.pseudo_king(position)
        legal_moves = pseudo_legal & ~self.attack_map & ~self.board.team_maps[self.board.colour]
        return map_to_moves(position, legal_moves)

    def get_legal_moves(self, only_captures=False) -> list[move.Move, ...]:
        """
        returns a list of legal moves from the current position
        """
        moves: list[move.Move, ...] = []

        if not self.board.positions[self.board.colour][pieces.king]:
            return moves
        t = time()
        self.attack_map = self.get_attack_map()

        king_pos = bitboard.bitset.index(self.board.positions[self.board.colour][pieces.king])

        self.check_mask = self.get_check_mask()

        self.pin_masks = self.get_pin_masks(king_pos)

        self.not_team_map = ~self.board.team_maps[self.board.colour]

        if only_captures:
            self.not_team_map = self.board.team_maps[not self.board.colour]

        moves.extend(self.get_legal_pawn_moves())

        moves.extend(self.get_legal_knight_moves())
        moves.extend(self.get_legal_bishop_moves())
        moves.extend(self.get_legal_rook_moves())
        moves.extend(self.get_legal_queen_moves())
        moves.extend(self.get_legal_king_moves())

        # special cases
        moves.extend(self.get_castling_moves())
        moves.extend(self.get_promotion_moves())
        moves.extend(self.get_en_passent_moves())
        self.timer += time() - t
        return moves
