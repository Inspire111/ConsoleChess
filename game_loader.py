"""
GameLoader class for loading chess positions from FEN notation.

FEN (Forsyth-Edwards Notation) is a standard notation for describing 
chess positions. Example: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
"""

from board import Board
from pieces import Pawn, Rook, Knight, Bishop, Queen, King
from exceptions import InvalidFENError


PIECE_FROM_FEN = {
    'p': (Pawn, 'black'),
    'r': (Rook, 'black'),
    'n': (Knight, 'black'),
    'b': (Bishop, 'black'),
    'q': (Queen, 'black'),
    'k': (King, 'black'),
    'P': (Pawn, 'white'),
    'R': (Rook, 'white'),
    'N': (Knight, 'white'),
    'B': (Bishop, 'white'),
    'Q': (Queen, 'white'),
    'K': (King, 'white'),
}


class GameLoader:
    """
    Loads chess game states from FEN notation.
    
    Supports both full FEN strings and position-only strings.
    
    Example usage:
        loader = GameLoader()
        game = loader.load_fen("r1bk3r/p2pBpNp/n4n2/1p1NP2P/6P1/3P4/P1P1K3/q5b1")
        game = loader.load_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    """
    
    def __init__(self):
        pass
    
    def load_fen(self, fen_string):
        """
        Load a game state from a FEN string.
        
        Args:
            fen_string: FEN notation string (full or position-only)
            
        Returns:
            Game: A new Game object with the loaded position
            
        Raises:
            InvalidFENError: If the FEN string is malformed
        """
        from game import Game
        
        fen_string = fen_string.strip()
        parts = fen_string.split()
        
        if len(parts) < 1:
            raise InvalidFENError(fen_string, "FEN string is empty.")
        
        # Parse position
        position = parts[0]
        board = self._parse_position(position, fen_string)
        
        # Parse active color (default: white)
        current_turn = 'white'
        if len(parts) >= 2:
            if parts[1] == 'b':
                current_turn = 'black'
            elif parts[1] != 'w':
                raise InvalidFENError(fen_string, f"Invalid active color: '{parts[1]}'. Must be 'w' or 'b'.")
        
        # Parse castling rights (default: none since we loaded a position)
        if len(parts) >= 3:
            self._apply_castling_rights(board, parts[2], fen_string)
        else:
            # If no castling info provided, assume pieces have moved
            self._mark_all_as_moved(board)
        
        # Parse en passant target
        if len(parts) >= 4 and parts[3] != '-':
            ep_square = self._parse_square(parts[3], fen_string)
            board.en_passant_target = ep_square
        
        # Create game with loaded state
        game = Game.__new__(Game)
        game.board = board
        game.current_turn = current_turn
        game.move_history = []
        game.game_over = False
        game.winner = None
        
        return game
    
    def _parse_position(self, position, original_fen):
        """Parse the position part of FEN and return a Board."""
        board = Board.__new__(Board)
        board.squares = []
        for _ in range(8):
            board.squares.append([None] * 8)
        board.en_passant_target = None
        
        ranks = position.split('/')
        if len(ranks) != 8:
            raise InvalidFENError(original_fen, f"Position must have 8 ranks, got {len(ranks)}.")
        
        for row, rank_str in enumerate(ranks):
            col = 0
            for char in rank_str:
                if col > 7:
                    raise InvalidFENError(original_fen, f"Rank {8 - row} has too many squares.")
                
                if char.isdigit():
                    empty_squares = int(char)
                    if empty_squares < 1 or empty_squares > 8:
                        raise InvalidFENError(original_fen, f"Invalid empty square count: {char}")
                    col += empty_squares
                elif char in PIECE_FROM_FEN:
                    piece_class, color = PIECE_FROM_FEN[char]
                    piece = piece_class(color)
                    board.squares[row][col] = piece
                    col += 1
                else:
                    raise InvalidFENError(original_fen, f"Invalid character in position: '{char}'")
            
            if col != 8:
                raise InvalidFENError(original_fen, f"Rank {8 - row} has {col} squares, expected 8.")
        
        return board
    
    def _apply_castling_rights(self, board, castling_str, original_fen):
        """Apply castling rights from FEN to the board."""
        # First mark all kings and rooks as moved
        self._mark_all_as_moved(board)
        
        if castling_str == '-':
            return
        
        for char in castling_str:
            if char == 'K':
                # White can castle kingside
                king = board.get_piece(7, 4)
                rook = board.get_piece(7, 7)
                if isinstance(king, King):
                    king.has_moved = False
                if isinstance(rook, Rook):
                    rook.has_moved = False
            elif char == 'Q':
                # White can castle queenside
                king = board.get_piece(7, 4)
                rook = board.get_piece(7, 0)
                if isinstance(king, King):
                    king.has_moved = False
                if isinstance(rook, Rook):
                    rook.has_moved = False
            elif char == 'k':
                # Black can castle kingside
                king = board.get_piece(0, 4)
                rook = board.get_piece(0, 7)
                if isinstance(king, King):
                    king.has_moved = False
                if isinstance(rook, Rook):
                    rook.has_moved = False
            elif char == 'q':
                # Black can castle queenside
                king = board.get_piece(0, 4)
                rook = board.get_piece(0, 0)
                if isinstance(king, King):
                    king.has_moved = False
                if isinstance(rook, Rook):
                    rook.has_moved = False
            else:
                raise InvalidFENError(original_fen, f"Invalid castling character: '{char}'")
    
    def _mark_all_as_moved(self, board):
        """Mark all pieces as having moved (for loaded positions)."""
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece is not None:
                    piece.has_moved = True
    
    def _parse_square(self, square_str, original_fen):
        """Parse algebraic notation square (e.g., 'e3') to (row, col)."""
        if len(square_str) != 2:
            raise InvalidFENError(original_fen, f"Invalid en passant square: '{square_str}'")
        
        file_char = square_str[0].lower()
        rank_char = square_str[1]
        
        if file_char not in 'abcdefgh' or rank_char not in '12345678':
            raise InvalidFENError(original_fen, f"Invalid en passant square: '{square_str}'")
        
        col = ord(file_char) - ord('a')
        row = 8 - int(rank_char)
        
        return (row, col)
    
    def save_fen(self, game):
        """
        Save the current game state to a FEN string.
        
        Args:
            game: Game object to save
            
        Returns:
            str: FEN notation string
        """
        board = game.board
        
        # Position
        position_parts = []
        for row in range(8):
            rank_str = ""
            empty_count = 0
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        rank_str += str(empty_count)
                        empty_count = 0
                    rank_str += self._piece_to_fen(piece)
            if empty_count > 0:
                rank_str += str(empty_count)
            position_parts.append(rank_str)
        position = '/'.join(position_parts)
        
        # Active color
        color = 'w' if game.current_turn == 'white' else 'b'
        
        # Castling rights
        castling = self._get_castling_rights(board)
        
        # En passant
        if board.en_passant_target:
            row, col = board.en_passant_target
            ep = chr(ord('a') + col) + str(8 - row)
        else:
            ep = '-'
        
        # Halfmove clock and fullmove number (simplified)
        halfmove = '0'
        fullmove = str(len(game.move_history) // 2 + 1)
        
        return f"{position} {color} {castling} {ep} {halfmove} {fullmove}"
    
    def _piece_to_fen(self, piece):
        """Convert a piece to its FEN character."""
        symbol = piece.symbol()
        return symbol
    
    def _get_castling_rights(self, board):
        """Determine castling rights from board state."""
        rights = ""
        
        # White kingside
        king = board.get_piece(7, 4)
        rook = board.get_piece(7, 7)
        if isinstance(king, King) and isinstance(rook, Rook):
            if not king.has_moved and not rook.has_moved:
                rights += 'K'
        
        # White queenside
        rook = board.get_piece(7, 0)
        if isinstance(king, King) and isinstance(rook, Rook):
            if not king.has_moved and not rook.has_moved:
                rights += 'Q'
        
        # Black kingside
        king = board.get_piece(0, 4)
        rook = board.get_piece(0, 7)
        if isinstance(king, King) and isinstance(rook, Rook):
            if not king.has_moved and not rook.has_moved:
                rights += 'k'
        
        # Black queenside
        rook = board.get_piece(0, 0)
        if isinstance(king, King) and isinstance(rook, Rook):
            if not king.has_moved and not rook.has_moved:
                rights += 'q'
        
        return rights if rights else '-'
