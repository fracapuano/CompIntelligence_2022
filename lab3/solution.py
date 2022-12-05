from lab_utils.nim import Nim
from lab_utils.nim_game import *
from lab_utils.nim_rules import *
import argparse

def boolean_string(s:str)->bool:
    """This function checks whether or not the input string corresponds to an input boolean string"""
    if s.lower() not in {'false', 'true'}:
        raise ValueError('Not a valid boolean string')
    return s.lower() == 'true'

def parse_args()->object: 
    """args function. 
    Side note: if args.grid_search is False the agent's parameters will be set equal to our best-tested agent,
    trained on Nim(5) ONLY.

    Returns:
        object: args parser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--nim-dimension", default=5, type=int, help="Dimension of the Nim game")
    parser.add_argument("--agent", default="omni", type=str, help="Type of agent to be considered (one in ['omni', 'rules'])")
    parser.add_argument("--grid-search", default=False, type=boolean_string, help="Whether to perform a grid search on parameters of rules or not")
    parser.add_argument("--print-best-config", default=False, type=boolean_string, help="Whether or not to print the best config retrieved during grid search")
    parser.add_argument("--play-action", default=True, type=boolean_string, help="Play the action on the actual Nim game rather than simply returning it")
    parser.add_argument("--return-action", default=False, type=boolean_string, help="Return best action considering the actual Nim game before playing it")
    parser.add_argument("--rule-alpha", default=None, type=float, help="When agent=rules, probability of nimming biggest heap size row")
    parser.add_argument("--rule-strategy", default=None, type=str, help="When agent=rules, strategy to be used to weigh pairwise difference")
    parser.add_argument("--rule-k", default=None, type=int, help="When agent=rules, number of heaps to be eliminated during opening")
    parser.add_argument("--rule-endgame-nim", default=None, type=float, help="When agent=rules, percentage of elements to nim in endgame")
                                            
    return parser.parse_args()

args = parse_args()

def main(): 
    # sanity check on args
    if args.agent.lower() not in ["omni", "rules"] or not isinstance(args.nim_dimension, int):
        raise ValueError("Invalid input types! Please use help to obtain guidance on input types")

    if not args.play_action ^ args.return_action:
        print("Please specify both --play-action and --return-action if you have not already!")
        raise ValueError("Cannot play and return action at the same time!")

    if args.agent.lower() == "rules" and args.grid_search: 
        # this performs grid search on possible configurations
        configs_championship = rules_tournament(Nim(args.nim_dimension))
        best_row = configs_championship.sort_values(by="success", ascending=False).iloc[0,:]

        # initialize game with best config
        game = Nim(args.nim_dimension, agent = args.agent.lower(), **best_row[:-1])

        if args.print_best_config:
            print(best_row)

    if not args.grid_search and not args.agent.lower() == "rules":
        # initialize game with default config 
        game = Nim(args.nim_dimension, agent = args.agent.lower())
    elif not args.grid_search and args.agent.lower() == "rules":
        # given parameters for rule-based agent
        params = {
            "k": args.rule_k if args.rule_k is not None else 1, 
            "alpha": args.rule_alpha if args.rule_alpha is not None else 0., 
            "strategy": args.rule_strategy if args.rule_strategy is not None else "sum", 
            "endgame_nim": args.rule_endgame_nim if args.rule_endgame_nim is not None else 0.6
        }
        game = Nim(args.nim_dimension, agent = args.agent.lower(), **params)
        
    if args.play_action: 
        play(game)
    elif args.return_action: 
        best_move = (best_move_nim_sum if game.agent == 'omni' else best_move_rules)(game)
        print(f"According to my super-powers, starting from {game._rows}, the best move is {best_move}")

if __name__ == "__main__": 
    main()
