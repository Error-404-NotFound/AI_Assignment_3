from utils import evaluate_board
import chess

def minimax(board, depth, maximizing_player):
    # Base case: if depth is 0 or the game is over, evaluate the board
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    # Get the list of legal moves for the current board state
    legal_moves = list(board.legal_moves)

    # Maximizing player's turn (usually white)
    if maximizing_player:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)  # Make the move
            eval = minimax(board, depth - 1, False)  # Recursively call minimax for the opponent
            board.pop()  # Undo the move
            max_eval = max(max_eval, eval)  # Update max_eval with the maximum evaluation
        return max_eval

    # Minimizing player's turn (usually black)
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)  # Make the move
            eval = minimax(board, depth - 1, True)  # Recursively call minimax for the maximizing player
            board.pop()  # Undo the move
            min_eval = min(min_eval, eval)  # Update min_eval with the minimum evaluation
        return min_eval