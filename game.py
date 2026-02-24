from board import Board
from move_parser import parse_move, is_valid_move
from pieces import King, Pawn


class Game:
    def __init__(self):
        """Initialize a new game."""
        self.board = Board()
        self.current_turn = 'white'
        self.move_history = []
        self.game_over = False
        self.winner = None
    
    def switch_turn(self):
        if self.current_turn == 'white':
            self.current_turn = 'black'
        else:
            self.current_turn = 'white'
    
    def make_move(self, move_str):
        move = parse_move(move_str, self.current_turn, self.board)
        
        if move is None:
            return False, f"Invalid move: '{move_str}'. Could not parse or no piece can make that move."
        
        if not is_valid_move(move, self.current_turn, self.board):
            return False, f"Illegal move: '{move_str}'. This would leave your king in check."
        
        # Execute the move
        from_pos = move['from']
        to_pos = move['to']
        
        captured = self.board.move_piece(from_pos, to_pos, move.get('promotion'))
        
        self.move_history.append({
            'notation': move_str,
            'from': from_pos,
            'to': to_pos,
            'captured': captured,
            'player': self.current_turn
        })
        
        self.switch_turn()
        
        status_msg = self._check_game_state()
        
        if captured:
            return True, f"Move played. Captured {captured.symbol()}. {status_msg}"
        return True, f"Move played. {status_msg}"
    
    def _check_game_state(self):
        in_check = self.board.is_in_check(self.current_turn)
        has_legal_moves = self._has_legal_moves(self.current_turn)
        
        if in_check and not has_legal_moves:
            self.game_over = True
            if self.current_turn == 'white':
                self.winner = 'black'
            else:
                self.winner = 'white'
            return f"Checkmate! {self.winner.capitalize()} wins!"
        
        if not in_check and not has_legal_moves:
            self.game_over = True
            return "Stalemate! The game is a draw."
        
        if in_check:
            return "Check!"
        
        return ""
    
    def _has_legal_moves(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece is not None and piece.color == color:
                    possible_moves = piece.get_possible_moves((row, col), self.board)
                    for move in possible_moves:
                        # Test if this move is legal
                        test_move = {
                            'from': (row, col),
                            'to': move,
                            'promotion': None
                        }
                        if is_valid_move(test_move, color, self.board):
                            return True
        return False
    
    def display(self):
        self.board.display()
    
    def get_status(self):
        if self.game_over:
            if self.winner:
                return f"Game over. {self.winner.capitalize()} wins!"
            return "Game over. Draw."
        
        status = f"{self.current_turn.capitalize()}'s turn"
        if self.board.is_in_check(self.current_turn):
            status += " (in check)"
        return status


def play_game():
    """Main game loop."""
    game = Game()
    
    print("=" * 50)
    print("       CONSOLE CHESS")
    print("=" * 50)
    print("\nEnter moves in algebraic notation:")
    print("  - Pawn moves: e4, d5, exd5")
    print("  - Piece moves: Nf3, Bb5, Qxd7")
    print("  - Castling: O-O (kingside), O-O-O (queenside)")
    print("  - Promotion: e8=Q")
    print("\nType 'quit' to exit, 'help' for commands")
    print("=" * 50)
    
    while not game.game_over:
        game.display()
        print(game.get_status())
        
        try:
            move_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGame aborted.")
            break
        
        if not move_input:
            continue
        
        if move_input.lower() == 'quit':
            print("Thanks for playing!")
            break
        
        if move_input.lower() == 'help':
            print("\nCommands:")
            print("  quit   - Exit the game")
            print("  help   - Show this help message")
            print("\nMove notation:")
            print("  e4     - Move pawn to e4")
            print("  Nf3    - Move knight to f3")
            print("  Bxe5   - Bishop captures on e5")
            print("  Rad1   - Rook from a-file to d1")
            print("  O-O    - Kingside castle")
            print("  O-O-O  - Queenside castle")
            print("  e8=Q   - Promote pawn to queen")
            continue
        
        success, message = game.make_move(move_input)
        print(message)
    
    if game.game_over:
        game.display()
        print(game.get_status())


if __name__ == '__main__':
    play_game()