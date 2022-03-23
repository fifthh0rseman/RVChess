"""
This file is responsible for displaying current GameState information
"""

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8  # dimension of the board
SQUARE_SIZE = HEIGHT / DIMENSION
MAX_FPS = 15

IMAGES = {}


# Download the images
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("./images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


"""
The Main Driver which will handle user input and graphics update
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # A flag responsible for if a move is made
    animate = False  # Flag responsible for animation
    loadImages()  # Do this only once
    running = True
    squareSelected = ()
    playerClicks = []
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = int(location[0] // SQUARE_SIZE)
                    row = int(location[1] // SQUARE_SIZE)
                    if squareSelected == (row, col):
                        squareSelected = ()  # unselect
                        playerClicks = []  # clear player clicks
                    else:
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if move.isPawnPromotion:
                                    gs.makeMove(validMoves[i], piecePromoting="Q")
                                else:
                                    gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                # get valid chess notation
                                moveNotation = move.getChessNotation()
                                gs.inCheck, gs.checks, gs.pins, gs.inDoubleCheck = gs.checkForPinsAndChecks()
                                number = gs.moveLog.index(move)
                                moveNotation = str(number + 1) + ". " + moveNotation
                                if gs.inCheck and not gs.inDoubleCheck:
                                    moveNotation += "+"
                                elif gs.inDoubleCheck:
                                    moveNotation += "++"
                                elif gs.checkmate:
                                    moveNotation += "#"
                                elif gs.stalemate:
                                    moveNotation += "$"
                                print(moveNotation)
                                # undo selecting
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            print(move.getChessNotation() + " not valid!")
                            playerClicks = [squareSelected]
            # button handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move if Z is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    if gameOver:
                        gameOver = not gameOver
                        gs.checkmate = False
                        gs.stalemate = False

                if e.key == p.K_r:  # reset the board
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, squareSelected)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = "Stalemate" if gs.stalemate else "Black wins by checkmate" if gs.whiteToMove else "White wins by checkmate"
            drawEndGameText(screen, text)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Highlight the squares where pieces can move to
"""


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):  # sqSelected is a piece that can be moved
            # highlight the square
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # transparency value: 0 -> completely transparent, 255 - opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            # highlight moves from the square
            s.fill(p.Color("yellow"))
            for m in validMoves:
                if m.startRow == r and m.startCol == c:
                    screen.blit(s, (SQUARE_SIZE * m.endCol, SQUARE_SIZE * m.endRow))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    global colors
    colors = [p.Color("light gray"), p.Color("dark green")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


"""
Animating the move
"""


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece in rectangle
        if move.pieceCaptured != "--":
            if move.isEnPassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == "b" else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * SQUARE_SIZE, enPassantRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, False, p.Color("Black"), p.Color("White"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


if __name__ == "__main__":
    main()
