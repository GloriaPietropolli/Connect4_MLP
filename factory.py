from neural_network import NeuralNetwork
from human import Human
from minimax import Minimax


def create(ai_name, player):
    if ai_name == 'minimax':
        return Minimax(player)

    if ai_name == 'neural_network':
        return NeuralNetwork(player)

    if ai_name == 'human':
        return Human(player)