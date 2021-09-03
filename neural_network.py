import tensorflow.compat.v1 as tf
import numpy as np

tf.disable_v2_behavior()

from copy import deepcopy

board_width = 6  # 7
board_height = 7

learning_rate = 0.01

n_hidden_1 = 35
n_hidden_2 = 25
n_input = board_width * board_height * 3
n_classes = board_height  # board_width

board = tf.placeholder("float", [7, 6])
x_p1 = tf.cast(tf.equal(board, -1), "float")
x_p2 = tf.cast(tf.equal(board, 1), "float")
x_empty = tf.cast(tf.equal(board, 0), "float")
x = tf.reshape(tf.concat([x_p1, x_p2, x_empty], 0), [1, n_input])
rating = tf.placeholder("float", [7])  # 7
y = tf.reshape(rating, [1, n_classes])


def multilayer_network(x, weights, biases):
    layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
    layer_1 = tf.sigmoid(layer_1)

    layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
    layer_2 = tf.sigmoid(layer_2)

    out_layer = tf.matmul(layer_2, weights['out']) + biases['out']
    out_layer = tf.nn.softmax(out_layer)

    return out_layer


weights = {
    'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
    'out': tf.Variable(tf.random_normal([n_hidden_2, n_classes]))
}

biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}

predict = multilayer_network(x, weights, biases)

cost = tf.reduce_mean(tf.square(y - predict))

optimizer = tf.train.AdamOptimizer().minimize(cost)
saver = tf.train.Saver()


def print_weights(name):
    w = weights[name]
    init_op = tf.initialize_all_variables()
    with tf.Session() as sess:
        sess.run(init_op)
        # print(sess.run(a))
        np.savetxt(name + '.csv', sess.run(w))


class NeuralNetwork:

    def __init__(self, player):
        self.session = tf.Session()
        self.session.run(tf.initialize_all_variables())
        self.player = player
        self.saved_actions = []
        self.number_of_games = 0

    def __enter__(self):
        return self

    def next_move(self, game):
        predictions = self.session.run([predict], feed_dict={
            board: game.board,
        })
        legal_moves = game.get_legal_moves()

        score = 0
        column = -1
        for index, prediction in enumerate(predictions[0][0]):
            if prediction > score and legal_moves[index]:
                score = prediction
                column = index

        self.saved_actions.append({
            'board': deepcopy(game.board),
            'column': column,
        })

        return column

    def turn_feedback(self, player, column):
        pass

    def game_feedback(self, game, status, winner):
        self.number_of_games += 1

        if winner != 0:
            if winner == self.player:
                for action in self.saved_actions:
                    self.back_propagation(
                        action['board'], action['column'], 1)

        self.saved_actions = []

    def back_propagation(self, game_board, column, score):
        output_data = [0., 0., 0., 0., 0., 0., 0.]
        output_data[column] = score

        _, c = self.session.run([optimizer, cost], feed_dict={
            board: game_board,
            rating: output_data
        })

    def __exit__(self, type, value, traceback):
        self.session.close()
