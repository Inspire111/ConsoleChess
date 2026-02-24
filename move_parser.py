import re
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

PIECE_MAP = {
    'K': King,
    'Q': Queen,
    'R': Rook,
    'B': Bishop,
    'N': Knight,
}


def parse_square(square_str):

    if len(square_str) != 2:
        return None
    
    file_char = square_str[0].lower()
    rank_char = square_str[1]
    
    if file_char not in 'abcdefgh' or rank_char not in '12345678':
        return None
    
    col = ord(file_char) - ord('a')
    row = 8 - int(rank_char)
    
    return (row, col)


def square_to_algebraic(row, col):
    file_char = chr(ord('a') + col)
    rank_char = str(8 - row)
    return file_char + rank_char


def parse_move(move_str, color, board):
    move_str = move_str.strip()
    
    if move_str in ['O-O', '0-0', 'o-o']:
        return parse_castling(color, board, kingside=True)
    if move_str in ['O-O-O', '0-0-0', 'o-o-o']:
        return parse_castling(color, board, kingside=False)
    
    # reg move pattern: [Piece][disambiguation][x][target][=Promotion]
    
    pattern = r'^([KQRBN])?([a-h])?([1-8])?(x)?([a-h][1-8])(=([QRBN]))?$'
    match = re.match(pattern, move_str)
    
    if not match:
        return None
    
    piece_char = match.group(1)  # K, Q, R, B, N or None (pawn)
    disambig_file = match.group(2)  # a-h or None
    disambig_rank = match.group(3)  # 1-8 or None
    is_capture = match.group(4) is not None  # x
    target_square = match.group(5)  # e4
    promotion_char = match.group(7)  # Q, R, B, N or None
    
    to_pos = parse_square(target_square)
    if to_pos is None:
        return None
    
    if piece_char:
        piece_type = PIECE_MAP[piece_char]
    else:
        piece_type = Pawn
    
    candidates = board.find_pieces(piece_type, color)
    valid_candidates = []
    
    for pos in candidates:
        piece = board.get_piece(pos[0], pos[1])
        possible_moves = piece.get_possible_moves(pos, board)
        
        if to_pos in possible_moves:
            if disambig_file and chr(ord('a') + pos[1]) != disambig_file:
                continue
            if disambig_rank and str(8 - pos[0]) != disambig_rank:
                continue
            
            valid_candidates.append(pos)
    
    if len(valid_candidates) == 0:
        return None
    if len(valid_candidates) > 1:
        return None
    
    from_pos = valid_candidates[0]
    
    # Handle promotion
    promotion = None
    if promotion_char:
        promotion = PIECE_MAP[promotion_char]
    
    return {
        'from': from_pos,
        'to': to_pos,
        'promotion': promotion
    }


def parse_castling(color, board, kingside):
    king_row = 7 if color == 'white' else 0
    king_col = 4
    
    king = board.get_piece(king_row, king_col)
    if not isinstance(king, King) or king.color != color:
        return None
    
    if kingside:
        target_col = 6
    else:
        target_col = 2
    
    # Check if castling is in possible moves
    possible = king.get_possible_moves((king_row, king_col), board)
    if (king_row, target_col) not in possible:
        return None
    
    return {
        'from': (king_row, king_col),
        'to': (king_row, target_col),
        'promotion': None
    }


def is_valid_move(move, color, board):
    # Make the move on a copy of the board
    test_board = board.copy()
    test_board.move_piece(move['from'], move['to'], move.get('promotion'))
    
    # Check if king is in check after the move
    return not test_board.is_in_check(color)


def get_move_notation(from_pos, to_pos, piece, board, is_capture=False, promotion=None):
    notation = ""
    
    # Castling
    if isinstance(piece, King) and abs(to_pos[1] - from_pos[1]) == 2:
        if to_pos[1] > from_pos[1]:
            return "O-O"
        else:
            return "O-O-O"
    
    # Piece letter (not for pawns)
    if not isinstance(piece, Pawn):
        notation += piece.symbol().upper()
    
    # Disambiguation for non-pawns
    if not isinstance(piece, Pawn):
        same_type_pieces = board.find_pieces(type(piece), piece.color)
        others_can_reach = []
        for pos in same_type_pieces:
            if pos != from_pos:
                other_piece = board.get_piece(pos[0], pos[1])
                if to_pos in other_piece.get_possible_moves(pos, board):
                    others_can_reach.append(pos)
        
        if others_can_reach:
            same_file = any(pos[1] == from_pos[1] for pos in others_can_reach)
            same_rank = any(pos[0] == from_pos[0] for pos in others_can_reach)
            
            if not same_file:
                notation += chr(ord('a') + from_pos[1])
            elif not same_rank:
                notation += str(8 - from_pos[0])
            else:
                notation += chr(ord('a') + from_pos[1]) + str(8 - from_pos[0])
    
    # Pawn captures include source file
    if isinstance(piece, Pawn) and is_capture:
        notation += chr(ord('a') + from_pos[1])
    
    # Capture symbol
    if is_capture:
        notation += 'x'
    
    # Target square
    notation += square_to_algebraic(to_pos[0], to_pos[1])
    
    # Promotion
    if promotion:
        notation += '=' + promotion('white').symbol().upper()
    
    return notation
