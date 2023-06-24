from game import Game
import search

bot = search.search


if __name__ == "__main__":
    game = Game(debug=True, black_is_ai=True, white_is_ai=False)
    game.set_ai(bot)
    game.set_ai(bot, colour=0)
    print(game.run(show_fps=True))
