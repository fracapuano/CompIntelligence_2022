from lab_utils.nim import *
import random
from tqdm import tqdm

class NimAI():

    def __init__(self, learning_rate = 0.5, eps = 0.2):
        """
            Initialise an empty dictionary, which will map each action to the corresponding Q-value.
            Defined as a tuple of Nim games, each action makes the game evolve from the first Nim game to the second..
        Args:
            learning_rate (float): learning rate. Defaults to 0.5.
            eps (float): probability of exploitation. Defaults to 0.2.
        """

        self.q = dict()
        self.learning_rate = learning_rate
        self.eps = eps

    def update(self, old_state, new_state, reward, next_action = None):
        """
            Update model. Given the current state and the previous state,
            it finds which is the next-step best action to do and updates the Q-value of the tuple (`old state`, `new state`).

        Args:
            old_state (Nim): previously observed state.
            new_state (Nim): resulting state.
            reward (float): reward when performing `action` in `old_state`
        """
        # Turn lists into tuples to make them hashable
        old_state_hash = tuple(old_state._rows)
        new_state_hash = tuple(new_state._rows)

        # if the tuple (`old_state`, `action`) is not present in the dictionary, 
        # then add this new key to the dictionary with value equal to the observed reward
        if (old_state_hash, new_state_hash) not in self.q:
            self.q[old_state_hash, new_state_hash] = reward
        else:
            # Consider the action that was played right after by the other player
            # Find the best reward associated to that action

            # next_action is None when the game has finished and all you need to know is REWARD,
            if next_action is None:
                best_future_reward = 0
            else:
                # It means that we are in a phase of game where both players can still win.
                # So the reward is 0, and all you need to know is BEST_FUTURE_REWARD.

                # Consider all possible actions starting from the last action that was played by the other player
                # For each of them, consider the corresponding q-value (i.e., the last entry in the q dictionary)
                # Isolate the one with the largest q-value
                best_future_reward = max([self.get_q(next_action, action) for action in next_action.possible_new_states()])

            # find the previous q-value
            old_q = self.q[old_state_hash, new_state_hash]

            # update it accordingly
            self.q[old_state_hash, new_state_hash] = old_q + (self.learning_rate * ((reward + best_future_reward) - old_q))

    def get_q(self, state, action):
        """
            Given a state and an action, return the corresponding Q-value (i.e., the last value associated to the matching key in the q dictionary).
            Should it be the first time that this combination of state and action is observed, return 0.

        Args:
            state (Nim)
            action (Nim): action performed in `state`

        Returns:
            float: Q-value when performing `action` in `state`
        """
        state = tuple(state._rows)
        action = tuple(action._rows)
        if (state, action) not in self.q:
            return 0
        return self.q[state, action]


    def best_move_rl(self, state, with_probability = False):
        """
            Given a state `state`, return the action to take.

        Args:
            state (Nim):
            with_probability (bool): 
                    If `with_probability` is `False`, then return the best available action with probability 1.
                    If `with_probability` is `True`, then return the best available action with probability `self.eps`, and 0 otherwise.
                    This is used during training to favour EXPLORATION over EXPLOITATION

        Returns:
            Nim: action to take.
        """
        # with probability = self.eps, the best move corresponds to a random move.
        # This is to favour EXPLORATION over EXPLOITATION.
        if with_probability and random.random() <= self.eps:
            return random.choice(state.possible_new_states())    
        else:
            values = [self.get_q(state, action) for action in state.possible_new_states()]
            return state.possible_new_states()[max(enumerate(values), key=lambda x: x[1])[0]]


def train(nim_game = None, n_iter = 10000, number_of_heaps = 4):
    """
        The AI will play `n_iter` games against itself.
        It will only play games with specified `number_of_heaps`, but with a random number of objects in each heap.
        The maximum number of objects inside the n-th heap is set to (`number_of_heaps` - 1) * 2 + 2. 

        This number corresponds to the number of objects in the last row of a regular Nim game with `number_of_heaps` heaps.

        Though not necessary (we could have trained the AI only on regular Nim games), we wanted our AI to explore a bigger space.

    Args:
        nim_game (NimAI, optional): use a pre-generated NimAI agent. 
        n_iter: number of training epochs
        number_of_heaps: number of heaps in every game the AI will be trained on and played against.

    Returns:
        NimAI: trained AI agent ready to be challenged.
    """
    if nim_game is not None:
        agent = nim_game
    else:
        agent = NimAI()

    return_per_episode = []

    for i in tqdm(range(n_iter), desc = 'Training'):
        # prepare a random configuration for Nim
        random_configuration = random.choices(range(1, (number_of_heaps - 1) * 2 + 2), k = number_of_heaps)
        
        # create the game
        game = Nim(random_configuration)
        
        # Keep track of the last moves made by either player
        last_move = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        # keep track of which player is playing
        turn = 0

        # Play
        while True:
            # current state
            state = Nim(game._rows.copy())
            # next state
            new_state = agent.best_move_rl(game, with_probability = True)

            game.nimming(target = new_state._rows)

            # Update the last_move dictionary
            last_move[turn]["state"] = state
            last_move[turn]["action"] = new_state

            # switch player
            turn = 1 - turn 

            # When game is over, update Q values with rewards
            if sum(game._rows) == 0:
                # loser's last move is given reward -1
                agent.update(old_state = last_move[turn]["state"], new_state = last_move[turn]["action"], reward = -1)
                # winner's last move is given reward +1
                agent.update(old_state = state, new_state = new_state, reward = 1)
                break

            # if the game has not finished and at least one move was played
            elif last_move[turn]["state"] is not None:
                # update other player's last move with reward 0.
                agent.update(old_state = last_move[turn]["state"], new_state = last_move[turn]["action"], next_action = last_move[1 - turn]["action"], reward = 0)

    # Return the trained AI
    return agent
