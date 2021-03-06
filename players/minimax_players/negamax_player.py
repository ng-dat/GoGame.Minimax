import random

import sys
sys.path.append('../../')
from environment.go import GO, actions
from players.base_player import BasePlayer

NEGATIVE_INFI = -10000
POSITIVE_INFI = 10000

class NegamaxPlayer(BasePlayer):
    def __init__(self):
        super(NegamaxPlayer, self).__init__()
        self.type = 'Negamax'

        self.depth_limit = 3
        self.braching_factor_limit = 20

    def play(self, go_game: GO):
        temp_go = go_game.copy_game()
        _, best_move = self.negamax(temp_go, self.stone_type, self.depth_limit, NEGATIVE_INFI, POSITIVE_INFI)
        if best_move == 'PASS':
            return actions['PASS'], -1, -1
        else:
            return actions['PLACE'], best_move[0], best_move[1]

    def __evaluation_func(self, go_game:GO, stone_type):
        '''
            Evaluation func is used to score the resulted board when reaching limited depth of the search but the game has not ended.
            This needs to satisfy the characteristics of a Zero-Sum Game

            Here we use the reward function. That function will return 1 when the stone_type win, -1 when it is defeated and 0 when there is a tie
        :param go_game: current state of the game
        :return: the evaluation value.
        '''
        return go_game.get_reward(stone_type)

    def __reward_func(self, go_game: GO, stone_type):
        '''
            The reward function is used to score the result when the game ends.
            This needs to satisfy the characteristics of a Zero-Sum Game

            Here we use the reward function. That function will return 1 when the stone_type win, -1 when it is defeated and 0 when there is a tie
        :param go_game: current state of the game
        :return: the evaluation value.
        '''
        return go_game.get_reward(stone_type)

    def negamax(self, go, stone_type, depth, alpha, beta):
        if go.check_game_end(self.stone_type, actions['PLACE']):  # if limited num of moves reached
            reward = self.__reward_func(go, stone_type)
            return reward, "PASS"

        if depth < 1:  # if limited search depth reached
            heuristic_reward = self.__evaluation_func(go, stone_type)
            return heuristic_reward, "PASS"

        possible_placements = go.get_possible_placements(stone_type)
        if not possible_placements:
            return self.__evaluation_func(go, stone_type), "PASS"

        shuffled_move_indexes = [i for i in range(len(possible_placements))]
        random.shuffle(shuffled_move_indexes)
        shuffled_move_indexes = shuffled_move_indexes[:self.braching_factor_limit]

        best_value = NEGATIVE_INFI
        best_move = "PASS"
        cur_go = go.copy_game()

        for move_index in shuffled_move_indexes:
            move = possible_placements[move_index]

            cur_go.move_forward(actions['PLACE'], move, stone_type)
            next_piece_type = 3 - stone_type  # reverse turn
            value, _ = self.negamax(cur_go, next_piece_type, depth - 1, -1 * beta, -1 * max(alpha, best_value))
            value *= -1
            if value > best_value:
                best_value = value
                best_move = move
            cur_go = go.copy_game()
            if best_value >= beta:
                break

        # Return
        return best_value, best_move
