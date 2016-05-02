from __future__ import print_function
from neat import nn, population, visualize
from drop7 import Game
import numpy as np
import random, pickle
from multiprocessing import Pool


class Learner:
    def __init__(self):
        #config = Config('drop7_config')
        pop = population.Population('drop7_config')
        pop.run(self.eval_fitness, 100)

        print('Number of evaluations: {0}'.format(pop.total_evaluations))

        # Display the most fit genome.
        self.winner = pop.statistics.best_genome()
        print('\nBest genome:\n{!s}'.format(self.winner))

        # Verify network output against training data.
        #print('\nOutput:')
        self.winner_net = nn.create_feed_forward_phenotype(self.winner)
        #for inputs, expected in zip(xor_inputs, xor_outputs):
        #        output = winner_net.serial_activate(inputs)
        #            print("expected {0:1.5f} got {1:1.5f}".format(expected, output[0]))

        visualize.plot_stats(pop.statistics)
        visualize.plot_species(pop.statistics)
        visualize.draw_net(self.winner, view=True, filename="drop7-all.gv")
        visualize.draw_net(self.winner, view=True, filename="drop7-enabled.gv", show_disabled=False)
        visualize.draw_net(self.winner, view=True, filename="drop7-enabled-pruned.gv", show_disabled=False, prune_unused=True)

    def make_move(self, game):
        moves = self.winner_net.serial_activate(game_to_sit(game))
        moves_tuples = zip(moves, range(len(moves)))
        moves_tuples.sort()
        for move in moves_tuples:
            if game.place_piece(move[1]):
                break
        
    def eval_fitness(self, genomes):
        for gen in genomes:
            net = nn.create_feed_forward_phenotype(gen)
            #scores = np.zeros(5, dtype=np.int)
            p = Pool(4)
            scores = p.map(simulate_game, [(net, False)] * 4)
            p.close()
            #for i in range(4):
                
                #if not game.place_piece(move):
                    #print("Tried to make illegal move :(")
                #    break
            gen.fitness = np.median(np.array(scores))
            
            #sum_square_error = 0.0
            #for inputs, expected in zip(xor_inputs, xor_outputs):
                # Serial activation propagates the inputs through the entire network.
                #output = net.serial_activate(inputs)
                #sum_square_error += (output[0] - expected) ** 2
                
                # When the output matches expected for all inputs, fitness will reach
                # its maximum value of 1.0.
                #g.fitness = 1 - sum_square_error

def simulate_game(tup):
    net, classic_mode = tup
    game = Game(print_board=False, sleep=False, classic_mode=classic_mode)
    while not game.game_over:
        moves = net.serial_activate(game_to_sit(game))
        #move = moves.index(max(moves))
        moves_tuples = zip(moves, range(len(moves)))
        moves_tuples.sort()
        for move in moves_tuples:
            if game.place_piece(move[1]):
                break
    return game.points
        
def game_to_sit(game):
    # 10 * 49 + 3 means 493 input nodes
    sit = []
    for row in game.board:
        for col in row:
            for i in range(col):
                sit.append(0)
            sit.append(1)
            for i in range(9 - col):
                sit.append(0)
    #sit = [item for sublist in game.board for item in sublist]
    sit.append(game.level)
    sit.append(game.pieces_left)
    sit.append(game.current_piece)
    return sit



def naive_scores(iterations):
    scores = []
    for i in range(iterations):
        g = Game(print_board=False, classic_mode=False)
        while not g.game_over:
            choices = g.available_cols()
            choice = random.choice(choices)
            g.place_piece(choice)
        scores.append(g.points)
    return max(scores), sum(scores)/len(scores)

if __name__ == "__main__":
    #print(naive_scores(100))
    l = Learner()
    output = open('learner2.pkl', 'wb')
    pickle.dump(l, output)
    output.close()

    #pkl_file = open('learner2.pkl', 'rb')
    #learner = pickle.load(pkl_file)
    #pkl_file.close()
    #simulate_game((learner.winner_net, False))
