import chess
import os
import matplotlib.pyplot as plt
import chess.svg
from PIL import Image
import cairosvg

piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3.2,
    chess.BISHOP: 3.3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# You can expand this with more tables
piece_square_tables = {
    chess.PAWN: [
        0, 0, 0, 0, 0, 0, 0, 0,
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
        0.1, 0.1, 0.2, 0.3, 0.3, 0.2, 0.1, 0.1,
        0.05, 0.05, 0.1, 0.25, 0.25, 0.1, 0.05, 0.05,
        0, 0, 0, 0.2, 0.2, 0, 0, 0,
        0.05, -0.05, -0.1, 0, 0, -0.1, -0.05, 0.05,
        0.05, 0.1, 0.1, -0.2, -0.2, 0.1, 0.1, 0.05,
        0, 0, 0, 0, 0, 0, 0, 0
    ],
    chess.KNIGHT: [
        -0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5,
        -0.4, -0.2, 0, 0, 0, 0, -0.2, -0.4,
        -0.3, 0, 0.1, 0.15, 0.15, 0.1, 0, -0.3,
        -0.3, 0.05, 0.15, 0.2, 0.2, 0.15, 0.05, -0.3,
        -0.3, 0, 0.15, 0.2, 0.2, 0.15, 0, -0.3,
        -0.3, 0.05, 0.1, 0.15, 0.15, 0.1, 0.05, -0.3,
        -0.4, -0.2, 0, 0.05, 0.05, 0, -0.2, -0.4,
        -0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5
    ]
    # chess.BISHOP: [
    #     # Add Bishop piece-square table here
    # ],
    # chess.ROOK: [
    #     # Add Rook piece-square table here
    # ],
    # chess.QUEEN: [
    #     # Add Queen piece-square table here
    # ],
    # chess.KING: [
    #     # Add King piece-square table here
    # ]
}

def piece_square_value(piece, square, is_white):
    if piece.piece_type in piece_square_tables:
        index = square if is_white else chess.square_mirror(square)
        return piece_square_tables[piece.piece_type][index]
    return 0

def evaluate_board(board):
    if board.is_checkmate():
        return float('-inf') if board.turn == chess.WHITE else float('inf')
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    eval = 0

    # Material and positional value
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values.get(piece.piece_type, 0)
            pos_value = piece_square_value(piece, square, piece.color == chess.WHITE)
            if piece.color == chess.WHITE:
                eval += value + pos_value
            else:
                eval -= value + pos_value

    # Mobility
    white_mobility = len(list(board.legal_moves)) if board.turn == chess.WHITE else 0
    black_mobility = len(list(board.legal_moves)) if board.turn == chess.BLACK else 0
    eval += 0.1 * (white_mobility - black_mobility)

    # Center control
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    for square in center_squares:
        piece = board.piece_at(square)
        if piece:
            eval += 0.2 if piece.color == chess.WHITE else -0.2

    # Penalize doubled pawns
    for file in range(8):
        white_pawns = [sq for sq in chess.SquareSet(chess.BB_FILES[file]) if board.piece_at(sq) == chess.Piece(chess.PAWN, chess.WHITE)]
        black_pawns = [sq for sq in chess.SquareSet(chess.BB_FILES[file]) if board.piece_at(sq) == chess.Piece(chess.PAWN, chess.BLACK)]
        if len(white_pawns) > 1:
            eval -= 0.2 * (len(white_pawns) - 1)
        if len(black_pawns) > 1:
            eval += 0.2 * (len(black_pawns) - 1)

    # King safety (penalize threats around king)
    for color in [chess.WHITE, chess.BLACK]:
        king_square = board.king(color)
        if king_square is not None:
            king_ring = board.attacks(king_square)
            threats = sum(1 for sq in king_ring if board.is_attacked_by(not color, sq))
            if color == chess.WHITE:
                eval -= 0.05 * threats
            else:
                eval += 0.05 * threats

    # Encourage castling
    if not board.has_castling_rights(chess.WHITE):
        eval -= 0.3
    if not board.has_castling_rights(chess.BLACK):
        eval += 0.3

    # Reward passed pawns
    for pawn_square in board.pieces(chess.PAWN, chess.WHITE):
        if not any(board.piece_at(sq) and board.piece_at(sq).color == chess.BLACK
                   for sq in chess.SquareSet(chess.BB_FILES[chess.square_file(pawn_square)])):
            eval += 0.2
    for pawn_square in board.pieces(chess.PAWN, chess.BLACK):
        if not any(board.piece_at(sq) and board.piece_at(sq).color == chess.WHITE
                   for sq in chess.SquareSet(chess.BB_FILES[chess.square_file(pawn_square)])):
            eval -= 0.2

    return eval

# def save_board_image(board, move_count, output_dir='frames'):
#     # Create the directory to save images if it doesn't exist
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
    
#     # Generate the SVG of the current board state
#     board_svg = chess.svg.board(board)
    
#     # Save the SVG as an image
#     img_path = os.path.join(output_dir, f"move_{move_count}.png")
#     with open(img_path, 'w') as f:
#         f.write(board_svg)
    
#     # Convert SVG to PNG using PIL
#     img = Image.open(img_path)
#     img.save(img_path)
#     return img_path


# def save_board_svg(board, move_number):
#     if not os.path.exists("frames_min_max"):
#         os.makedirs("frames_min_max")
#     svg = chess.svg.board(board=board, size=500)
#     filepath = f"frames_min_max/board_{move_number:03d}.svg"
#     with open(filepath, "w", encoding="utf-8") as f:
#         f.write(svg)

#     # Convert SVG to PNG
#     svg_filepath = f"frames_min_max/board_{move_number:03d}.svg"
#     png_filepath = f"frames_min_max/board_{move_number:03d}.png"
#     cairosvg.svg2png(url=svg_filepath, write_to=png_filepath)

# def save_board_svg_ab(board, move_number):
#     svg = chess.svg.board(board=board, size=500)
#     filepath = f"frames_ab/board_{move_number:03d}.svg"
#     with open(filepath, "w", encoding="utf-8") as f:
#         f.write(svg)

#     # Convert SVG to PNG
#     svg_filepath = f"frames_ab/board_{move_number:03d}.svg"
#     png_filepath = f"frames_ab/board_{move_number:03d}.png"
#     cairosvg.svg2png(url=svg_filepath, write_to=png_filepath)


def save_board_svg(board, move_number):
    if not os.path.exists("frames"):
        os.makedirs("frames")
    svg = chess.svg.board(board=board, size=500)
    filepath = f"frames/board_{move_number:03d}.svg"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)

    # Convert SVG to PNG
    svg_filepath = f"frames/board_{move_number:03d}.svg"
    png_filepath = f"frames/board_{move_number:03d}.png"
    cairosvg.svg2png(url=svg_filepath, write_to=png_filepath)
    
    
def create_gif(frame_files, output_filename="chess_game.gif", duration=500):
    # Open all the PNG images and append them to a list
    images = [Image.open(file) for file in frame_files]
    # Create a GIF from the images
    images[0].save(output_filename, save_all=True, append_images=images[1:], duration=duration, loop=0)