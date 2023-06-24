from engine.game import Game
from engine import search

bot = search.Bot()



if __name__ == "__main__":
    game = Game(debug=True, black_is_ai=True, white_is_ai=False)
    game.set_ai(bot.search)
    game.set_ai(bot.search, colour=0)
    print(game.run(show_fps=True))
