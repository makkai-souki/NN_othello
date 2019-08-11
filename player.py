from board import Board
import random


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
        # print("AI")
        # print(self.myplayer)
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
