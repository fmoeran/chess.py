from random import randint

max_size = 1 << 64


def random_map():
    return randint(0, max_size - 1)


def random_map_fewbits():
    return random_map() & random_map() & random_map()


def rmask(sq):
    result = 0
    rank, file = sq // 8, sq % 8
    for r in range(rank + 1, 7):  # go north to the edge of the board
        result |= 1 << (r * 8 + file)
    for r in range(rank - 1, 0, -1):  # go south to the edge
        result |= 1 << (r * 8 + file)
    for f in range(file + 1, 7):  # east to edge
        result |= 1 << (rank * 8 + f)
    for f in range(file - 1, 0, -1):  # east to edge
        result |= 1 << (rank * 8 + f)
    return result


def bmask(sq):
    result = 0
    rank, file = sq // 8, sq % 8

    r, f = rank + 1, file + 1
    while r < 7 and f < 7:  # north-east
        result |= 1 << (r * 8 + f)
        r, f = r + 1, f + 1

    r, f = rank + 1, file - 1
    while r < 7 and f > 0:  # north-west
        result |= 1 << (r * 8 + f)
        r, f = r + 1, f - 1

    r, f = rank - 1, file + 1
    while r > 0 and f < 7:  # south-east
        result |= 1 << (r * 8 + f)
        r, f = r - 1, f + 1

    r, f = rank - 1, file - 1
    while r > 0 and f > 0:  # south-west
        result |= 1 << (r * 8 + f)
        r, f = r - 1, f - 1

    return result



def ratt(sq, block_map):
    result = 0
    rank, file = sq // 8, sq % 8
    for r in range(rank + 1, 8):  # north
        pos = 1 << (r * 8 + file)
        result |= pos
        if block_map & pos:
            break

    for r in range(rank - 1, -1, -1):  # south
        pos = 1 << (r * 8 + file)
        result |= pos
        if block_map & pos:
            break

    for f in range(file + 1, 8):  # north
        pos = 1 << (rank * 8 + f)
        result |= pos
        if block_map & pos:
            break

    for f in range(file - 1, -1, -1):  # south
        pos = 1 << (rank * 8 + f)
        result |= pos
        if block_map & pos:
            break

    return result


def batt(sq, block_map):
    result = 0
    rank, file = sq // 8, sq % 8

    r, f = rank + 1, file + 1
    while r <= 7 and f <= 7:  # north-east
        pos = 1 << (r * 8 + f)
        result |= pos
        r, f = r + 1, f + 1
        if block_map & pos:
            break

    r, f = rank + 1, file - 1
    while r <= 7 and f >= 0:  # north-east
        pos = 1 << (r * 8 + f)
        result |= pos
        r, f = r + 1, f - 1
        if block_map & pos:
            break

    r, f = rank - 1, file + 1
    while r >= 0 and f <= 7:  # north-east
        pos = 1 << (r * 8 + f)
        result |= pos
        r, f = r - 1, f + 1
        if block_map & pos:
            break

    r, f = rank - 1, file - 1
    while r >= 0 and f >= 0:  # north-east
        pos = 1 << (r * 8 + f)
        result |= pos
        r, f = r - 1, f - 1
        if block_map & pos:
            break

    return result


def transform(board, magic_num, num_bits):
    buffer = (1 << num_bits) - 1
    #return (board * magic_num ^ (board >> 32) * (magic_num>>32) >> (32-num_bits)) & buffer
    return (board * magic_num) >> (64 - num_bits) & buffer




def map_index(index, mask):
    """
    returns an index for a specific mask in relation to a position's view.
    used for indexing every possible set of positions from the view of a square
    """
    # we do this by imagining we map every position of the index num (max 12 bits)
    # to the mask's bits and then return that mask

    result = 0
    while index:  # while we still have a bit left in our index
        # set the current mask to the next 1 bit of the mask
        current_mask_bitset = mask & (~mask+1)
        # if the last bit == 1, we should set our new mask's position to 1
        if index % 2 == 1:
            result |= current_mask_bitset
        # remove this bit from the mask, we have used it
        mask &= ~current_mask_bitset
        index >>= 1
    return result



# mask = rmask(35)
# for i in range(1 << 10):
#     bitboard.printmap(map_index(i, mask))
#     print()

def test_magic(magic, num_bits, blockers):
    # a register of which indexes we have used
    used = [False for _ in range(4096)]

    failed = False
    for i in range(1 << num_bits):
        magic_index = transform(blockers[i], magic, num_bits)
        if used[magic_index]:  # this specific magic has duplicates, AKA is not a perfect hash
            failed = True
            break
        else:
            used[magic_index] = True
    return not failed


