class ChessException(Exception):
    """Base exception class for all chess-related errors."""
    pass


class InvalidMoveError(ChessException):
    """Raised when a move cannot be parsed or is syntactically invalid."""
    
    def __init__(self, move_str, message=None):
        self.move_str = move_str
        if message is None:
            message = f"Invalid move: '{move_str}'. Could not parse or no piece can make that move."
        super().__init__(message)


class IllegalMoveError(ChessException):
    """Raised when a move is valid syntax but illegal (e.g., leaves king in check)."""
    
    def __init__(self, move_str, message=None):
        self.move_str = move_str
        if message is None:
            message = f"Illegal move: '{move_str}'. This would leave your king in check."
        super().__init__(message)


class InvalidFENError(ChessException):
    """Raised when a FEN string cannot be parsed or is malformed."""
    
    def __init__(self, fen_str, message=None):
        self.fen_str = fen_str
        if message is None:
            message = f"Invalid FEN notation: '{fen_str}'."
        super().__init__(message)


class GameOverError(ChessException):
    """Raised when trying to make a move after the game has ended."""
    
    def __init__(self, message="Cannot make a move - the game is already over."):
        super().__init__(message)
