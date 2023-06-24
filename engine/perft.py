import time
import bitboard
import move_generator

fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
#fen = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - "
#fen = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - "
#fen = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"

gen_time = 0

board = bitboard.Board.from_fen(fen)
generator = move_generator.Generator(board)


def perft(search_depth, print_moves=True):
    global gen_time
    out = []
    t = time.time()
    move_list = generator.get_legal_moves()
    gen_time += time.time() - t
    n_moves = len(move_list)
    node_count = 0

    if search_depth == 1:
        return n_moves

    for move in move_list:
        board.make_move(move)
        count = perft(search_depth - 1, print_moves=False)
        node_count += count

        if print_moves:
            print(f"{move.notate()}: {count}")

        board.unmake_move()

    return node_count


print("searching")

t = time.perf_counter()

depth = 4
nodes = perft(depth)
elapsed = time.perf_counter() - t

print(f"finished in {elapsed:.2f}s")
print(f"{int(nodes / elapsed):,} n/s")
print("gen time", gen_time)
print(f"timer {generator.timer}")

print(f"{nodes:,} nodes")



# print("specific time", move_generator.total_time)
# print(f"portion {move_generator.total_time/gen_time*100:.1f}%")

