from bitboard import bitboard
<<<<<<< HEAD
from bitmcts import run
=======
from bitmcts import task
>>>>>>> d68bf81af0fb2160283db88499fb7e24309a8f0a


def bot_then_player():
  b = bitboard()
  while b.is_terminal() == -2:
    mv = run(b)
    b.move(mv)
    b.print()
    if b.is_terminal() != -2:
      break;
    mv = int(input("Enter: "))
    b.move(mv)
    b.print()

def player_then_bot():
  b = bitboard()
  while b.is_terminal() == -2:
    mv = int(input("Enter: "))
    b.move(mv)
    b.print()
    if b.is_terminal() != -2:
      break;
    mv = run(b)
    b.move(mv)
    b.print()

  print("Winner: " + str(b.winner))
  return

player_then_bot()
