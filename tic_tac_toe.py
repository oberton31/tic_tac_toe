import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random


'''
Tic Tac Toe Board:
0 1 2
3 4 5
6 7 8
'''
class TicTacToe(gym.Env):
    metadata = {"render_modes": ["human"]}
    def __init__(self, render_mode = None):

        self.observation_space = spaces.Box(low=0, high=2, shape=(3,3), dtype=np.int32)
        self.action_space = spaces.Discrete(9)
        
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.current_player = 1 # human player
        self._outcome = 0 # 0 for no winner, 1 for player 1 wins, 2 for player 2, and 3 for draw

    
    def reset(self):

        self.current_player = random.randint(1, 2)
        if self.render_mode == "human":
            self._render_frame()
        return self._board, None # No extra info to return
    
    def play_human_move(self):

        while True:
            try:
                move = int(input("Enter your move (0-8): "))
                if 0 <= move < 9 and self._board[move] == 0:
                    return move
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Enter a number between 0 and 8.")
        


    def check_game_over(self):
        for i in range(3):
            if self._board[i][0] == self._board[i][1] == self._board[i][2] != 0:
                self._outcome == self._board[i][0]
                return True  # Row win
            if self._board[0][i] == self._board[1][i] == self._board[2][i] != 0:
                self._outcome = self._board[0][i]
                return True  # Column win

        if self._board[0][0] == self._board[1][1] == self._board[2][2] != 0:
            self._outcome = self._board[0][0]
            return True  # Diagonal win
        if self._board[0][2] == self._board[1][1] == self._board[2][0] != 0:
            self._outcome = self._board[0][2]
            return True  # Anti-diagonal win

        # Check if the board is full (draw)
        for row in self._board:
            if 0 in row:
                return False  # Game is still ongoing
        self._outcome = 3
        return True  # Draw (no winner)

    def step(self, action):
        self.board[action] = self.current_player
        done = self.check_game_over()
        self.current_player = 3 - self.current_player # Toggle between 1 and 2
        reward = 0
        if done:
            if self._outcome == 3:
                reward = -1
            elif self._outcome == 2:
                reward = 5
            elif self._outcome == 1:
                reward = -5
        
        if self.render_mode == "human":
            self._render_frame()
        return self._board, reward, done, False, None
    
    def _render_frame(self):
        print("Current Board:")
        print(self._board)
    
