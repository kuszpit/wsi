#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <gsl/gsl_rng.h>
#include <gsl/gsl_randist.h>
#include <time.h>
#include <arpa/inet.h>

#include "./board.h"

#define MAX_DEPTH 10
#define SCORE 1000000

int evaluateBoard(int player) {
    int score = 50;
    //int opponent = 3 - player;

    if (winCheck(player)) return +SCORE;
    if (loseCheck(player)) return -SCORE;
    if (winCheck(3 - player)) return -SCORE;
    if (loseCheck(3 - player)) return +SCORE;


    return 0;
}

int isValidMove(int move) {
  int row = (move / 10) - 1;
  int col = (move % 10) - 1;
  if (row < 0 || row > 4 || col < 0 || col > 4) return false;
  return board[row][col] == 0;
}

int minimax(int depth, bool isMaximizing, int current_player, int bot_player) {
  int opponent = 3 - current_player;

  if (winCheck(1) || winCheck(2) || loseCheck(1) || loseCheck(2) || depth == 0)
    return evaluateBoard(bot_player);

  int best = isMaximizing ? -SCORE : SCORE;

  for (int row = 1; row <= 5; row++) {
    for (int col = 1; col <= 5; col++) {
      int pos = row * 10 + col;

      if (!isValidMove(pos)) continue;

      board[row - 1][col - 1] = current_player;
      int val = minimax(depth - 1, !isMaximizing, opponent, bot_player);
      board[row - 1][col - 1] = 0;
      
      if (isMaximizing) {
        if (val > best) best = val;
      } else {
        if (val < best) best = val;
      }
    }
  }

  return best;
}

int findBestMove(int player, int depth) {
  int bestVal = -SCORE;
  int bestMove = -1;

  for (int row = 1; row <= 5; row++) {
    for (int col = 1; col <= 5; col++) {
      int pos = row * 10 + col;
      if (!isValidMove(pos)) continue;

      board[row - 1][col - 1] = player;
      int moveVal = minimax(depth - 1, true, 3 - player, player);
      board[row - 1][col - 1] = 0;

      if (moveVal > bestVal) {
        bestVal = moveVal;
        bestMove = pos;
      }
    }
  }

  return bestMove;
}

int main(int argc, char *argv[]) {
  int server_socket;
  struct sockaddr_in server_addr;
  char server_message[16], player_message[16];

  bool end_game;
  int player, depth, msg, move;
  
  gsl_rng *generator = gsl_rng_alloc(gsl_rng_mt19937);
  gsl_rng_set(generator, time(NULL));

  if ( argc != 6 ) {
    printf("Wrong number of arguments. Usage: %s <ip> <port> <player_num> <player_name> <depth>\n", argv[0]);
    return -1;
  }

  // Create socket
  server_socket = socket(AF_INET, SOCK_STREAM, 0);
  if ( server_socket < 0 ) {
    printf("Unable to create socket\n");
    return -1;
  }
  printf("Socket created successfully\n");

  // Set port and IP the same as server-side
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(atoi(argv[2]));
  server_addr.sin_addr.s_addr = inet_addr(argv[1]);

  // Send connection request to server
  if ( connect(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0 ) {
    printf("Unable to connect\n");
    return -1;
  }
  printf("Connected with server successfully\n");

  // Receive the server message
  memset(server_message, '\0', sizeof(server_message));
  if ( recv(server_socket, server_message, sizeof(server_message), 0) < 0 ) {
    printf("Error while receiving server's message\n");
    return -1;
  }

  memset(player_message, '\0', sizeof(player_message));
  snprintf(player_message, sizeof(player_message), "%s %s", argv[3], argv[4]);
  // Send the message to server
  if ( send(server_socket, player_message, strlen(player_message), 0) < 0 ) {
    printf("Unable to send message\n");
    return -1;
  }

  setBoard();
  end_game = false;
  sscanf(argv[3], "%d", &player);
  sscanf(argv[5], "%d", &depth);

  while ( !end_game ) {
    memset(server_message, '\0', sizeof(server_message));
    if ( recv(server_socket, server_message, sizeof(server_message), 0) < 0 ) {
      printf("Error while receiving server's message\n");
      return -1;
    }
    sscanf(server_message, "%d", &msg);
    move = msg%100;
    msg = msg/100;
    if ( move != 0 ) {
      setMove(move, 3-player);
    }
    if ( (msg == 0) || (msg == 6) ) {
      move = findBestMove(player, depth);
      printf("Chosen move: %d\n", move);
      setMove(move, player);
      printBoard();

      memset(player_message, '\0', sizeof(player_message));
      snprintf(player_message, sizeof(player_message), "%d", move);

      if ( send(server_socket, player_message, strlen(player_message), 0) < 0 ) {
        printf("Unable to send message\n");
        return -1;
      }
     } else {
       end_game = true;
       switch ( msg ) {
         case 1 : printf("You won.\n"); break;
         case 2 : printf("You lost.\n"); break;
         case 3 : printf("Draw.\n"); break;
         case 4 : printf("You won. Opponent error.\n"); break;
         case 5 : printf("You lost. Your error.\n"); break;
      }
    }
  }

  // Close socket
  close(server_socket);

  return 0;
}
