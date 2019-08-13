from board import Board
# from manager import GameManager
import random
import numpy as np
import pandas as pd

evals = [
    [
        45.0, -11.0, 4.0, -1.0, -1.0, 4.0, -11.0, 45.0,
        -11.0, -16.0, -1.0, -3.0, -3.0, -1.0, -16.0, -11.0,
        4.0, -1.0, 2.0, -1.0, -1.0, 2.0, -1.0, 4.0,
        -1.0, -3.0, -1.0, 0.0, 0.0, -1.0, -3.0, -1.0,
        -1.0, -3.0, -1.0, 0.0, 0.0, -1.0, -3.0, -1.0,
        4.0, -1.0, 2.0, -1.0, -1.0, 2.0, -1.0, 4.0,
        -11.0, -16.0, -1.0, -3.0, -3.0, -1.0, -16.0,
        -11.0, 45.0, -11.0, 4.0, -1.0, -1.0, 4.0, -11.0, 45.0
    ],
    [
        30.0, -12.0, 0.0, -1.0, -1.0, 0.0, -12.0, 30.0,
        -12.0, -15.0, -3.0, -3.0, -3.0, -3.0, -15.0, -12.0,
        0.0, -3.0, 0.0, -1.0, -1.0, 0.0, -3.0, 0.0,
        -1.0, -3.0, -1.0, -1.0, -1.0, -1.0, -3.0, -1.0,
        -1.0, -3.0, -1.0, -1.0, -1.0, -1.0, -3.0, -1.0,
        0.0, -3.0, 0.0, -1.0, -1.0, 0.0, -3.0, 0.0,
        -12.0, -15.0, -3.0, -3.0, -3.0, -3.0, -15.0, -12.0,
        30.0, -12.0, 0.0, -1.0, -1.0, 0.0, -12.0, 30.0
    ]
]


class Human:
    def __init__(self):
        self.board = Board()

    def AI(self, black, white, player):
        i = list(map(int, input().split()))
        offset = 0
        result = 8 * (i[1] + offset) + (i[0] + offset)
        return result


class RandomAI:
    def __init__(self):
        self.board = Board()

    def AI(self, black, white, player):
        self.myplayer = player
        self.board.white = white
        self.board.black = black
        pos = self.convert_to_your_board(self.random_ai())
        return pos

    def convert_to_your_board(self, position):
        for i in range(64):
            if position & (1 << (63 - i)):
                return i
        return 0

    def random_ai(self):
        shuffle_positions = []
        shuffle_positions = self.get_reversible_positions()
        random.shuffle(shuffle_positions)
        return shuffle_positions[0]

    def get_reversible_positions(self):
        reversivle_positions = []
        tmp = self.board.check_legal(self.myplayer)
        count = 0
        while tmp != 0:
            if (tmp & 1) != 0:
                reversivle_positions.append(1 << count)
            tmp = tmp >> 1
            count += 1
            if tmp == 0:
                break
        return reversivle_positions


class NN:
    def __init__(self, weights):
        self.weights = weights

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def ReLU(self, x):
        return np.maximum(0, x)

    def forward(self, vector):
        layer1 = np.dot(vector, self.weights[0])
        layer2 = self.sigmoid(layer1)
        layer3 = np.dot(layer2, self.weights[1])
        return layer3[0]


class AIwithNN:
    def __init__(self):
        weights = []
        weights.append(np.random.rand(6, 10))
        weights.append(np.random.rand(10, 1))
        self.Nuro = NN(weights)
        self.board = Board()
        # self.gm = GameManager()

    def AI(self, black, white, player):
        self.myplayer = player
        self.board.black = black
        self.board.white = white
        tmp_reverse_pos = self.get_reversible_positions()
        output_scores = []
        for pos in tmp_reverse_pos:
            input_scores = self.make_input_vecotr(pos)
            tmp = self.Nuro.forward(input_scores)
            output_scores.append(tmp)
        max_key = np.argmax(output_scores)
        return_pos = self.convert_to_your_board(tmp_reverse_pos[max_key])
        return return_pos

    def get_reversible_positions(self):
        reversivle_positions = []
        tmp = self.board.check_legal(self.myplayer)
        count = 0
        while tmp != 0:
            if (tmp & 1) != 0:
                reversivle_positions.append(1 << count)
            tmp = tmp >> 1
            count += 1
            if tmp == 0:
                break
        return reversivle_positions

    def make_input_vecotr(self, position):
        vector = []
        self.board.reverse(self.myplayer, position)
        vector.append(self.get_corner_stone())
        vector.append(self.get_stone_diff(self.myplayer))
        vector.append(self.get_board_score())
        vector.append(self.get_board_score(1))
        vector.append(self.get_enemy_set(self.myplayer))
        vector.append(self.get_blank_stone())
        self.board.undo_turn()
        return np.array(vector)

    def get_corner_stone(self):
        corner = 0x8100000000000081
        black_corner = self.board.stone_count(self.board.black & corner)
        white_corner = self.board.stone_count(self.board.white & corner)
        if self.myplayer:
            return white_corner - black_corner
        else:
            return black_corner - white_corner

    def get_stone_diff(self, player):
        black_count = self.board.stone_count(self.board.black)
        white_count = self.board.stone_count(self.board.white)
        if player:
            return black_count - white_count
        else:
            return white_count - black_count

    def get_enemy_set(self, player):
        count = self.board.stone_count(self.board.check_legal(player))
        return count

    def get_blank_stone(self):
        blank = self.board.white | self.board.black
        return 64 - self.board.stone_count(blank)

    def get_board_score(self, id=0):
        white_score = 0
        black_score = 0
        for i in range(64):
            if self.board.is_stone(self.board.white, i):
                white_score += evals[id][i]
            if self.board.is_stone(self.board.black, i):
                black_score += evals[id][i]
        if self.myplayer:
            return white_score - black_score
        else:
            return black_score - white_score

    def convert_to_your_board(self, position):
        for i in range(64):
            if position & (1 << (63 - i)):
                return i
        return 0


# py = AIwithNN()
# position_aaaa = py.AI(0x0000000810000000, 0x0000001008000000, 0)
# print(position_aaaa)
# weights = []
# weights.append(np.random.rand(6, 10))
# weights.append(np.random.rand(10, 1))
# vect = np.array([[0, - 3, - 1, - 3,  3, 59]])
# nuro = NN(weights)
# nuro.forward(vect)
