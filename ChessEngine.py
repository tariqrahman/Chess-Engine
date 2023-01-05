class GameState():
    def __init__(self):

        # Generate 8x8 board which consists of a 2D list
        # First letter represents color of piece: "w", "b"
        # Second letter represents the type of piece: "R", "N", "B", "Q", "K", "p"
        # "--" Represents an empty space

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "wp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "bp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 
                            'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves }
        self.whiteToMove = True
        self.moveLog = []

        # Keep track of king locations
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = ()
    
    # Takes a move as a parameter and executes it (Won't work for castling and pawn-promotion)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log move to undo later
        self.whiteToMove = not self.whiteToMove # Change turns

        # Update king location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # Enpassant Move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # Update Enpassant Variable
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()


    # Undo last move
    def undoMove(self):
        # Check if no moves have been made
        if len(self.moveLog) != 0:
            # Take most recent move from log and reverse it
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Switch turns back

            # Update the king's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            
            # Undo En Passant
            if move.isEnpassantMove:
                # Leave landing square blank
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)

            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()
            

    # All moves considering checks
    def getValidMoves(self):

        tempEnpassantPossible = self.enPassantPossible

        # Generate all possible moves
        moves = self.getAllPossibleMoves()

        # When removing from list, move backward through list
        for i in range(len(moves) - 1, -1, -1):
            # For each move, make the move
            self.makeMove(moves[i])

            # Switch turns back to ensure makeMove doesn't alter accuracy
            self.whiteToMove = not self.whiteToMove
            # Remove moves which yield a check from validMoves
            if self.inCheck():
                moves.remove(moves[i])
            # Switch turns back to original and undo testing move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        # Determine if no valid moves exist - If so, check for checkMate / staleMate
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        # Ensure we maintain the original Enpassant tuple before engine modification 
        self.enPassantPossible = tempEnpassantPossible
        return moves

    # Determine if current player is in check
    def inCheck(self):
        # If king square is under attack, return True. We'll remove any move which yields this outcome in getValidMoves()
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    
    # Determine if the enemy can attack current square
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # Switch to opponent turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # Switch turns back
        for move in oppMoves:
            # Square is under attack
            if move.endRow == r and move.endCol == c:
                return True
        return False

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
                elif (r - 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove = True))
                
            # Captures to the right
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove = True))

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
                elif (r - 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove = True))
            # Captures to the right
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r - 1, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove = True))


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

    def __init__(self, startSq, endSq, board, isEnpassantMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)

        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "wp"

            
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
