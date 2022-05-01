"""
This file is responsible for storing all information of GameState, for validating moves at the current state.
It will also keep a MOVE LOG.
"""
import copy


class GameState:
    def __init__(self):
        """

        The board is a 8x8 2dim list, each element containing 2 characters.
        The first character means the color of figure, the second - figure itself. Here's a map:

        b - black
        w - white

        R - rook
        N - knight
        B - bishop
        Q - queen
        K - king
        p - pawn

        """

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]


        self.moveFunctions = {
            "p": self.getPawnMoves, "R": self.getRookMoves, "B": self.getBishopMoves,
            "N": self.getNightMoves, "Q": self.getQueenMoves, "K": self.getKingMoves
        }

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.inDoubleCheck = False
        self.checkmate = False
        self.stalemate = False
        self.pins = []
        self.checks = []
        self.enPassantPossible = ()
        self.enPassantLog = [self.enPassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.CastleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def makeMove(self, move, piecePromoting=""):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # store the move in move log
        self.whiteToMove = not self.whiteToMove  # switch sides
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + piecePromoting

        if move.isEnPassantMove:
            if move.pieceMoved == "wp":
                self.board[move.endRow + 1][move.endCol] = "--"
            else:
                self.board[move.endRow - 1][move.endCol] = "--"

        # update enPassantPossible
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enPassantPossible = ()

        # make castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                # grab the rook and move it
                self.board[move.endRow][move.endCol + 1] = "--"  # erase the rook square
            else:  # queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                # grab the rook and move it
                self.board[move.endRow][move.endCol - 2] = "--"  # erase the rook square

        # update en-passant rights
        self.enPassantLog.append(self.enPassantPossible)

        # update castle rights if it's a rook or a king move
        self.updateCastleRights(move)
        self.CastleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"
                if self.whiteToMove:
                    self.board[move.endRow + 1][move.endCol] = move.pieceCaptured
                else:
                    self.board[move.endRow - 1][move.endCol] = move.pieceCaptured
            self.enPassantLog.pop()
            self.enPassantPossible = self.enPassantLog[-1]

            self.CastleRightsLog.pop()
            self.currentCastlingRights = self.CastleRightsLog[-1]

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # queenside castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            print("undone: " + move.getChessNotation())

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False

    """
    All moves considering checks
    """

    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        moves = []
        self.inCheck, self.pins, self.checks, self.inDoubleCheck = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if not self.inDoubleCheck:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # squares that pieces can move to
                # if knight, capture knight for move the king, other pieces can be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + i * check[2], kingCol + i * check[3])  # check[2] and check[3] are
                        # the directions of the check
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                    # get rid of any moves that don't block the check or move the king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])

            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True

        self.enPassantPossible = tempEnPassantPossible

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        return moves

    def checkForPinsAndChecks(self):
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        inDoubleCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no check or pin is possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        """
                        Possibilities here:
                        1) orthogonally away from the king and the piece is rook
                        2) diagonally from the king and the piece is bishop
                        3) 1 square away from the king and the piece is pawn
                        4) any direction and the piece is queen
                        5) any direction 1 square away and the piece is king (necessary for avoiding "king-tuple")
                        """
                        if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == "p" and (
                                        (enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            if possiblePin == ():  # no piece blocking, so it's a check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking, so it's a pin
                                pins.append(possiblePin)
                                break
                        else:  # not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[1] == "N" and endPiece[0] == enemyColor:
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        if len(checks) == 2:
            inDoubleCheck = True
        return inCheck, pins, checks, inDoubleCheck

    """
    All moves without considering checks
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  # call the appropriate move function based on the piece
        return moves

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        enemyColor = "b" if self.whiteToMove else "w"
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:  # look at the white pawn
            if self.board[r - 1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # captures to the left
                if not piecePinned or pinDirection == (-1, -1):
                    if self.board[r - 1][c - 1][0] == "b":
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                    elif (r - 1, c - 1) == self.enPassantPossible:
                        gsCopy = copy.deepcopy(self)
                        gsCopy.makeMove(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
                        kingRow, kingCol = gsCopy.whiteKingLocation if gsCopy.whiteToMove else \
                            gsCopy.blackKingLocation
                        if not gsCopy.squareUnderAttack(not gsCopy.whiteToMove, kingRow, kingCol):
                            moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
            if c + 1 <= 7:  # captures to the right
                if not piecePinned or pinDirection == (-1, 1):
                    if self.board[r - 1][c + 1][0] == "b":
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                    elif (r - 1, c + 1) == self.enPassantPossible:
                        gsCopy = copy.deepcopy(self)
                        gsCopy.makeMove(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
                        kingRow, kingCol = gsCopy.whiteKingLocation if gsCopy.whiteToMove else gsCopy.blackKingLocation
                        if not gsCopy.squareUnderAttack(not gsCopy.whiteToMove, kingRow, kingCol):
                            moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True))
        else:
            if self.board[r + 1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # captures to the left
                if not piecePinned or pinDirection == (1, -1):
                    if self.board[r + 1][c - 1][0] == "w":
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enPassantPossible:
                        gsCopy = copy.deepcopy(self)
                        gsCopy.makeMove(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
                        kingRow, kingCol = gsCopy.whiteKingLocation if gsCopy.whiteToMove else gsCopy.blackKingLocation
                        if not gsCopy.squareUnderAttack(not gsCopy.whiteToMove, kingRow, kingCol):
                            moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
            if c + 1 <= 7:  # captures to the right
                if not piecePinned or pinDirection == (1, 1):
                    if self.board[r + 1][c + 1][0] == "w":
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enPassantPossible:
                        gsCopy = copy.deepcopy(self)
                        gsCopy.makeMove(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
                        kingRow, kingCol = gsCopy.whiteKingLocation if gsCopy.whiteToMove else gsCopy.blackKingLocation
                        if not gsCopy.squareUnderAttack(not gsCopy.whiteToMove, kingRow, kingCol):
                            moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":  # remove the queen from the pin only once
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":  # remove the queen from the pin only once
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getNightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                if self.board[r][c][1] != "Q":  # remove the queen from the pin only once
                    self.pins.remove(self.pins[i])
                break
        if not piecePinned:
            if r - 2 >= 0 and c + 1 <= 7 and self.board[r - 2][c + 1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r - 2, c + 1), self.board))  # up2-right1
            if r - 2 >= 0 and c - 1 >= 0 and self.board[r - 2][c - 1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r - 2, c - 1), self.board))  # up2-left1
            if r + 2 <= 7 and c + 1 <= 7 and self.board[r + 2][c + 1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r + 2, c + 1), self.board))  # bottom2-left1
            if r + 2 <= 7 and c - 1 >= 0 and self.board[r + 2][c - 1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r + 2, c - 1), self.board))  # bottom2-right1
            if r - 1 >= 0 and c + 2 <= 7 and self.board[r - 1][c + 2][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r - 1, c + 2), self.board))  # up1-right2
            if r - 1 >= 0 and c - 2 >= 0 and self.board[r - 1][c - 2][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r - 1, c - 2), self.board))  # up1-left2
            if r + 1 <= 7 and c + 2 <= 7 and self.board[r + 1][c + 2][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r + 1, c + 2), self.board))  # bottom1-right2
            if r + 1 <= 7 and c - 2 >= 0 and self.board[r + 1][c - 2][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r + 1, c - 2), self.board))  # bottom1-left2

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        allyColor = "w" if self.whiteToMove else "b"
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks, inDoubleCheck = self.checkForPinsAndChecks()
                    # print("generated checks:" + str(checks))
                    if not inCheck:
                        move = Move((r, c), (endRow, endCol), self.board)
                        moves.append(move)
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def squareUnderAttack(self, side, r, c):
        if side:
            return self.squareUnderWhiteAttack(r, c)
        else:
            return self.squareUnderBlackAttack(r, c)

    def squareUnderBlackAttack(self, r, c):
        gs = copy.deepcopy(self)
        res = False
        gs.whiteToMove = False
        gs.board[r][c] = "wQ"
        moves = gs.getAllPossibleMoves()

        for move in moves:
            # print("generated: " + str(move.getChessNotation()) + ", endRow:" + str(move.endRow) + ", endCol:" +
            #      str(move.endCol) + ", r:" + str(r) + ", c:" + str(c))
            if move.endRow == r and move.endCol == c:
                res = True
                break
            else:
                res = False
        return res

    def squareUnderWhiteAttack(self, r, c):
        gs = copy.deepcopy(self)
        res = False
        gs.whiteToMove = True
        gs.board[r][c] = "bQ"
        moves = gs.getAllPossibleMoves()

        for move in moves:
            # print("generated: " + str(move.getChessNotation()) + ", endRow:" + str(move.endRow) + ", endCol:" +
            #      str(move.endCol) + ", r:" + str(r) + ", c:" + str(c))
            if move.endRow == r and move.endCol == c:
                res = True
                break
            else:
                res = False
        return res

    def getCastleMoves(self, r, c, moves):
        if self.inCheck:
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--" and self.board[r][c + 3][1] == "R":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, castle=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--" \
                and self.board[r][c - 4][1] == "R":
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, castle=True))

    def proposeMoveFromNotation(self, moveString):
        kingRow, kingCol = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        if moveString == "O-O":
            return Move((kingRow, kingCol), (kingRow, kingCol + 2), self.board, castle=True)
        elif moveString == "O-O-O":
            return Move((kingRow, kingCol), (kingRow, kingCol - 2), self.board, castle=True)
        else:
            startCol = Move.filesToCols[moveString[1]]
            startRow = Move.ranksToRows[moveString[2]]
            endCol = Move.filesToCols[moveString[4]]
            endRow = Move.ranksToRows[moveString[5]]
            if self.enPassantPossible == (endRow, endCol):
                return Move((startRow, startCol),
                            (endRow, endCol), self.board, isEnPassantMove=True)
            else:
                return Move((startRow, startCol),
                            (endRow, endCol), self.board)




class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}  # dictionary rank-row
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}  # dictionary file-col
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove=False, castle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # unique identifier of the move from 0 to 7777
        # For example: 0002 = move from row 0, col 0 to row 0, col 2

        self.isPawnPromotion = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7):
            self.isPawnPromotion = True

        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

        self.isCastleMove = castle

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def getChessNotation(self):
        # TODO: make this real chess notation
        if self.isCastleMove:
            if self.endCol - self.startCol == 2:
                return "O-O"
            else:
                return "O-O-O"
        else:
            res = self.pieceMoved[1] if self.pieceMoved[1] != "p" else ""
            return res + self.getRankFile(self.startRow, self.startCol) + "-" + \
                   self.getRankFile(self.endRow, self.endCol)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
