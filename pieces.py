class Piece:
    def __init__(self, color):
        self.color = color
        self.has_moved = False
    
    def symbol(self):
        """Return the display symbol for this piece."""
        raise NotImplementedError
    
    def get_possible_moves(self, pos, board):
        """
        Return list of possible target squares for this piece.
        """
        raise NotImplementedError
    
    def _is_valid_square(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8
    
    def _can_move_to(self, row, col, board):
        if not self._is_valid_square(row, col):
            return False
        piece = board.get_piece(row, col)
        return piece is None or piece.color != self.color
    
    def _can_capture_on(self, row, col, board):
        if not self._is_valid_square(row, col):
            return False
        piece = board.get_piece(row, col)
        return piece is not None and piece.color != self.color


class Pawn(Piece):
    def symbol(self):
        if self.color == 'white':
            return 'P'
        else:
            return 'p'
    
    def get_possible_moves(self, pos, board):
        moves = []
        row, col = pos
        
        if self.color == 'white':
            direction = -1
            start_row = 6
        else:
            direction = 1
            start_row = 1
        
        new_row = row + direction
        if self._is_valid_square(new_row, col) and board.get_piece(new_row, col) is None:
            moves.append((new_row, col))
            
            if row == start_row:
                new_row2 = row + 2 * direction
                if board.get_piece(new_row2, col) is None:
                    moves.append((new_row2, col))
        
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if self._is_valid_square(new_row, new_col):
                target = board.get_piece(new_row, new_col)
                if target is not None and target.color != self.color:
                    moves.append((new_row, new_col))
                elif board.en_passant_target == (new_row, new_col):
                    moves.append((new_row, new_col))
        
        return moves


class Rook(Piece):
    def symbol(self):
        if self.color == 'white':
            return 'R'
        else:
            return 'r'
    
    def get_possible_moves(self, pos, board):
        moves = []
        row, col = pos
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self._is_valid_square(new_row, new_col):
                    break
                target = board.get_piece(new_row, new_col)
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class Knight(Piece):

    def symbol(self):
        if self.color == 'white':
            return 'N'
        else:
            return 'n'
    
    def get_possible_moves(self, pos, board):
        moves = []
        row, col = pos
        
        # All possible L-shaped moves
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if self._can_move_to(new_row, new_col, board):
                moves.append((new_row, new_col))
        
        return moves


class Bishop(Piece):
    def symbol(self):
        if self.color == 'white':
            return 'B'
        else:
            return 'b'
    
    def get_possible_moves(self, pos, board):
        moves = []
        row, col = pos
        
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self._is_valid_square(new_row, new_col):
                    break
                target = board.get_piece(new_row, new_col)
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class Queen(Piece):
    def symbol(self):
        if self.color == 'white':
            return 'Q'
        else:
            return 'q'
    
    def get_possible_moves(self, pos, board):
        moves = []
        row, col = pos
        
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self._is_valid_square(new_row, new_col):
                    break
                target = board.get_piece(new_row, new_col)
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class King(Piece):
    def symbol(self):
        if self.color == 'white':
            return 'K'
        else:
            return 'k'
    
    def get_possible_moves(self, pos, board):
        moves = []
        row, col = pos
        
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self._can_move_to(new_row, new_col, board):
                moves.append((new_row, new_col))
        
        if not self.has_moved:
            if self._can_castle_kingside(row, col, board):
                moves.append((row, col + 2))
            if self._can_castle_queenside(row, col, board):
                moves.append((row, col - 2))
        
        return moves
    
    def _can_castle_kingside(self, row, col, board):
        rook = board.get_piece(row, 7)
        if not isinstance(rook, Rook) or rook.has_moved:
            return False
        
        if board.get_piece(row, 5) is not None or board.get_piece(row, 6) is not None:
            return False
        
        if board.is_square_attacked(row, col, self.color):
            return False
        if board.is_square_attacked(row, col + 1, self.color):
            return False
        if board.is_square_attacked(row, col + 2, self.color):
            return False
        
        return True
    
    def _can_castle_queenside(self, row, col, board):
        """Check if queenside castling is possible."""
        rook = board.get_piece(row, 0)
        if not isinstance(rook, Rook) or rook.has_moved:
            return False
        
        if board.get_piece(row, 1) is not None or board.get_piece(row, 2) is not None or board.get_piece(row, 3) is not None:
            return False
        
        if board.is_square_attacked(row, col, self.color):
            return False
        if board.is_square_attacked(row, col - 1, self.color):
            return False
        if board.is_square_attacked(row, col - 2, self.color):
            return False
        
        return True