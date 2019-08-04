H_MASK = 0x7e7e7e7e7e7e7e7e   # 端の一列が空白のもの
V_MASK = 0x00FFFFFFFFFFFF00   # 上下の一行が空白のもの
A_MASK = 0x007e7e7e7e7e7e00   # 一番外側の一周が空白のもの


class Board:
    def __init__(self):
        self.black = 0x0000000810000000  # 黒の初期配置
        self.white = 0x0000001008000000  # 白の初期配置
        self.turn = 1  # 現在のターン数
        self.player = False  # 石を置く色
        # self.setpositions = []  # 置いた場所のリスト
        # self.reversed = []  # 返した場所のリスト
        self.past_black = []  # 黒の過去の状態
        self.past_white = []  # 白の過去の状態
        self.past_player = []  # 過去に打ったplayerを保持

    def print_board(self):
        for i in range(64):
            if self.is_stone(self.white, i) or self.is_stone(self.black, i):
                if self.is_stone(self.white, i):
                    print("●", end="")
                if self.is_stone(self.black, i):
                    print("○", end="")
            else:
                print("×", end="")
            if i % 8 == 7:
                print("")
        print("")

    def is_stone(self, bitboard, position):
        return bitboard >> (63 - position) & 1

    def print_board_virtual(self, bitboard):
        for i in range(64):
            if self.is_stone(bitboard, i):
                print("○", end="")
            else:
                print("×", end="")
            if i % 8 == 7:
                print("")

    def convert_input(self, position):
        result = 0x0000000000000001
        result = result << (63 - position)
        return result

    # 着手可能位置を返す関数
    def check_legal(self, p):
        if p:
            offence = self.white
            diffence = self.black
        else:
            offence = self.black
            diffence = self.white
        blank = ~(offence | diffence)
        h_watcher = diffence & H_MASK
        v_watcher = diffence & V_MASK
        a_watcher = diffence & A_MASK

    # 左右
        tmp = h_watcher & (offence << 1)
        tmp |= h_watcher & (tmp << 1)
        tmp |= h_watcher & (tmp << 1)
        tmp |= h_watcher & (tmp << 1)
        tmp |= h_watcher & (tmp << 1)
        tmp |= h_watcher & (tmp << 1)
        legal_board = blank & (tmp << 1)

        tmp = h_watcher & (offence >> 1)
        tmp |= h_watcher & (tmp >> 1)
        tmp |= h_watcher & (tmp >> 1)
        tmp |= h_watcher & (tmp >> 1)
        tmp |= h_watcher & (tmp >> 1)
        tmp |= h_watcher & (tmp >> 1)
        legal_board |= blank & (tmp >> 1)

        # 上下
        tmp = v_watcher & (offence << 8)
        tmp |= v_watcher & (tmp << 8)
        tmp |= v_watcher & (tmp << 8)
        tmp |= v_watcher & (tmp << 8)
        tmp |= v_watcher & (tmp << 8)
        tmp |= v_watcher & (tmp << 8)
        legal_board |= blank & (tmp << 8)

        tmp = v_watcher & (offence >> 8)
        tmp |= v_watcher & (tmp >> 8)
        tmp |= v_watcher & (tmp >> 8)
        tmp |= v_watcher & (tmp >> 8)
        tmp |= v_watcher & (tmp >> 8)
        tmp |= v_watcher & (tmp >> 8)
        legal_board |= blank & (tmp >> 8)

        # 斜め
        tmp = a_watcher & (offence >> 9)
        tmp |= a_watcher & (tmp >> 9)
        tmp |= a_watcher & (tmp >> 9)
        tmp |= a_watcher & (tmp >> 9)
        tmp |= a_watcher & (tmp >> 9)
        tmp |= a_watcher & (tmp >> 9)
        legal_board |= blank & (tmp >> 9)

        tmp = a_watcher & (offence << 9)
        tmp |= a_watcher & (tmp << 9)
        tmp |= a_watcher & (tmp << 9)
        tmp |= a_watcher & (tmp << 9)
        tmp |= a_watcher & (tmp << 9)
        tmp |= a_watcher & (tmp << 9)
        legal_board |= blank & (tmp << 9)

        tmp = a_watcher & (offence >> 7)
        tmp |= a_watcher & (tmp >> 7)
        tmp |= a_watcher & (tmp >> 7)
        tmp |= a_watcher & (tmp >> 7)
        tmp |= a_watcher & (tmp >> 7)
        tmp |= a_watcher & (tmp >> 7)
        legal_board |= blank & (tmp >> 7)

        tmp = a_watcher & (offence << 7)
        tmp |= a_watcher & (tmp << 7)
        tmp |= a_watcher & (tmp << 7)
        tmp |= a_watcher & (tmp << 7)
        tmp |= a_watcher & (tmp << 7)
        tmp |= a_watcher & (tmp << 7)
        legal_board |= blank & (tmp << 7)

        return legal_board

    def transfer(self, position, i):
        if i == 0:
            return (position << 8) & 0xffffffffffffff00
        elif i == 1:
            return (position << 7) & 0x7f7f7f7f7f7f7f00
        elif i == 2:
            return (position >> 1) & 0x7f7f7f7f7f7f7f7f
        elif i == 3:
            return (position >> 9) & 0x007f7f7f7f7f7f7f
        elif i == 4:
            return (position >> 8) & 0x00ffffffffffffff
        elif i == 5:
            return (position >> 7) & 0x00fefefefefefefe
        elif i == 6:
            return (position << 1) & 0xfefefefefefefefe
        elif i == 7:
            return (position << 9) & 0xfefefefefefefe00
        else:
            return 0

    def reverse(self, p, position):
        self.past_black.append(self.black)
        self.past_white.append(self.white)
        self.past_player.append(p)
        if p:
            offence = self.white
            diffence = self.black
        else:
            offence = self.black
            diffence = self.white
        rev = 0
        self.setpositions.append(position)
        for i in range(8):
            mask = self.transfer(position, i)
            rev_tmp = 0
            while (mask != 0) and ((mask & diffence) != 0):
                rev_tmp |= mask
                mask = self.transfer(mask, i)
                if (mask & offence) != 0:
                    rev |= rev_tmp
        offence ^= position | rev
        diffence ^= rev
        if p:
            self.white = offence
            self.black = diffence
        else:
            self.white = diffence
            self.black = diffence

    def stone_count(self, bitboard):
        return bin(bitboard).count("1")

    def undo_turn(self):
        self.white = self.past_white.pop(-1)
        self.black = self.past_black.pop(-1)
        self.player = self.past_player.pop(-1)
