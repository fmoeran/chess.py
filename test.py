import engine

engine.game.starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w QKqk - 0 1"
game = engine.game.Game(black_is_ai=True, white_is_ai=False, debug=True)
bot = engine.search.Bot()

game.set_ai(bot.search, engine.pieces.black)
game.set_ai(bot.search, engine.pieces.white)

game.run()
