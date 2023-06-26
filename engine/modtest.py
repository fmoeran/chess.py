import chess
import time

board = chess.Board()
#board.set_board_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w QKqk - 0 1")

gen_time = 0


def perft(search_depth, print_moves=True):
    global gen_time
    out = []
    t = time.time()
    move_list = board.generate_legal_moves()
    gen_time += time.time() - t
    node_count = 0

    if search_depth == 1:
        return sum(1 for _ in move_list)

    for move in move_list:
        board.push(move)
        count = perft(search_depth - 1, print_moves=False)
        node_count += count

        if print_moves:
            print(f"{move}: {count}")
        board.pop()

    return node_count

print("searching")

t = time.perf_counter()

depth = 5
nodes = perft(depth)
elapsed = time.perf_counter() - t

print(f"finished in {elapsed:.2f}s")
print(f"{int(nodes / elapsed):,} n/s")

print(f"{nodes:,} nodes")

