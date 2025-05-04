from engine import * 

############
# New game #
############
game = Mancala()
while winner(game) == 3:
    if len(moveGen(game))==0:
            game.turn^=1
            continue
    print()
    printBoard(game)
    if game.turn == 0:
        valid_moves = moveGen(game)
        move = int(input(f"Your move {valid_moves}: "))
        while move not in valid_moves:
            print("Invalid move. Try again.")
            move = int(input(f"Your move {valid_moves}: "))
        game.move(move)
    else:
        print("AI is thinking...")
        best = getBestMove(game, 10)
        print(f"AI chose move: {best[1]} || Score: {best[0]}")
        game.move(best[1])
        print(f"Static eval: {eval(game)}")

printBoard(game)
if winner(game) == 0:
    print("You win!")
elif winner(game) == 1:
    print("AI wins!")
else:
    print("It's a draw!")