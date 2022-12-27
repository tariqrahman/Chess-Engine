class GameState():
    def __init__(self):

        # Generate 8x8 board which consists of a 2D list
        # First letter represents color of piece: "w", "b"
        # Second letter represents the type of piece: "R", "N", "B", "Q", "K", "p"
        # "--" Represents an empty space

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "bp", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 
                            'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
    
    # Takes a move as a parameter and executes it (Won't work for castling and pawn-promotion)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log move to undo later
        self.whiteToMove = not self.whiteToMove # Change turns

    

    # Undo last move
    def undoMove(self):
        # Check if no moves have been made
        if len(self.moveLog) != 0:
            # Take most recent move from log and reverse it
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Switch turns back

    # All moves considering checks
    def getValidMoves(self):
        return self.getAllPossibleMoves()

    # All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # Calls appropriate move function based on piece type
        return moves

    # Get all possible moves for a pawn at r,c and add these moves to the list
    def getPawnMoves(self, r, c, moves):
        # White pawn moves
        if self.whiteToMove:
            # Move directly forward
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            # Captures to the left
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            # Captures to the right
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        # Black pawn moves
        else:
            # Move directly forward
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # Captures to the left
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            # Captures to the right
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))


    # Get all possible moves for a rook at r,c and add these moves to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # Up Left Down Right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                # Check if square is on board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    # Empty square
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # Enemy Piece
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    # Companion Piece
                    else:
                        break
                else:
                    break



    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, 1), (-2, -1), (2, 1), (2, -1), (-1, -2), (-1, 2), (1, 2), (1, -2))
        allyColor = "w" if self.whiteToMove else "b"

        for move in knightMoves:
            endRow = r + move[0]
            endCol = c + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # Get all possible moves for Bishops at r,c and add these moves to the list
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # Four Diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            # Bishop can move max of 7 squares
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                # Check if square is on board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    # Empty square
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # Enemy Piece
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    # Companion Piece
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 1), (1, 0))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


# Nested class not useful here, but look it up
class Move():

    # Hashmap translations of ranks to rows, rows to ranks
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5":3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    # Hashmap translations of files to columns, columns to files
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Create unique ID for a given move
        self.moveID = self.startRow * 1000 + self.startCol* 100  + self.endRow * 10 + self.endCol

    # Overriding equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False 


    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r , c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
