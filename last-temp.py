import random
import time
import math
import copy
from move_validation import get_piece_moves
from checkmate_logic import is_checkmate, is_stalemate, is_in_check
from utils import switch_turn

# قيم ثابتة
CHECKMATE = 100000
STALEMATE = 0
MAX_DEPTH = 3  # يمكن زيادته لزيادة الصعوبة

# قيم القطع
pieceScore = {"K": 0, "Q": 90, "R": 50, "B": 35, "N": 30, "P": 10}

# مصفوفات تقييم المواقع
knightScore = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScore = [[4, 3, 2, 1, 1, 2, 3, 4],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [4, 3, 2, 1, 1, 2, 3, 4]]

queenScore = [[1, 1, 1, 3, 1, 1, 1, 1],
              [1, 2, 3, 3, 3, 1, 1, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 2, 3, 3, 3, 1, 1, 1],
              [1, 1, 1, 3, 1, 1, 1, 1]]

rookScore = [[4, 3, 4, 4, 4, 4, 3, 4],
             [4, 4, 4, 4, 4, 4, 4, 4],
             [1, 1, 2, 3, 3, 2, 1, 1],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 1, 2, 3, 3, 2, 1, 1],
             [4, 4, 4, 4, 4, 4, 4, 4],
             [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScore = [[8, 8, 8, 8, 8, 8, 8, 8],
                  [8, 8, 8, 8, 8, 8, 8, 8],
                  [5, 6, 6, 7, 7, 6, 6, 5],
                  [2, 3, 3, 5, 5, 3, 3, 2],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [1, 2, 3, 3, 3, 3, 2, 1],
                  [1, 1, 1, 0, 0, 1, 1, 1],
                  [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                  [1, 1, 1, 0, 0, 1, 1, 1],
                  [1, 2, 3, 3, 3, 3, 2, 1],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [2, 3, 3, 5, 5, 3, 3, 2],
                  [5, 6, 6, 7, 7, 6, 6, 5],
                  [8, 8, 8, 8, 8, 8, 8, 8],
                  [8, 8, 8, 8, 8, 8, 8, 8]]

piecePosScores = {'N': knightScore, 'B': bishopScore, 'Q': queenScore,
                  'R': rookScore, "wp": whitePawnScore, "bp": blackPawnScore}


def get_all_possible_moves(board_obj, color):
    """الحصول على جميع الحركات الممكنة مع ترتيبها حسب الأهمية"""
    moves = []
    board = board_obj.board

    # أولوية تحريك القطع الأكثر قيمة
    piece_order = ['K', 'Q', 'R', 'B', 'N', 'P']

    for piece_type in piece_order:
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece.strip() == '' or piece == '##':
                    continue

                if piece[0].lower() != color[0].lower():
                    continue

                if piece[1].upper() != piece_type:
                    continue

                for end_row in range(8):
                    for end_col in range(8):
                        start_pos = (row, col)
                        end_pos = (end_row, end_col)
                        if get_piece_moves(piece, board_obj, start_pos, color, end_pos):
                            moves.append((start_pos, end_pos))

    return order_moves(moves, board_obj, color)


def order_moves(moves, board_obj, color):
    """ترتيب الحركات حسب الأهمية"""
    scored_moves = []
    board = board_obj.board

    for move in moves:
        score = 0
        start, end = move
        piece = board[start[0]][start[1]]
        target = board[end[0]][end[1]]

        # مكافأة الأكلات
        if target.strip() and target != '##':
            score += 10 * pieceScore.get(target[1].upper(), 0)

        # مكافأة تحريك القطع نحو المركز
        if end[0] in [3, 4] and end[1] in [3, 4]:
            score += 5

        # مكافأة الكش
        temp_board = copy.deepcopy(board_obj)
        temp_board.move_piece(move, color)
        if is_in_check(temp_board, switch_turn(color)):
            score += 30

        scored_moves.append((score, move))

    # ترتيب تنازلي حسب النقاط
    scored_moves.sort(reverse=True, key=lambda x: x[0])
    return [move for (score, move) in scored_moves]


def evaluate_board(board_obj):
    """تقييم اللوحة مع عوامل متعددة"""
    if is_checkmate(board_obj, 'black'):
        return CHECKMATE
    elif is_checkmate(board_obj, 'white'):
        return -CHECKMATE
    elif is_stalemate(board_obj, 'white') or is_stalemate(board_obj, 'black'):
        return STALEMATE

    score = 0
    board = board_obj.board
    center_control = 0
    piece_development = 0

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.strip() == '' or piece == '##':
                continue

            piece_type = piece[1].upper()
            color = piece[0].lower()

            # القيمة الأساسية للقطعة
            value = pieceScore.get(piece_type, 0)

            # قيمة الموقع
            if piece_type == 'P':
                pos_key = 'wp' if color == 'w' else 'bp'
                value += piecePosScores[pos_key][row][col]
            else:
                value += piecePosScores.get(piece_type, [[0] * 8] * 8)[row][col]

            # تحكم المركز
            if (row, col) in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                center_control += 1 if color == 'w' else -1

            # تطور القطع
            if piece_type in ['N', 'B']:
                if color == 'w' and row < 6:
                    piece_development += 1
                elif color == 'b' and row > 1:
                    piece_development -= 1

            if color == 'w':
                score += value
            else:
                score -= value

    # تطبيق العوامل الإضافية
    score += center_control * 3
    score += piece_development * 2

    return score


def minimax(board_obj, depth, alpha, beta, maximizing_player, color):
    """خوارزمية minimax مع alpha-beta pruning"""
    if depth == 0:
        return quiescence_search(board_obj, alpha, beta, color), None

    valid_moves = get_all_possible_moves(board_obj, color)
    if not valid_moves:
        if is_in_check(board_obj, color):
            return (-CHECKMATE, None) if maximizing_player else (CHECKMATE, None)
        else:
            return (STALEMATE, None)

    best_move = None

    if maximizing_player:
        max_score = -math.inf
        for move in valid_moves:
            temp_board = copy.deepcopy(board_obj)
            temp_board.move_piece(move, color)

            current_score, _ = minimax(temp_board, depth - 1, alpha, beta, False, switch_turn(color))

            if current_score > max_score:
                max_score = current_score
                best_move = move
                alpha = max(alpha, current_score)

            if beta <= alpha:
                break

        return max_score, best_move
    else:
        min_score = math.inf
        for move in valid_moves:
            temp_board = copy.deepcopy(board_obj)
            temp_board.move_piece(move, color)

            current_score, _ = minimax(temp_board, depth - 1, alpha, beta, True, switch_turn(color))

            if current_score < min_score:
                min_score = current_score
                best_move = move
                beta = min(beta, current_score)

            if beta <= alpha:
                break

        return min_score, best_move


def quiescence_search(board_obj, alpha, beta, color):
    """بحث إضافي للحركات العدوانية فقط"""
    stand_pat = evaluate_board(board_obj)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    capture_moves = [move for move in get_all_possible_moves(board_obj, color)
                     if is_capture_move(board_obj, move)]

    for move in capture_moves:
        temp_board = copy.deepcopy(board_obj)
        temp_board.move_piece(move, color)
        score = -quiescence_search(temp_board, -beta, -alpha, switch_turn(color))

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def is_capture_move(board_obj, move):
    """تحقق إذا كانت الحركة أكل"""
    start, end = move
    board = board_obj.board
    target = board[end[0]][end[1]]
    return target.strip() != '' and target != '##'


def get_ai_move(board_obj, color):
    """الحصول على أفضل حركة للكمبيوتر"""
    start_time = time.time()

    # زيادة العمق في نهاية اللعبة
    depth = MAX_DEPTH
    if count_pieces(board_obj) < 10:
        depth += 1

    _, best_move = minimax(board_obj, depth, -math.inf, math.inf, True, color)

    end_time = time.time()
    print(f"AI Move Time: {end_time - start_time:.2f}s")

    return best_move


def count_pieces(board_obj):
    """عد القطع المتبقية على اللوحة"""
    count = 0
    for row in board_obj.board:
        for piece in row:
            if piece.strip() and piece != '##':
                count += 1
    return count