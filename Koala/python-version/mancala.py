####################################################
# Koala - Open Source Framework for Mancala engine #
#                                       by Dragjon #
####################################################

import copy
import random
import math
import time  

class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"
    # cancel SGR codes if we don't write to a terminal
    if not __import__("sys").stdout.isatty():
        for _ in dir():
            if isinstance(_, str) and _[0] != "_":
                locals()[_] = ""
    else:
        # set Windows console in VT mode
        if __import__("platform").system() == "Windows":
            kernel32 = __import__("ctypes").windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            del kernel32

##############
# Game Rules #
##############

'''
Map of board to arrays

(house of player2) [4, 4, 4, 4, 4, 4,                4, 4, 4, 4, 4, 4] (house of 1st player)
Player starts here -->                                                  Opponent starts here -->
'''

class Mancala:
    def __init__(self):
        self.board = [4] * 12
        self.houses = [0, 0]
        self.turn = 0

    def move(self, idx):
        current_player = self.turn
        my_house = 6 if current_player == 0 else 0

        num_marbles = self.board[idx]
        if num_marbles == 0:
            return
        self.board[idx] = 0

        current_pos = (idx + 1) % 12
        last_pos = None

        house_visits = 0
        visited_house_last_turn = False

        for i in range(num_marbles):
            # Place marble in my house or current pit
            if current_pos == my_house and last_pos != my_house:
                self.houses[current_player] += 1
                last_pos = my_house
                house_visits+=1
                visited_house_last_turn = True
                continue
            elif (i <= num_marbles - house_visits + 1):
                self.board[current_pos] += 1
                last_pos = current_pos
                current_pos = (current_pos + 1) % 12
                visited_house_last_turn = False

        if last_pos == my_house and visited_house_last_turn:
            return  # Player gets another turn

        # Check for capture
        if (last_pos is not None and self.board[last_pos] == 1 and 
                last_pos // 6 == current_player):
            opposite_pos = 11 - last_pos
            self.houses[current_player] += self.board[opposite_pos] + 1
            self.board[last_pos] = 0
            self.board[opposite_pos] = 0

        self.turn ^= 1  # Switch turns

def printBoard(game):
        print("-----------------------------------------------------")
        print(f"Turn: {'Player 1' if game.turn == 0 else 'Player 2'}")
        print(f"             {' ' if (game.houses[1] > 9) else ''}", end="")
        for i in range(11, 5, -1):
            print(f"  {Colors.DARK_GRAY}{str(i).zfill(2)}{Colors.END}", end="")
        print()

        # Top row - Opponent's side
        print(f"             {' ' if game.houses[1]>9 else ''}{Colors.CYAN}+{Colors.END}", end="")
        for i in range(11, 5, -1):
            print(f"{str(game.board[i]):^3}", end=f"{Colors.CYAN}+{Colors.END}")
        print(f" {Colors.YELLOW}({game.houses[0]}) Player 1{Colors.END}")

        # Bottom row - Your side
        print(f"{Colors.CYAN}Player 2 ({game.houses[1]}){Colors.END} {Colors.YELLOW}+{Colors.END}", end="")
        for i in range(6):
            print(f"{str(game.board[i]):^3}", end=f"{Colors.YELLOW}+{Colors.END}")
        print()

        print(f"             {' ' if game.houses[1]>9 else ''}", end="")
        for i in range(6):
            print(f"  {Colors.DARK_GRAY}{str(i).zfill(2)}{Colors.END}", end="")
        print()
        print("-----------------------------------------------------")

def winner(game):
    if game.houses[0] > 24 and game.houses[1] < 25:
        return 0
    elif game.houses[0] < 25 and game.houses[1] > 24:
        return 1
    elif game.houses[0] == 24 and game.houses[1] == 24: 
        return 2
    return 3

def clone(game):
    game_new = Mancala()
    game_new.turn = game.turn
    game_new.board = game.board.copy()
    game_new.houses = game.houses.copy()
    return game_new

############
# Move Gen #
############
def moveGen(game):
    start = 0 if game.turn == 0 else 6
    return [start + i for i, count in enumerate(game.board[start:start+6]) if count != 0]

##############
# Perft Test #
##############

def perft(game, depth):
    """Calculate the number of nodes at a given depth for performance testing."""
    '''Does not consider "move skips" or terminal conditions'''
    if depth == 0:
        return 1
    nodes = 0
    for move in moveGen(game):
        new_game = clone(game)
        new_game.move(move)
        nodes += perft(new_game, depth - 1)
    return nodes

'''
Baseline
Depth 1: 6 nodes in 0.000s (0 nodes/s)
Depth 2: 35 nodes in 0.000s (0 nodes/s)
Depth 3: 185 nodes in 0.000s (0 nodes/s)
Depth 4: 948 nodes in 0.016s (61,035 nodes/s)
Depth 5: 4694 nodes in 0.016s (299,548 nodes/s)
Depth 6: 23281 nodes in 0.063s (372,326 nodes/s)
Depth 7: 114067 nodes in 0.301s (379,301 nodes/s)
Depth 8: 558242 nodes in 1.551s (359,990 nodes/s)
Depth 9: 2722223 nodes in 7.875s (345,670 nodes/s)
'''

def perf(max_depth):
    """Run perft tests for depths up to max_depth and print results."""
    for depth in range(1, max_depth + 1):
        game = Mancala()  # Start from the initial position for each depth
        start_time = time.time()
        node_count = perft(game, depth)
        elapsed = time.time() - start_time
        nps = node_count / elapsed if elapsed != 0 else 0
        print(f"Depth {depth}: {node_count} nodes in {elapsed:.3f}s ({nps:,.0f} nodes/s)")
