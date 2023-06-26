import engine

game = engine.Game(black_is_ai=True, white_is_ai=True)
bot = engine.Bot()

game.set_ai(bot.search, engine.pieces.black)
game.set_ai(bot.search, engine.pieces.white)

game.run()


print(engine.evaluate.timer)