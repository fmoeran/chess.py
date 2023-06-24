import os

cd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cd)


from engine.game import Game
from engine.search import Bot
