# v0.1

from mancala import *

'''
"Tuned" Eval
'''
def eval(game):
    if game.turn == 0:
        net_diff_seeds = 0
        for i in range(6):
            net_diff_seeds += game.board[i] - game.board[i+6]
        return 30 + 100*(game.houses[0] - game.houses[1]) + net_diff_seeds
    
    net_diff_seeds = 0
    for i in range(6):
        net_diff_seeds += game.board[i+6] - game.board[i]
    return 30 + 100*(game.houses[1] - game.houses[0]) + net_diff_seeds

'''
Negamax function
'''
rootbestmove = 0

def search(game, depth, ply, alpha, beta):
    global rootbestmove
    max = -100000
    state = winner(game)
    if state == 0 or state == 1:
        return -30000
    
    if state == 2:
        return 0
    
    if depth <= 0:
        return eval(game)

    copygame = clone(game)
    movelist = moveGen(copygame)
    prevturn = copygame.turn
    
    # Deal with the pesky turn skip >:(
    if not movelist:
        copygame.turn ^= 1
        ply + 1
        movelist = moveGen(copygame)

    for move in movelist:
        copygame2 = clone(copygame)
        copygame2.move(move)
        # If we have another free turn
        if (copygame2.turn == prevturn):
            score = search(copygame2, depth - 1, ply + 1, alpha, beta)
            if score > max:
                max = score
                if ply == 0:
                    rootbestmove = move
                if score > alpha:
                    alpha = score
        else:
            score = -search(copygame2, depth - 1, ply + 1, -beta, -alpha)
            if score > max:
                max = score
                if ply == 0:
                    rootbestmove = move
                if score > alpha:
                    alpha = score
                    if alpha >= beta:
                        break
            
    return max

def getBestMove(game, depth):
    c_eval = search(game, depth, 0, -100000, 100000)
    return [c_eval, rootbestmove]