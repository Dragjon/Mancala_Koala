from mancala import *

rootbestmove = 0

######################################################
#                   Original agent                   #
######################################################
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

######################################################
#                       Dev agent                    #
######################################################

def eval1(game):
    net_diff_seeds = 0
    for i in range(6):
        net_diff_seeds += game.board[i] - game.board[i+6]
    return 30 + 100*(game.houses[0] - game.houses[1]) + net_diff_seeds if game.turn == 0 \
      else 30 - 100*(game.houses[0] - game.houses[1]) - net_diff_seeds
    
def search1(game, depth, ply, alpha, beta):
    global rootbestmove
    max = -100000
    state = winner(game)
    if state == 0 or state == 1:
        return -30000
    
    if state == 2:
        return 0
    
    if depth <= 0:
        return eval1(game)

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
            score = search1(copygame2, depth - 1, ply + 1, alpha, beta)
            if score > max:
                max = score
                if ply == 0:
                    rootbestmove = move
                if score > alpha:
                    alpha = score
        else:
            score = -search1(copygame2, depth - 1, ply + 1, -beta, -alpha)
            if score > max:
                max = score
                if ply == 0:
                    rootbestmove = move
                if score > alpha:
                    alpha = score
                    if alpha >= beta:
                        break
            
    return max

def getBestMove1(game, depth):
    c_eval = search1(game, depth, 0, -100000, 100000)
    return [c_eval, rootbestmove]


'''
Testing framework
'''
import random

fp = open("openingsD7_111k.txt")
# Upper limit
n = 111434  
size = 10000 

# Ensure size <= n + 1
random_list = random.sample(range(0, n + 1), size)

print("Parsing opening strings...")

opening_strings = []

for i, line in enumerate(fp):
    if i in random_list:
        opening_strings.append(line)

fp.close()

print(len(opening_strings))

'''
Parsing opening strings
'''
def parseStr(opstr):
    game = Mancala()
    parts = opstr.split()
    game.turn = int(parts[0])
    game.board = [int(x) for x in parts[1].split("-")]
    game.houses = [int(x) for x in parts[2].split("+")]
    return game

openings = []
for op_string in opening_strings:
    openings.append(parseStr(op_string))

games_ran = 0
original_score = 0
dev_score = 0
draws = 0

def run_pair_match(game_o):
    global games_ran, original_score, dev_score, draws

    games_ran+=1

    print(f"Running game {games_ran}... ", end="")

    game = clone(game_o)

    while winner(game) == 3:
        if len(moveGen(game))==0:
            game.turn^=1
            continue
        
        if game.turn == 0:
            best = getBestMove(game, 5)
            game.move(best[1])
        else:
            best = getBestMove1(game, 5)
            game.move(best[1])
    
    if winner(game) == 0:
        original_score+=1
        print(f"{Colors.RED}Original Wins{Colors.END}!")
    elif winner(game) == 1:
        dev_score+=1
        print(f"{Colors.GREEN}Dev wins{Colors.END}!")
    else:
        draws+=1
        print(f"{Colors.DARK_GRAY}It's a draw{Colors.END}!")

    games_ran+=1

    print(f"Running game {games_ran}... ", end="")

    game = clone(game_o)

    while winner(game) == 3:
        if len(moveGen(game))==0:
            game.turn^=1
            continue
        
        if game.turn == 1:
            best = getBestMove(game, 5)
            game.move(best[1])
        else:
            best = getBestMove1(game, 5)
            game.move(best[1])

    if winner(game) == 1:
        original_score+=1
        print(f"{Colors.RED}Original Wins{Colors.END}!")
    elif winner(game) == 0:
        dev_score+=1
        print(f"{Colors.GREEN}Dev wins{Colors.END}!")
    else:
        draws+=1
        print(f"{Colors.DARK_GRAY}It's a draw{Colors.END}!")

import math

def elo_probabilities(elo, draw_ratio):
    """
    Given an Elo difference and draw ratio, returns win, draw, and loss probabilities.
    Assumes symmetric Elo model.
    """
    p_draw = draw_ratio
    p_win = (1 - p_draw) / (1 + 10 ** (-elo / 400))
    p_loss = 1 - p_win - p_draw
    return p_win, p_draw, p_loss

def compute_llr(w, d, l, elo0, elo1, draw_ratio):
    """
    Computes the Log-Likelihood Ratio (LLR) from win/draw/loss counts
    under two Elo hypotheses.
    """
    p0 = elo_probabilities(elo0, draw_ratio)
    p1 = elo_probabilities(elo1, draw_ratio)

    # Avoid log(0) with a small epsilon
    epsilon = 1e-15
    terms = [
        w * math.log((p1[0] + epsilon) / (p0[0] + epsilon)),
        d * math.log((p1[1] + epsilon) / (p0[1] + epsilon)),
        l * math.log((p1[2] + epsilon) / (p0[2] + epsilon))
    ]
    return sum(terms)

ub = 0
lb = 0

def sprt_result(w, d, l, elo0, elo1, alpha=0.05, beta=0.05, draw_ratio=0.5):
    global ub, lb
    """
    Returns SPRT result:
    - "accept H1" if LLR ≥ upper bound
    - "accept H0" if LLR ≤ lower bound
    - "continue" otherwise
    """
    llr = compute_llr(w, d, l, elo0, elo1, draw_ratio)

    lower_bound = math.log(beta / (1 - alpha))
    upper_bound = math.log((1 - beta) / alpha)

    ub = upper_bound
    lb = lower_bound

    if llr >= upper_bound:
        return ["accept H1", llr]
    elif llr <= lower_bound:
        return ["accept H0",llr]
    else:
        return ["continue", llr]

def run_tournament():
    i = 0
    for game in openings:
        i+=1
        run_pair_match(game)
        result_sprt = sprt_result(dev_score, draws, original_score, 0, 10, 0.05, 0.05, 0.5)
        if i != 0 and i % 20 == 0:
            print()
            print(f"Score Ratio: {Colors.RED}{original_score}{Colors.END}/{Colors.DARK_GRAY}{draws}{Colors.END}/{Colors.GREEN}{dev_score}{Colors.END} || LLR ({lb:.3f}, {ub:.3f}): {result_sprt[1]:.3f}")
            print()
        if  result_sprt[0] == "accept H1" or result_sprt[0] == "accept H0":
            break

    result_sprt = sprt_result(dev_score, draws, original_score, 0, 10, 0.05, 0.05, 0.5)
    print("----------------------------------")
    print(result_sprt[0])
    print(f"Total Games: {i*2}")
    print(f"Score Ratio: {Colors.RED}{original_score}{Colors.END}/{Colors.DARK_GRAY}{draws}{Colors.END}/{Colors.GREEN}{dev_score}{Colors.END}")
    print(f"LLR ({lb:.3f}, {ub:.3f}): {result_sprt[1]:.3f}")
    print("----------------------------------")
run_tournament()