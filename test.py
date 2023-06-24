import engine

game = engine.Game(black_is_ai=True)
bot = engine.Bot()

game.set_ai(bot.search, 1)

game.run()


