import chess
from algorithms.minimax import minimax
from algorithms.abpruning import alpha_beta
from utils import evaluate_board
import random

previous_moves = []

def get_best_move(board, depth, use_alphabeta=True, maximizing_player=True):
    best_move = None
    best_eval = float('-inf') if maximizing_player else float('inf')
    move_scores = []

    for move in board.legal_moves:
        if len(previous_moves) >= 2 and move == previous_moves[-2]:
            continue

        board.push(move)

        if use_alphabeta:
            eval = alpha_beta(board, depth - 1, float('-inf'), float('inf'), not maximizing_player)
        else:
            eval = minimax(board, depth - 1, not maximizing_player)

        board.pop()
        move_scores.append((move, eval))

        if maximizing_player:
            if eval > best_eval:
                best_eval = eval
                best_move = move
        else:
            if eval < best_eval:
                best_eval = eval
                best_move = move

    # Select among near-best moves to add variety
    top_moves = [m for m, e in move_scores if abs(e - best_eval) < 0.2]
    if top_moves:
        best_move = random.choice(top_moves)

    return best_move, best_eval
