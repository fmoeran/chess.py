import engine

if __name__ == "__main__":
    engine.game.starting_fen = "8/k7/3p4/p2P1p2/P2P1P2/8/8/K7 w - - 0 1"
    bot = engine.search.Bot()
    game = engine.game.Game(black_is_ai=True, white_is_ai=False, debug=True)
    game.set_ai(bot.search)
    game.set_ai(bot.search, colour=engine.pieces.black)
    game.run()
