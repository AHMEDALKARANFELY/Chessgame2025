import copy
import math
from move_validation import get_piece_moves
from checkmate_logic import is_checkmate, is_stalemate, is_in_check
from utils import switch_turn

# قيم القطع الأساسية
PIECE_VALUES = {
    'P': 10,  # بيدق
    'N': 30,  # حصان
    'B': 30,  # فيل
    'R': 50,  # قلعة
    'Q': 90,  # وزير
    'K': 900  # ملك
}

# مصفوفات تقييم المواقع لكل قطعة
POSITIONAL_SCORES = {
    'P': [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 5, 5, 5, 5, 5, 5, 5],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [0, 0, 1, 2, 2, 1, 0, 0],
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 0, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ],
    'N': [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 3, 3, 3, 3, 2, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 2, 3, 3, 3, 3, 2, 1],
        [1, 2, 2, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]
    ],
    'B': [
        [4, 3, 2, 1, 1, 2, 3, 4],
        [3, 4, 3, 2, 2, 3, 4, 3],
        [2, 3, 4, 3, 3, 4, 3, 2],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [2, 3, 4, 3, 3, 4, 3, 2],
        [3, 4, 3, 2, 2, 3, 4, 3],
        [4, 3, 2, 1, 1, 2, 3, 4]
    ],
    'R': [
        [4, 3, 4, 4, 4, 4, 3, 4],
        [4, 4, 4, 4, 4, 4, 4, 4],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 2, 3, 4, 4, 3, 2, 1],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [4, 4, 4, 4, 4, 4, 4, 4],
        [4, 3, 4, 4, 4, 4, 3, 4]
    ],
    'Q': [
        [1, 1, 1, 3, 1, 1, 1, 1],
        [1, 2, 3, 3, 3, 1, 1, 1],
        [1, 4, 3, 3, 3, 4, 2, 1],
        [1, 2, 3, 3, 3, 2, 2, 1],
        [1, 2, 3, 3, 3, 2, 2, 1],
        [1, 4, 3, 3, 3, 4, 2, 1],
        [1, 2, 3, 3, 3, 1, 1, 1],
        [1, 1, 1, 3, 1, 1, 1, 1]
    ],
    'K': [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0]
    ]
}


def minimax(board_obj, depth, alpha, beta, maximizing_player, current_color):
    """خوارزمية Minimax مع Alpha-Beta Pruning"""
    if depth == 0 or is_checkmate(board_obj, current_color) or is_stalemate(board_obj, current_color):
        return evaluate_board(board_obj), None

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for move in get_all_possible_moves(board_obj, current_color):
            temp_board = copy.deepcopy(board_obj)
            temp_board.move_piece(move, current_color)

            evaluation, _ = minimax(temp_board, depth - 1, alpha, beta, False, switch_turn(current_color))

            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move

            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break

        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in get_all_possible_moves(board_obj, current_color):
            temp_board = copy.deepcopy(board_obj)
            temp_board.move_piece(move, current_color)

            evaluation, _ = minimax(temp_board, depth - 1, alpha, beta, True, switch_turn(current_color))

            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move

            beta = min(beta, evaluation)
            if beta <= alpha:
                break

        return min_eval, best_move


def get_piece_positional_score(piece, row, col):
    """الحصول على قيمة الموقع للقطعة"""
    piece_type = piece[1].upper()
    if piece_type not in POSITIONAL_SCORES:
        return 0

    if piece[0] == 'b':
        row = 7 - row

    return POSITIONAL_SCORES[piece_type][row][col]


def evaluate_board(board_obj):
    """تقييم اللوحة مع مراعاة مواقع القطع"""
    board = board_obj.board
    score = 0

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.strip() == '' or piece == '##':
                continue

            color = piece[0]
            piece_type = piece[1].upper()
            base_value = PIECE_VALUES.get(piece_type, 0)
            positional_value = get_piece_positional_score(piece, row, col)
            total_value = base_value + positional_value

            if color == 'w':
                score += total_value
            else:
                score -= total_value

    if is_in_check(board_obj, 'white'):
        score -= 20
    if is_in_check(board_obj, 'black'):
        score += 20

    return score


def get_all_possible_moves(board_obj, color):
    """الحصول على كل الحركات الممكنة للون معين"""
    moves = []
    board = board_obj.board

    for start_row in range(8):
        for start_col in range(8):
            piece = board[start_row][start_col]
            if piece.strip() == '' or piece == '##':
                continue

            if piece[0].lower() != color[0].lower():
                continue

            for end_row in range(8):
                for end_col in range(8):
                    start_pos = (start_row, start_col)
                    end_pos = (end_row, end_col)
                    if get_piece_moves(piece, board_obj, start_pos, color, end_pos):
                        moves.append((start_pos, end_pos))

    return moves


def get_ai_move(board_obj, color, depth=3):
    """الحصول على أفضل حركة للكمبيوتر"""
    _, best_move = minimax(board_obj, depth, -math.inf, math.inf, True, color)
    return best_move