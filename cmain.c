#include <stdio.h>

#include "cbitboard.h"
#include "cmcts.h"

int main()
{
  int mv;
  Board b;
  init_board(&b);
  move(&b, run(&b));
  return 0;
  while (is_terminal(&b) == 3)
  {
    move(&b, run(&b));
    print(&b);
    if (is_terminal(&b) != 3)
      break;
    scanf("%d", &mv);
    move(&b, mv);
    print(&b);
  }
}
