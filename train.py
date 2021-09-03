from random import random
import sys

from neural_network import print_weights

from game import Game
from game import GAME_STATUS
from factory import create

verbose = False


def printv(to_print):
    if verbose:
        print(to_print)


def display_stats(game_statuses, p1_type, p2_type):
    total_games = game_statuses['draw'] + \
                  game_statuses['won_p1'] + game_statuses['won_p2']
    print('won games p1 (' + p1_type + '): ' + str(game_statuses['won_p1']) + ' / ' + str(
        total_games) + ' (' + str(game_statuses['won_p1'] * 100 / total_games) + '%)')
    print('won games p2 (' + p2_type + '): ' + str(game_statuses['won_p2']) + ' / ' + str(
        total_games) + ' (' + str(game_statuses['won_p2'] * 100 / total_games) + '%)')
    print('draw : ' + str(game_statuses['draw']) + ' / ' + str(
        total_games) + ' (' + str(game_statuses['draw'] * 100 / total_games) + '%)')


def handle_stats(game_statuses, batch_statuses, p1_type, p2_type):
    for key in batch_statuses:
        game_statuses[key] += batch_statuses[key]
    print('--- batch statistics ---')
    display_stats(batch_statuses, p1_type, p2_type)
    print('--- total statistics ---')
    display_stats(game_statuses, p1_type, p2_type)

    for key in batch_statuses:
        batch_statuses[key] = 0


def main(argv):
    first_player = -1
    second_player = 1

    p1_type = 'human'
    p2_type = 'neural_network'

    number_of_games = 1000
    randomness = 0.25
    board_width = 6  # 7
    board_height = 7

    game = Game(board_width, board_height)

    batch_statuses = {
        'draw': 0,
        'won_p1': 0,
        'won_p2': 0
    }

    game_statuses = {
        'draw': 0,
        'won_p1': 0,
        'won_p2': 0
    }

    batch_number = 1

    p1_ai = create(p1_type, first_player)
    p2_ai = create(p2_type, second_player)


    for game_number in range(number_of_games):
        status = game.get_status()

        while status == GAME_STATUS['PLAYING']:
            current_player = game.current_player
            current_ai = p1_ai if current_player == first_player \
                else p2_ai

            action = current_ai.next_move(game)

            if random() < randomness and current_player == first_player:
                printv('random triggered')
                action = game.random_action()

            game.play(action, current_player)

            status = game.get_status()

            p1_ai.turn_feedback(current_player, action)
            p2_ai.turn_feedback(current_player, action)

        p1_ai.game_feedback(game, status, game.winner)
        p2_ai.game_feedback(game, status, game.winner)

        print(game.board)
        # print_weights_biases(weights['h1'])

        if game.winner == first_player:
            batch_statuses['won_p1'] += 1
        elif game.winner == second_player:
            batch_statuses['won_p2'] += 1
        else:
            batch_statuses['draw'] += 1

        game.reset()
        if game_number > 1 and game_number % 100 == 0:
            print("### BATCH N " + str(batch_number) + " ###")
            batch_number += 1
            handle_stats(game_statuses, batch_statuses, p1_type, p2_type)

    print_weights('h1')
    print_weights('h2')
    print_weights('out')


if __name__ == "__main__":
    main(sys.argv[1:])