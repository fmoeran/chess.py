1.                      2.
........   ....1...     ....q..b   ....1...
........   ....1...     ppp...Q.   ....1...
.k......   ....1...     nk......   ....1...
.b..R...   .111.111     .b..R...   .111.111
........   ....1...     ........   ....1...
....K...   ....1...     ....K...   ....1...
........   ........     .n.....p   ........
.n......   ........     ........   ........

........
....A...
....B...
....C...
.DEF.GH.
....I...
....J...
........

ABCDEFGH
I.......
........
........
........
....,...
........
........


........
........
........
........
........
........
.......A
BCDEFGHI

1.                      2.
........  00000000      ........  00000000
........  00000000      ........  00000000
.b......  00000000      .b......  01000000
........  00000000      ........  00100000
........  00000000      ........  00010000
....K...  00000000      ....K...  00000000
........  00000000      ........  00000000
..n.....  00000000      ........  00000000

3.                      4.
........  00000000      ........  11111111
........  00000000      ........  11111111
.b......  00000000      .b......  11111111
..P.....  00000000      ..P.....  11111111
........  00000000      ........  11111111
....K...  00000000      ....K...  11111111
........  00000000      ........  11111111
..n.....  00100000      ........  11111111


1.                      2.
........  00000000      ........  11111111
b.......  10000000      r.......  11111111
........  01000000      ........  11111111
..R.....  00000000      ..R.....  11111111
........  00010000      ........  11111111
....K...  00000000      ....K...  11111111
........  00000000      ........  11111111
........  00000000      ........  11111111

3.
........  00000000
b.......  10000000
........  01000000
..B.....  00000000
........  00010000
....K...  00000000
........  00000000
........  00000000


........   ........
..1.....   1.......
.1.1111.   1.......
..1.....   .111111.
..1.....   1.......
..1.....   1.......
..1.....   1.......
........   ........

1.                      2.
........  00001000      ....q...  00001000
b.......  00001000      bppp....  00001000
........  00001000      .....N..  00001000
.k..R...  01110111      .k..R...  01110111
........  00001000      ........  00001000
....K...  00001000      ....Kn..  00001000
........  00000000      ........  00000000
........  00000000      r.......  00000000



nzero = ~0
masks = [nzero for _ in range(64)]

bishop_pos = board.positions[not board.colour][pieces.bishop]
bishop_pos = board.positions[not board.colour][pieces.bishop]
queen_pos = board.positions[not board.colour][pieces.queen]

enemy_map = bishop_pos | queen_pos

# treat the king as if it is a bishop
bishop_pseudo = bishop_attack_lookups[king_pos][board.all]
# bishop_pseudo only holding team piece positions
team_bishop_pseudo = bishop_pseudo & board.team_maps[board.colour]
# used to iterate through the positions
position = bitset[63]
while position > 0:
    if position & team_bishop_pseudo:
        # get the pseudo moves but ignoring the position
        new_bishop_pseudo = bishop_attack_lookups[king_pos][magic_hash(board.all ^ position)]
        if new_bishop_pseudo & enemy_map & ~bishop_pseudo:
            int_pos = bitboard.get_single_position(position)
            position_pseudo = bishop_attack_lookups[int_pos][board.all]
            # update the mask
            masks[int_pos] &= position_pseudo & new_bishop_pseudo
    position >>= 1

def search(board):
    best_move = None
    best_score = NEGATIVE_INFINITY
    for move in get_legal_moves(board):
        board.make_move(move)
        if evaluate(board) > best_score:
            best_move = move
            best_score = score
        board.unmake_move()
    return best_move