def find_magic(sq, num_bits, is_bishop):
    """
    finds a suitable magic number for a certain square
    :param sq: square the piece is on
    :param num_bits: number of bits in the mask
    :param is_bishop: True for bishop, False for rook
    :return: magic number
    """

    # set up the mask for getting the seen pieces
    mask = bmask(sq) if is_bishop else rmask(sq)

    blockers = [0 for _ in range(1 << num_bits)]
    for i in range(1 << num_bits):
        blockers[i] = map_index(i, mask)

    for _ in range(10000000):
        # get a random magic number to test
        magic = random_map_fewbits()
        if test_magic(magic, num_bits, blockers):  # failed
            return magic
    print("***Failed***", sq)


# the number of bits in each position's view mask

r_bits = [
    12, 11, 11, 11, 11, 11, 11, 12,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    12, 11, 11, 11, 11, 11, 11, 12
]

b_bits = [
    6, 5, 5, 5, 5, 5, 5, 6,
    5, 5, 5, 5, 5, 5, 5, 5,
    5, 5, 7, 7, 7, 7, 5, 5,
    5, 5, 7, 9, 9, 7, 5, 5,
    5, 5, 7, 9, 9, 7, 5, 5,
    5, 5, 7, 7, 7, 7, 5, 5,
    5, 5, 5, 5, 5, 5, 5, 5,
    6, 5, 5, 5, 5, 5, 5, 6
]


def generate_rooks():
    with open("rooks_magics.txt", "w") as file:
        for square in range(64):
            # print(f"{hex(find_magic(square, r_bits[square], False))}")
            mag = hex(find_magic(square, r_bits[square], False))
            print(f"{square}/64 {mag}")
            file.write(f"{mag}\n")


def generate_bishops():
    with open("bishops_magics.txt", "w") as file:
        for square in range(64):
            # print(f"{hex(find_magic(square, r_bits[square], False))}")
            mag = hex(find_magic(square, b_bits[square], True))
            print(f"{square}/64 {mag}")
            file.write(f"{mag}\n")


def get_lookup(sq, mask, magic, num_bits, is_bishop):
    lookup_table = [0 for _ in range(4096)]
    for i in range(1 << num_bits):
        blocker_map = map_index(i, mask)
        attack_map = batt(sq, blocker_map) if is_bishop else ratt(sq, blocker_map)
        hash_index = transform(blocker_map, magic, num_bits)
        lookup_table[hash_index] = attack_map
    return lookup_table


def save_rook_lookups():
    # make lookup tables
    lookups = []
    with open("rooks_magics.txt", "r") as file:
        for sq, l in enumerate(file):
            magic_num = int(l.strip(), 16)
            new_lookup = get_lookup(sq, rmask(sq), magic_num, r_bits[sq], False)
            lookups.append(new_lookup)
    # save lookup tables
    with open("rook_lookups.txt", "w") as file:
        for lookup in lookups:
            line = " ".join(map(str, lookup))
            file.write(line + "\n")


def save_bishop_lookups():
    # make lookup tables
    lookups = []
    with open("bishops_magics.txt", "r") as file:
        for sq, l in enumerate(file):
            magic_num = int(l.strip(), 16)
            new_lookup = get_lookup(sq, bmask(sq), magic_num, b_bits[sq], True)
            lookups.append(new_lookup)
    # save lookup tables
    with open("bishop_lookups.txt", "w") as file:
        for lookup in lookups:
            line = " ".join(map(str, lookup))
            file.write(line + "\n")


class MagicLookup:

    def __init__(self, sq, magic_number, lookup_table, is_bishop):
        """

        :param sq: square
        :param magic_number: magic number for square in either rooks_magics or bishops_magics
        :param is_bishop: whether the piece is a bishop or a rook
        """
        self.sq = sq
        self.mask = bmask(sq) if is_bishop else rmask(sq)
        self.magic = magic_number
        self.num_bits = b_bits[sq] if is_bishop else r_bits[sq]
        self.is_bishop = is_bishop
        self.lookup_table = lookup_table

    def __getitem__(self, all_board):
        """
        returns a bitmap of all the positions that a piece can reach in a given bitboard.Board.all
        """
        blockers = self.mask & all_board
        ind = transform(blockers, self.magic, self.num_bits)
        return self.lookup_table[ind]


if __name__ == '__main__':
    #generate_rooks()
    #generate_bishops()
    #save_rook_lookups()
    #save_bishop_lookups()


    pass
