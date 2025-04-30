import gym
import gym_chess
import chess
import random
import sys
import os
import chess.pgn
from agent import get_best_move  # Returns (move, evaluation)
from algorithms.minimax import minimax
from algorithms.abpruning import alpha_beta
from utils import evaluate_board, save_board_svg, create_gif
import shutil

def play_game(depth=3, ai_algorithm="alphabeta", user_is_white=True, log_file="game_log.txt"):
    sys.stdout = open(log_file, 'w', encoding='utf-8')

    env = gym.make("Chess-v0")
    env.reset()
    board = env._board

    game = chess.pgn.Game()
    node = game
    move_count = 0
    max_moves = 300
    
    frame_files = []

    print("Game Start!")
    print(f"Player Side (for reference): {'White' if user_is_white else 'Black'}")
    print(f"Algorithm: {ai_algorithm.capitalize()}")
    print("=" * 40)

    while not board.is_game_over():
        if move_count > max_moves:
            print("Terminating: move limit reached.")
            break

        use_ab = (ai_algorithm == 'alphabeta')
        move, evaluation = get_best_move(board, depth, use_alphabeta=use_ab)
        if move is None:
            print("No legal moves. Game over!")
            break

        board.push(move)
        node = node.add_variation(move)
        move_count += 1
        
        save_board_svg(board, move_count)
        frame_files.append(f"frames/board_{move_count:03d}.png")

        print(board)
        print(f"\nMove {move_count}: {move.uci()}")
        print(f"Evaluation: {evaluation}")
        print("Move by:", "White" if board.turn == chess.BLACK else "Black")  # because board.turn flips after push
        print("\n" + "=" * 40 + "\n")

    result = board.result()
    if result == '1-0':
        winner = 'White'
    elif result == '0-1':
        winner = 'Black'
    else:
        winner = 'Draw'
    print(f"Game over! Result: {result}")
    print(f"Winner: {winner}")
    sys.stdout.close()
    
    create_gif(frame_files, output_filename=f"{ai_algorithm}_chess_game.gif", duration=500)
    
    for file in frame_files:
        os.remove(file)
        
    shutil.rmtree('frames', ignore_errors=True)

if __name__ == "__main__":
    import argparse
    
    def parse_args():
        parser = argparse.ArgumentParser(description="Chess AI: Minimax vs Alpha-Beta Pruning")
        parser.add_argument('--depth', type=int, default=3, help='Search depth for AI')
        parser.add_argument('--algo', choices=['minimax', 'alphabeta'], default='alphabeta', help='Algorithm used by AI')
        parser.add_argument('--player_color', choices=['white', 'black'], required=True, help='Your side (for log reference only)')
        return parser.parse_args()
    args = parse_args()
    user_is_white = args.player_color == 'white'
    log_filename = f"user_{args.player_color}_algo_{args.algo}_depth_{args.depth}.txt"
    play_game(depth=args.depth, ai_algorithm=args.algo, user_is_white=user_is_white, log_file=log_filename)
