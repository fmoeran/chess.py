import os

cd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cd)


from engine import game
from engine import search
from engine import pieces
from engine import bitboard
from engine import move
