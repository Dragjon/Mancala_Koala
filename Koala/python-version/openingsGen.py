from mancala import *
def gen(game, depth):
    if depth == 0:
        print(str(game.turn) +" "+ '-'.join(str(x) for x in game.board) + " " + '+'.join(str(x) for x in game.houses))
        return
    for move in moveGen(game):
        new_game = clone(game)
        new_game.move(move)
        gen(new_game, depth - 1)

gen(Mancala(), 7)
