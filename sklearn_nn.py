from drop7 import Game
import random
import numpy as np
#from sklearn.neural_network import MLPRegressor
from sknn.mlp import Regressor, Layer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
import logging

class Learner:
    def __init__(self, iterations=5):
        results = []
        situations = []
        logging.basicConfig()
        for i in range(0, iterations):
            g = Game(print_board=False)
            round_situations = []
            while not g.game_over:
                choices = g.available_cols()
                choice = random.choice(choices)
                round_situations.append(self.game_to_sit(g, choice))
                g.place_piece(choice)
            for situation in round_situations:
                results.append(g.points)
            situations.extend(round_situations)
        #self.pipeline = Pipeline([
        #    ('min/max scaler', MinMaxScaler(feature_range=(0.0, 1.0))),
        #    ('neural network', Regressor(
        self.nn = Regressor(layers=[
                    Layer("Rectifier", units=100),
                    Layer("Linear")],
                learning_rate=0.00002,
                n_iter=10)
        #self.pipeline.fit(np.array(situations), np.array(results))
        print np.array(situations).shape
        self.nn.fit(np.array(situations), np.array(results))
        #self.clf = MLPRegressor(algorithm='l-bfgs', alpha=1e-5,
        #                         hidden_layer_sizes=(5, 2), random_state=1)
        #clf.train(situations, results)

    def game_to_sit(self, game, choice):
        sit = [float(item) / 9 for sublist in game.board for item in sublist]
        sit.append(float(choice) / 7)
        sit.append(float(game.level) / 100)
        assert(float(game.level) / 100)
        sit.append(float(game.pieces_left) / 30)
        return sit
    
    def pick_move(self, game):
        choices = game.available_cols()
        max_choice, max_val = None, 0
        for c in choices:
            sit = np.array([self.game_to_sit(game, c)])
            final_score_predict = self.nn.predict(sit)
            if final_score_predict > max_val:
                max_val = final_score_predict
                max_choice = c
        return max_choice
        
if __name__ == "__main__":
    l = Learner(100)
    g = Game(sleep=True)
    while not g.game_over:
        move = l.pick_move(g)
        g.place_piece(move)
        #choices = g.available_cols()
        #break
