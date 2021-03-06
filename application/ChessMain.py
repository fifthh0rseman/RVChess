"""
This file is responsible for displaying current GameState information
"""
import pyaudio
import pygame as p
import pyttsx3
from vosk import KaldiRecognizer

import ChessEngine
import Sayer
import VoskAssistant
from translator import NotationTranslator

CLOCK_PANEL_WIDTH = 150
CLOCK_PANEL_HEIGHT = 512
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVELOG_PANEL_WIDTH = 400
MOVELOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # dimension of the board
SQUARE_SIZE = BOARD_HEIGHT / DIMENSION
MAX_FPS = 15
MOVELOG_FONT_SIZE = 20

IMAGES = {}


# Download the images
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("./data/images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


"""
The Main Driver which will handle user input and graphics update
"""


def main():
    model = VoskAssistant.loadModel('ru-small')
    p.init()
    screen = p.display.set_mode((CLOCK_PANEL_WIDTH + BOARD_WIDTH + MOVELOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveLogFont = p.font.SysFont("Helvitca", MOVELOG_FONT_SIZE, False, False)
    moveMade = False  # A flag responsible for if a move is made
    animate = False  # Flag responsible for animation
    loadImages()  # Do this only once
    running = True  # Flag responsible for if an app is running
    squareSelected = ()
    playerClicks = []
    gameOver = False
    voicing = False
    engine = pyttsx3.init()
    sayer = Sayer.Sayer(engine, "ru")
    audioManager = pyaudio.PyAudio()
    currentPiecePromoting = "--"
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                voicing = False
                audioManager.terminate()
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN and not voicing:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = int(location[0] // SQUARE_SIZE)
                    row = int(location[1] // SQUARE_SIZE)
                    color = "w" if gs.whiteToMove else "b"
                    if squareSelected == (row, col) or col >= 8:  # user clicks on the square twice or on the move log
                        squareSelected = ()  # unselect
                        playerClicks = []  # clear player clicks
                    else:
                        if (gs.board[row][col][0] == color and len(playerClicks) == 0) or len(playerClicks) == 1:
                            squareSelected = (row, col)
                            playerClicks.append(squareSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                attrs = vars(validMoves[i])
                                print(', '.join("%s: %s" % item for item in attrs.items()))
                                if move.isPawnPromotion:
                                    if currentPiecePromoting == "--":
                                        print("Please specify the promoting piece: 1 - queen, 2 - rook, "
                                              "3 - bishop, 4 - knight")
                                        continue
                                    else:
                                        move.piecePromoting = currentPiecePromoting
                                        currentPiecePromoting = "--"
                                animate, moveMade = makeMoveAndAnimate(gs, move)
                                print("turn: " + ("white" if gs.whiteToMove else "black"))
                                # undo selecting
                                squareSelected = ()
                                playerClicks = []

                        if not moveMade:
                            attrs = vars(move)
                            print(', '.join("%s: %s" % item for item in attrs.items()))
                            print(move.getFullChessNotation() + " not valid!")
                            squareSelected = ()
                            playerClicks = []
            # button handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move if Z is pressed
                    gs.undoMove()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    if gameOver:
                        gameOver = not gameOver
                        gs.checkmate = False
                        gs.stalemate = False

                if e.key == p.K_r:  # reset the board
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    gameOver = False
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

                if e.key == p.K_g:  # enter the voice mode
                    if not voicing:
                        print("Voice play mode is chosen.")
                        sayer.say("?????????????????? ?????????? ??????????????.")
                        voicing = True
                    else:
                        print("Voice play mode disabled.")
                        sayer.say("???????????? ???????????????????? ????????????")
                        voicing = False
                if e.key == p.K_1:  # queen
                    currentPiecePromoting = "Q"
                if e.key == p.K_2:  # rook
                    currentPiecePromoting = "R"
                if e.key == p.K_3:  # bishop
                    currentPiecePromoting = "B"
                if e.key == p.K_4:  # knight
                    currentPiecePromoting = "N"

        if voicing:
            rec = KaldiRecognizer(model, 16000)
            stream = audioManager.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True,
                                       frames_per_buffer=8000)
            stream.start_stream()
            for text in VoskAssistant.listen(stream, rec):
                print("Received: " + text)
                translator = NotationTranslator.NotationTranslator()
                if "????????" in text:
                    voicing = False
                    sayer.say("???????????? ???????????????????? ????????????")
                    print("voice play mode disabled")
                    stream.close()
                    break
                if "??????????" in text:
                    sayer.say("?????????????? ??????")
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    if gameOver:
                        gameOver = not gameOver
                        gs.checkmate = False
                        gs.stalemate = False
                    break
                if "??????????" in text:
                    sayer.say("?????????? ????????")
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    gameOver = False
                    moveMade = False
                    animate = False
                    break
                if not gameOver:
                    res = translator.reformatSpeech(str(text))
                    if (len(res) < 6 and res != "O-O" and res != "O-O-O") or res == "" or "(-)" in res \
                            or "[-]" in res or "Unknown" in res:
                        sayer.say("?????? ???? ?????? ?????? ??????")
                        print("Sorry, didn't recognize the move. Please repeat again:" + res)
                        break
                    move = gs.proposeMoveFromNotation(res)
                    if move.isPawnPromotion and move.piecePromoting == "--":
                        sayer.say("?????? ???? ??????????. ?????????????? ???????????? ??????????????????????")
                        print("Specify the promoting piece")
                        break
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            animate, moveMade = makeMoveAndAnimate(gs, move)
                    if moveMade:
                        print("Reformatted: " + res)
                        sayer.say("?????????? ??????")
                        if sayer.sayMove(res):
                            raise TypeError("Error in Sayer!")
                        if gs.inCheck and not gs.inDoubleCheck:
                            sayer.say("??????")
                        if gs.inDoubleCheck:
                            sayer.say("?????????????? ??????")
                        if gs.stalemate:
                            sayer.say("??????")
                        if gs.checkmate:
                            sayer.say("?? ??????")
                    else:
                        print("Incorrect move.")
                        sayer.say("?????????????????????? ??????")
                        if sayer.sayMove(res):
                            raise TypeError("Error in Sayer!")
                else:
                    sayer.say("???????? ????????????????. ????????????????????, ?????????????????????????? ???????? ?????? ???????????????? ??????.")
            stream.close()
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = "Stalemate" if gs.stalemate else "Black wins by checkmate" if gs.whiteToMove else "White wins by " \
                                                                                                     "checkmate "
            drawEndGameText(screen, text)
        clock.tick(MAX_FPS)
        p.display.flip()


def makeMoveAndAnimate(gs, move):
    gs.makeMove(move)
    moveMade = True
    animate = True
    return animate, moveMade


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


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont, True)
    drawClockPanel(screen, gs)


# todo: make whiteToMove sign to the left

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


def drawClockPanel(screen, gs):
    moveLogRect = p.Rect(BOARD_WIDTH + MOVELOG_PANEL_WIDTH, 0, CLOCK_PANEL_WIDTH, CLOCK_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("blue"), moveLogRect)
    blackTurnRect = p.Rect(BOARD_WIDTH + MOVELOG_PANEL_WIDTH + CLOCK_PANEL_WIDTH * 0.25, 50, CLOCK_PANEL_WIDTH / 2, 80)
    whiteTurnRect = p.Rect(BOARD_WIDTH + MOVELOG_PANEL_WIDTH + CLOCK_PANEL_WIDTH * 0.25, CLOCK_PANEL_HEIGHT - 130,
                           CLOCK_PANEL_WIDTH / 2, 80)
    whiteMoveColor = p.Color("green") if not gs.whiteToMove else p.Color("red")
    blackMoveColor = p.Color("red") if not gs.whiteToMove else p.Color("green")
    p.draw.rect(screen, whiteMoveColor, blackTurnRect)
    p.draw.rect(screen, blackMoveColor, whiteTurnRect)


def drawMoveLog(screen, gs, moveLogFont, ifFullNotation):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVELOG_PANEL_WIDTH, MOVELOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    checksLog = gs.moveLogChecks
    moveTexts = []
    movesPerRow = 3
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + (moveLog[i].getFullChessNotation() if ifFullNotation
                                               else moveLog[i].getShortChessNotation(gs)) + str(checksLog[i])
        if i + 1 < len(moveLog):  # make sure black made a move
            moveString += " " + moveLog[i + 1].getFullChessNotation() + str(checksLog[i + 1]) + " "
        moveTexts.append(moveString)

        if i >= 150:
            moveTexts = moveTexts[1:]


    padding = 5
    paddingY = padding
    lineSpacing = 2

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObject = moveLogFont.render(text, 1, p.Color("White"))
        textLocation = moveLogRect.move(padding, paddingY)
        screen.blit(textObject, textLocation)
        paddingY += textObject.get_height() + lineSpacing


"""
Animating the move
"""


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 4  # frames to move one square
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
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)


if __name__ == "__main__":
    main()
