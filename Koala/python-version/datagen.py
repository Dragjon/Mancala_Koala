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

from itertools import islice

fp = open("openingsD7_111k.txt")
opening_strings = list(islice(fp, 50000))
fp.close()

print("Parsing opening strings...")

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

def gen_pos():

    print(f"{Colors.CYAN}Start data gen{Colors.END}")

    with open("datagen-50k.csv", "w") as f:
        f.write("pos,score\n")
        num_pos = 0
        all_game_positions = []
        all_end_score = []
        games_ran = 0

        for game_o in openings:
            game_positions = []
            games_ran+=1

            if games_ran % 50 == 0:
                print(f"Num pos: {Colors.LIGHT_PURPLE}{num_pos}{Colors.END} || Running game {Colors.GREEN}{games_ran}{Colors.END}... ")

            game = clone(game_o)

            while winner(game) == 3:
                game_positions.append(str(game.turn) +" "+ '-'.join(str(x) for x in game.board) + " " + '+'.join(str(x) for x in game.houses))
                if len(moveGen(game))==0:
                    game.turn^=1
                    continue

                best = getBestMove(game, 5)
                game.move(best[1])

            curr_winner = 1 if winner(game) == 0 else -1 if winner(game) == 1 else 0
            for pos in game_positions:
                num_pos+=1
                all_game_positions.append(pos)
                all_end_score.append(curr_winner)

        print()
        print("=============================")
        print(f"Total games    : {games_ran}")
        print(f"Total positions: {num_pos}")
        print("=============================")
        print()

        for i in range(len(all_game_positions)):
            f.write(f"{all_game_positions[i]},{all_end_score[i]}\n")


gen_pos()