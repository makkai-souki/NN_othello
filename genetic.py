from manager import GameManager
from operator import attrgetter
from player import AIwithNN
from player import RandomAI
import numpy as np
import random
from joblib import Parallel, delayed


class Genetic:
    def __init__(self):
        self.n_ind = 10  # 世代の個体数
        self.n_generation = 3  # 世代数
        self.indivisuals = []  # それぞれの個体
        self.i_mutation_rate = 0.1
        self.g_mutation_rate = 0.1
        self.now_gen = 0  # 現在の世代
        self.elite = Indivisual([])  # 最良の個体
        self.tornament_size = 5
        self.cxpb = 0.7
        self.make_first_generation()

    def make_first_generation(self):
        for i in range(self.n_ind):
            tmp_weight = [np.random.rand(6, 10), np.random.rand(10, 1)]
            self.indivisuals.append(Indivisual(tmp_weight))

    def evaluate_indivisuals(self):
        # Parallel(n_jobs=-1)([delayed(self.i_vs_j)(i)
                            #  for i in range(self.n_ind)])
        for i in range(self.n_ind):
            for j in range(i + 1, self.n_ind):
                tmp_game = GameManager()
                tmp_game.white_player = AIwithNN(self.indivisuals[i].weights)
                tmp_game.black_palyer = AIwithNN(self.indivisuals[j].weights)
                tmp_game.main_process()
                win_mode = tmp_game.finish_process()
                if win_mode == 1:
                    self.indivisuals[i].lose += 1
                    self.indivisuals[j].win += 1
                elif win_mode == -1:
                    self.indivisuals[i].win += 1
                    self.indivisuals[j].lose += 1
                else:
                    self.indivisuals[i].win += 0.5
                    self.indivisuals[j].win += 0.5
                    self.indivisuals[i].lose += 0.5
                    self.indivisuals[j].lose += 0.5
        for i in range(self.n_ind):
            self.indivisuals[i].calc_win_rate()
        self.indivisuals = sorted(
            self.indivisuals, key=attrgetter("win_rate"), reverse=True)
        self.elite = self.indivisuals[0]

    def i_vs_j(self, i):
        for j in range(i + 1, self.n_ind):
            tmp_game = GameManager()
            tmp_game.white_player = AIwithNN(self.indivisuals[i].weights)
            tmp_game.black_palyer = AIwithNN(self.indivisuals[j].weights)
            tmp_game.main_process()
            win_mode = tmp_game.finish_process()
            if win_mode == 1:
                self.indivisuals[i].lose += 1
                self.indivisuals[j].win += 1
            elif win_mode == -1:
                self.indivisuals[i].win += 1
                self.indivisuals[j].lose += 1
            else:
                self.indivisuals[i].win += 0.5
                self.indivisuals[j].win += 0.5
                self.indivisuals[i].lose += 0.5
                self.indivisuals[j].lose += 0.5

    def select_population(self):
        chosen = []
        for i in range(self.n_ind):
            aspirants = [random.choice(self.indivisuals)
                         for j in range(self.tornament_size)]
            chosen.append(max(aspirants, key=attrgetter("win_rate")))
        self.indivisuals = chosen

    def group_devide(self):
        return list(np.array_split(self.indivisuals, 2))

    def crossover_manager(self):
        indivisual_groups = self.group_devide()
        next_indivisuals = []
        for i in range(int(self.n_ind / 2)):
            if np.random.rand() < self.cxpb:
                next_indivisuals.extend(self.crossover(
                    indivisual_groups[0][i], indivisual_groups[1][i]))
            else:
                next_indivisuals.extend([
                    indivisual_groups[0][i], indivisual_groups[1][i]])
        self.indivisuals = next_indivisuals
        return next_indivisuals

    def crossover(self, a, b):
        reshapew1_a = np.reshape(a.weights[0], (60))
        reshapew2_a = np.reshape(a.weights[1], (10))
        reshapew1_b = np.reshape(b.weights[0], (60))
        reshapew2_b = np.reshape(b.weights[1], (10))
        tmpw1_a = reshapew1_a.copy()
        tmpw1_b = reshapew1_b.copy()
        tmpw2_a = reshapew2_a.copy()
        tmpw2_b = reshapew2_b.copy()
        w1len = len(tmpw1_a)
        w2len = len(tmpw2_a)
        w1cp1 = random.randint(1, w1len)
        w1cp2 = random.randint(1, w1len - 1)
        w2cp1 = random.randint(1, w2len)
        w2cp2 = random.randint(1, w2len - 1)
        if w1cp2 >= w1cp1:
            w1cp2 += 1
        else:
            w1cp1, w1cp2 = w1cp2, w1cp1
        if w2cp2 >= w2cp1:
            w2cp2 += 1
        else:
            w2cp1, w2cp2 = w2cp2, w2cp1
        tmpw1_a[w1cp1:w1cp2], tmpw1_b[w1cp1:w1cp2] = \
            tmpw1_b[w1cp1:w1cp2].copy(), tmpw1_a[w1cp1:w1cp2].copy()
        tmpw2_a[w2cp1:w2cp2], tmpw2_b[w2cp1:w2cp2] = \
            tmpw2_b[w2cp1:w2cp2].copy(), tmpw2_a[w2cp1:w2cp2].copy()
        a.weights[0] = np.reshape(tmpw1_a, (6, 10)).copy()
        a.weights[1] = np.reshape(tmpw2_a, (10, 1)).copy()
        b.weights[0] = np.reshape(tmpw1_b, (6, 10)).copy()
        b.weights[1] = np.reshape(tmpw2_b, (10, 1)).copy()
        return [a, b]

    def mutation_manager(self):
        for i in range(self.n_ind):
            if np.random.rand() < self.g_mutation_rate:
                self.indivisuals[i] = self.mutation(self.indivisuals[i])

    def mutation(self, a):
        weight1 = np.reshape(a.weights[0], (60))
        weight2 = np.reshape(a.weights[1], (10))
        for i in range(len(weight1)):
            if np.random.rand() < self.g_mutation_rate:
                weight1[i] = np.random.rand()
        for i in range(len(weight2)):
            if np.random.rand() < self.g_mutation_rate:
                weight2[i] = np.random.rand()
        weight1 = np.reshape(weight1, (6, 10))
        weight2 = np.reshape(weight2, (10, 1))
        result = Indivisual([weight1, weight2])
        return result

    def set_elite(self):
        self.indivisuals[0] = self.elite

    def output_data(self):
        w1_file = './data/elitew1_' + str(self.now_gen) + '.csv'
        w2_file = './data/elitew2_' + str(self.now_gen) + '.csv'
        analisis_file = './data/analisis.csv'
        np.savetxt(w1_file,
                   self.elite.weights[0], delimiter=',')
        np.savetxt(w2_file,
                   self.elite.weights[1], delimiter=',')
        test_rate = self.test_elite()
        with open(analisis_file, 'a') as f:
            print('{},{}'.format(self.now_gen, test_rate), file=f)

    def test_elite(self):
        r = Parallel(n_jobs=10)([delayed(self.vs_random)()
                                 for i in range(500)])
        return sum(r) / 500

    def vs_random(self):
        tmp_gm = GameManager()
        tmp_gm.white_player = RandomAI()
        tmp_gm.black_palyer = AIwithNN(self.elite.weights)
        tmp_gm.main_process()
        if tmp_gm.finish_process() == -1:
            return 1
        else:
            return 0

    def init_genelation(self):
        for i in range(self.n_ind):
            self.indivisuals[i].win = 0
            self.indivisuals[i].lose = 0
            self.indivisuals[i].win_rate = 0

    def genetic_manager(self, gen=10):
        for i in range(gen):
            print("generation:{}, evaluate start".format(i))
            self.evaluate_indivisuals()
            print(self.indivisuals)
            self.output_data()
            print("generation:{}, output_data".format(i))
            self.select_population()
            self.crossover_manager()
            self.mutation_manager()
            self.set_elite()
            if i == self.n_generation - 1:
                print("more genelation:")
                more_gen = int(input())
                if more_gen > 0:
                    self.genetic_manager(more_gen)


class Indivisual:
    def __init__(self, weights, win=0, lose=0, win_rate=0):
        self.weights = weights
        self.lose = lose
        self.win = win
        self.win_rate = win_rate

    def calc_win_rate(self):
        self.win_rate = self.win / (self.win + self.lose)

    def __repr__(self):
        return "win:{}".format(self.win_rate)


ga = Genetic()
ga.genetic_manager(ga.n_generation)
