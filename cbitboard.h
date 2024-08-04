#pragma once

#include <stdint.h>

#define PL0WIN 0
#define PL1WIN 1
#define INPLAY 2
#define TIE 3
#define PLCNT 2
#define ROWS 6
#define COLS 7
#define BSIZE 42

typedef uint_fast8_t  u8;
typedef int_fast8_t   s8;
typedef uint_fast32_t u32;
typedef uint_fast64_t u64;

typedef struct Board
{
  u8 player;
  u8 winner; // 0->0won, 1->1won, 2->tie, 3->going on
  u64 s0, s1;
  u8 heights[COLS];
  u64 boards[PLCNT];
} Board;

void init_board(Board *b);
void move(Board *b, u8 col);
void undo_move(Board *b, u8 col);
u32 legal_moves(Board *b);
u32 get_move(Board *b);
s8 is_terminal(Board *b);
s8 swap_is_terminal(Board *b, u8 col);
void print(Board *b);
