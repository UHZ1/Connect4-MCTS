from board import Board
from mcts import run

def play(t):
  b = Board(t)
  while not b.checkWin() and not b.checkDraw():
    move = int(input("Enter: "))
    b.dropPiece(move)
    b.print()
    if b.checkWin() or b.checkDraw():
      break;

    move = run(b,  3000, 150)
    b.dropPiece(move)
    b.print()

  print("Winner: " + str((not b.turn)+1))
  return
