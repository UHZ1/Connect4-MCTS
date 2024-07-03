from bitboard import bitboard
from bitmcts import task

def play():
  b = bitboard()
  while b.is_terminal() == -2:
    mv = int(input("Enter: "))
    b.move(mv)
    b.print()
    if b.is_terminal() != -2:
      break;
    print()
    mv = task(b, 3000, 150)
    b.move(mv)
    b.print()

  print("Winner: " + str(b.winner))
  return

play()
