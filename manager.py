from board import Board
from player import Human
from player import RandomAI
from player import AIwithNN


class GameManager:
    def __init__(self):
        self.board = Board()
        self.white_player = AIwithNN()
        self.black_palyer = AIwithNN()

    def check_finish(self):   # 終了ならばTrue
        if self.board.stone_count(self.board.check_legal(True)) == 0 and \
           self.board.stone_count(self.board.check_legal(False)) == 0:
            # print(self.board.stone_count(self.board.check_legal(True)))
            return True
        else:
            return False

    def check_pass(self, p):
        if self.board.stone_count(self.board.check_legal(p)) == 0:
            return True
        else:
            return False

    def main_process(self):
        # self.board.print_board()
        while not self.check_finish():
            # print(self.board.player)
            if not self.check_pass(self.board.player):
                while not self.board_manager():
                    pass
            else:
                self.pass_process()
                # self.board.print_board()

    def pass_process(self):
        self.board.past_player.append(self.board.player)
        self.board.past_black.append(self.board.black)
        self.board.past_white.append(self.board.past_white)
        self.board.player = not self.board.player

    def finish_process(self):
        white_count = self.board.stone_count(self.board.white)
        black_count = self.board.stone_count(self.board.black)
        # self.board.print_board()
        if white_count < black_count:
            return -1
        elif black_count < white_count:
            return 1
        else:
            return 0

    def board_manager(self):  # プレイヤーがpos(int)に置く処理
        # print(self.board.player)
        if self.board.player:
            pos = self.white_player.AI(self.board.black,
                                       self.board.white,
                                       self.board.player)
        else:
            pos = self.black_palyer.AI(self.board.black,
                                       self.board.white,
                                       self.board.player)
        if pos == -1:
            # print("undo")
            self.board.undo_turn()
            return True
        pos_64bit = self.board.convert_input(pos)
        if (self.board.check_legal(self.board.player) & pos_64bit) != 0:
            self.board.reverse(self.board.player, pos_64bit)
            self.board.player = not self.board.player
            return True
        else:
            return False
