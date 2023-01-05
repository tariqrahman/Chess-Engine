import pygame as p
import ChessEngine


WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # For animatin purposes
IMAGES = {}

# Allows us to access images via IMAGES[piece_name]
def loadImages():
    
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Flag to prevent regenerating valid move set while move hasn't been made
    loadImages()
    running = True
    sqSelected = () # Initially no square selected, keeps track of last click
    playerClicks = [] # Keeps track of player clicks

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # Gets (x,y) location of mouse pointer
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                # Conditional which resets decision for user. Undo operation
                if sqSelected == (row,col):
                    sqSelected = () # Deselect
                    playerClicks = [] # Clear player clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    # Only reset moves when a valid move is made
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                    # If we encounter invalid move, set the next click as the first click
                    if not moveMade:
                        playerClicks = [sqSelected]
                            
            # Key Handlers
            elif e.type == p.KEYDOWN:
                # Undo Move
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
        

# Responsible for all graphics within current GameState
def drawGameState(screen, gs):
    drawBoard(screen) # Draw squares on the board
    drawPieces(screen, gs.board) # Draw pieces on top of squares


# Draw the squares on the board. Top left square is always light
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("light blue")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draw pieces on the board using GameState.board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Import for automatically running the function when importing the file
if __name__ == "__main__":
    main()