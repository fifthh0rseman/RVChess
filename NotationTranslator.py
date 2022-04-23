class NotationTranslator:

    def __init__(self):
        self.ruFigureDict = {"король": "K", "ферзь": "Q", "ладья": "R", "слон": "B", "конь": "N", "пешка": "p"}
        self.ruNumberDict = {"один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7, "восемь": 8}
        self.ruColDict = {"а": "a", "б": "b", "бы": "b", "бай": "b", "це": "c", "де": "d", "дай": "d",
                          "я": "e", "ей": "e", "е": "e", "эф": "f", "же": "g", "аш": "h"}
        self.ruExceptionsList = {"едва": "e2"}

    def reformatSpeech(self, speechString):
        if not isinstance(speechString, str):
            raise TypeError("Argument is not str.")
        if "длин" in speechString and "рок" in speechString:
            return "O-O-O"
        if "рок" in speechString:
            return "O-O"
        speechString.lower()
        result = ""
        if " " in speechString:
            figure, move = speechString.split(" ", 1)
        else:
            print("Incorrect move recognition.")
            return "Unknown (-)[-]-(-)[-]"
        figure = str(figure)
        move = str(move)
        result = self.recognizeFigure(figure, result)
        if " " in move:
            moveStartColContender, otherPartOfMove = move.split(" ", 1)
        else:
            print("Incorrect move recognition.")
            return result + "(-)[-]-(-)[-]"
        moveStartColContender = str(moveStartColContender)
        otherPartOfMove = str(otherPartOfMove)
        parsingNumberIsNeeded = True

        parsingNumberIsNeeded, result = self.recognizeCol(moveStartColContender, parsingNumberIsNeeded, result)
        moveEnded = False
        if parsingNumberIsNeeded:
            if " " in otherPartOfMove:
                moveStartNumberContender, otherPartOfMove = otherPartOfMove.split(" ", 1)
            else:
                moveStartNumberContender = otherPartOfMove
                moveEnded = True
            result = self.recognizeRow(moveStartNumberContender, result)
        if moveEnded:
            return result
        else:
            result += "-"
            if " " in otherPartOfMove:
                moveEndColContender, moveEndRowContender = otherPartOfMove.split(" ", 1)
                parsingNumberIsNeeded, result = self.recognizeCol(moveEndColContender, parsingNumberIsNeeded, result)
                result = self.recognizeRow(moveEndRowContender, result)
                return result
            elif otherPartOfMove in self.ruExceptionsList:
                result += self.ruExceptionsList[otherPartOfMove]
            else:
                print("Neither endCol, nor endRow is not recognized")
                result += "(-)[-]"
                print("Returned:" + result)
            return result

    def recognizeRow(self, moveStartNumberContender, result):
        if moveStartNumberContender in self.ruNumberDict:
            result += str(self.ruNumberDict[moveStartNumberContender])
        else:
            # todo
            print("Row number is not recognized")
            result += "[-]"
        return result

    def recognizeCol(self, moveColContender, parsingNumberIsNeeded, result):
        if moveColContender in self.ruExceptionsList:
            result += self.ruExceptionsList[moveColContender]
            parsingNumberIsNeeded = False
        else:
            if moveColContender in self.ruColDict:
                result += self.ruColDict[moveColContender]
            elif moveColContender not in self.ruNumberDict:
                if "д" in moveColContender:
                    result += "d"
                elif "ж" in moveColContender:
                    result += "g"
                elif "б" in moveColContender:
                    result += "b"
                elif "ц" in moveColContender:
                    result += "c"
                elif "а" in moveColContender:
                    result += "a"
                elif "е" in moveColContender:
                    result += "e"
                elif "ф" in moveColContender:
                    result += "f"
                else:
                    print("Column is not recognized")
                    result += "(-)"
            else:
                print("Column is not recognized")
                result += "(-)"
        return parsingNumberIsNeeded, result

    def recognizeFigure(self, figure, result):
        if figure in self.ruFigureDict:
            result += self.ruFigureDict[figure]
        else:
            if "коро" in figure:
                result += "K"
            elif "сло" in figure:
                result += "B"
            elif "фе" in figure:
                result += "Q"
            elif "лад" in figure:
                result += "R"
            elif "кон" in figure:
                result += "N"
            elif "пеш" in figure:
                result += "p"
            else:
                print("Incorrect figure recognition.")
                result += "Unknown "
        return result
