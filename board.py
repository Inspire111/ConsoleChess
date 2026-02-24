from pieces import Pawn, Rook, Knight, Bishop, Queen, King


class Board:
    def __init__(self):
        self.squares = []
        for row_index in range(8):
            new_row = [None, None, None, None, None, None, None, None]
            self.squares.append(new_row)
        self.en_passant_target = None  # square where en passant is possible
        self._setup_pieces()
    
    def _setup_pieces(self):
        self.squares[0] = [
            Rook('black'), Knight('black'), Bishop('black'), Queen('black'),
            King('black'), Bishop('black'), Knight('black'), Rook('black')
        ]
        
        black_pawns = []
        for i in range(8):
            black_pawns.append(Pawn('black'))
        self.squares[1] = black_pawns
        
        white_pawns = []
        for i in range(8):
            white_pawns.append(Pawn('white'))
        self.squares[6] = white_pawns
        
        self.squares[7] = [
            Rook('white'), Knight('white'), Bishop('white'), Queen('white'),
            King('white'), Bishop('white'), Knight('white'), Rook('white')
        ]
    
    def get_piece(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.squares[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        self.squares[row][col] = piece
    
    def move_piece(self, from_pos, to_pos, promotion_piece=None):
        """
        Move a piece from one position to another.
        
        Args:
            from_pos: (row, col) tuple
            to_pos: (row, col) tuple
            promotion_piece: Piece class for pawn promotion (optional)
            
        Returns:
            captured_piece or None
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.get_piece(from_row, from_col)
        captured = self.get_piece(to_row, to_col)
        
        # handle en passant
        if isinstance(piece, Pawn) and (to_row, to_col) == self.en_passant_target:
            capture_row = from_row  # the captured pawn is on the same row as the capturing pawn
            captured = self.get_piece(capture_row, to_col)
            self.set_piece(capture_row, to_col, None)
        
        # update en passant target
        self.en_passant_target = None
        if isinstance(piece, Pawn) and abs(to_row - from_row) == 2:
            self.en_passant_target = ((from_row + to_row) // 2, from_col)
        
        # castling
        if isinstance(piece, King) and abs(to_col - from_col) == 2:
            if to_col > from_col:  # kingside
                rook = self.get_piece(from_row, 7)
                self.set_piece(from_row, 7, None)
                self.set_piece(from_row, 5, rook)
                rook.has_moved = True
            else:  # queenside
                rook = self.get_piece(from_row, 0)
                self.set_piece(from_row, 0, None)
                self.set_piece(from_row, 3, rook)
                rook.has_moved = True
        
        # pawn promotion
        if isinstance(piece, Pawn) and (to_row == 0 or to_row == 7):
            if promotion_piece:
                piece = promotion_piece(piece.color)
            else:
                piece = Queen(piece.color)  # default is queen
        
        # move the piece
        self.set_piece(from_row, from_col, None)
        self.set_piece(to_row, to_col, piece)
        piece.has_moved = True
        
        return captured
    
    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None
    
    def is_square_attacked(self, row, col, by_color):
        if by_color == 'white':
            enemy_color = 'black'
        else:
            enemy_color = 'white'
        
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece is not None and piece.color == enemy_color:
                    # pawns : check attack squares specifically (not move squares)
                    if isinstance(piece, Pawn):
                        if piece.color == 'white':
                            direction = -1
                        else:
                            direction = 1
                        if r + direction == row and abs(c - col) == 1:
                            return True
                    else:
                        moves = piece.get_possible_moves((r, c), self)
                        if (row, col) in moves:
                            return True
        return False
    
    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if king_pos is None:
            return False
        return self.is_square_attacked(king_pos[0], king_pos[1], color)
    
    def find_pieces(self, piece_type, color):
        positions = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if isinstance(piece, piece_type) and piece.color == color:
                    positions.append((row, col))
        return positions
    
    def copy(self):
        new_board = Board.__new__(Board)
        new_board.squares = []
        for row_index in range(8):
            new_row = [None, None, None, None, None, None, None, None]
            new_board.squares.append(new_row)
        new_board.en_passant_target = self.en_passant_target
        
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece is not None:
                    # Create a copy of the piece
                    new_piece = type(piece)(piece.color)
                    new_piece.has_moved = piece.has_moved
                    new_board.squares[row][col] = new_piece
        
        return new_board
    
    def display(self):
        print()
        print("    a    b    c    d    e    f    g    h")
        print("  +----+----+----+----+----+----+----+----+")
        
        for row in range(8):
            rank = 8 - row
            row_str = f"{rank} |"
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece is None:
                    row_str += "    |"
                else:
                    symbol = piece.symbol()
                    row_str += f" {symbol}  |"
            print(row_str)
            print("  +----+----+----+----+----+----+----+----+")
        
        print()
