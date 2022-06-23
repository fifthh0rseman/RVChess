class NotationTranslator:

    def __init__(self):
        self.ruFigureDict = {"король": "K", "ферзь": "Q", "ладья": "R", "слон": "B", "конь": "N", "пешка": "p"}
        self.ruNumberDict = {"один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7, "восемь": 8}
        self.ruColDict = {"а": "a", "б": "b", "бы": "b", "бай": "b", "це": "c", "с": "c", "со": "c", "де": "d", "дай": "d",
                          "я": "e", "ей": "e", "е": "e", "эф": "f", "же": "g", "аш": "h", "аж": "h"}
        self.ruExceptionsList = {"едва": "e2", "опять": "a5", "фадин": "f1"}

    def reformatSpeech(self, speechString):
        objectsList = []
        if not isinstance(speechString, str):
            raise TypeError("Argument is not str.")
        if "длин" in speechString and "рок" in speechString:
            return "O-O-O"
        if "рок" in speechString:
            return "O-O"
        inputString = speechString
        if " " not in inputString:
            print("Incorrect move.")
            return "Unknown (-)[-]-(-)[-]"
        while " " in inputString:
            obj, inputString = inputString.split(" ", 1)
            objectsList.append(obj)
        objectsList.append(inputString)
        res = ""
        collidedValuesFirst = False
        collidedValuesSecond = False
        if len(objectsList) > 0:
            res = self.recognizeFigure(objectsList[0], res)
        if len(objectsList) > 1:
            if objectsList[1] in self.ruExceptionsList:
                res += self.ruExceptionsList[objectsList[1]]
                collidedValuesFirst = True
                res += "-"
            else:
                res = self.recognizeCol(objectsList[1], res)
        if len(objectsList) > 2:
            if not collidedValuesFirst:
                res = self.recognizeRow(objectsList[2], res)
                res += "-"
            else:
                if objectsList[2] in self.ruExceptionsList:
                    res += self.ruExceptionsList[objectsList[1]]
                    collidedValuesSecond = True
                else:
                    res = self.recognizeCol(objectsList[2], res)
        if len(objectsList) > 3:
            if objectsList[3] in self.ruExceptionsList:
                res += self.ruExceptionsList[objectsList[3]]
            else:
                if collidedValuesFirst:
                    res = self.recognizeRow(objectsList[3], res)
                else:
                    res = self.recognizeCol(objectsList[3], res)
        if len(objectsList) > 4:
            if (collidedValuesFirst and not collidedValuesSecond) or (collidedValuesSecond and "p" in res):
                res = self.recognizeFigure(objectsList[4], res)
            else:
                res = self.recognizeRow(objectsList[4], res)
        if len(objectsList) > 5:
            if "p" in res:
                res = self.recognizeFigure(objectsList[5], res)
        return res

    def deprecatedReformatSpeech(self, speechString):
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

        result = self.recognizeCol(moveStartColContender, result)
        if " " in otherPartOfMove:
            moveStartNumberContender, otherPartOfMove = otherPartOfMove.split(" ", 1)
        else:
            print("Incorrect move recognition.")
            return result + "[-]-(-)[-]"
        result = self.recognizeRow(moveStartNumberContender, result)
        result += "-"
        if " " in otherPartOfMove:
            moveEndColContender, otherPartOfMove = otherPartOfMove.split(" ", 1)
            result = self.recognizeCol(moveEndColContender, result)
            if " " in otherPartOfMove:
                moveEndRowContender, otherPartOfMove = otherPartOfMove.split(" ", 1)
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
            print("Row number is not recognized")
            result += "[-]"
        return result

    def recognizeCol(self, moveColContender, result):
        if moveColContender in self.ruExceptionsList:
            result += self.ruExceptionsList[moveColContender]
        else:
            if moveColContender in self.ruColDict:
                result += self.ruColDict[moveColContender]
            elif moveColContender not in self.ruNumberDict:
                if "д" in moveColContender:
                    result += "d"
                elif "ф" in moveColContender:
                    result += "f"
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
                else:
                    print("Column is not recognized")
                    result += "(-)"
            else:
                print("Column is not recognized")
                result += "(-)"
        return result

    def recognizeFigure(self, figure, result):
        if figure in self.ruFigureDict:
            result += self.ruFigureDict[figure]
        else:
            if "коро" in figure:
                result += "K"
            elif "сло" in figure or "салон" in figure:
                result += "B"
            elif "фе" in figure or "фи" in figure or "перси" in figure:
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
