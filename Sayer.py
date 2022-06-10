import NotationTranslator


class Sayer:

    def __init__(self, engine, lang):
        self.engine = engine
        self.figuresToText = {}
        self.colsToText = {}
        self.rowsToText = {}
        self.castlesToText = {}
        if lang == "ru":
            self.figuresToText = {"K": "король", "Q": "ферзь", "R": "ладья", "B": "слон", "N": "конь", "p": "пешка"}
            self.rowsToText = {"1": "один", "2": "два", "3": "три", "4": "четыре",
                               "5": "пять", "6": "шесть", "7": "семь", "8": "восемь"}
            self.colsToText = {"a": "а", "b": "бэ", "c": "це", "d": "дэ", "e": "е", "f": "эф", "g": "же", "h": "аш"}
            self.castlesToText = {"O-O-O": "длинная рокировка", "O-O": "рокировка"}
        else:
            raise AttributeError("No Sayer language specified. Please specify language")

    def say(self, stringToSay):
        self.engine.say(stringToSay)
        self.engine.runAndWait()

    def sayMove(self, notationString):
        res = ""
        if notationString in self.castlesToText:
            self.say(self.castlesToText[notationString])
            return False
        else:
            error = ""
            if notationString[0] in self.figuresToText:
                res += self.figuresToText[notationString[0]] + " "
            else:
                error += "figure "
            if notationString[1] in self.colsToText:
                res += self.colsToText[notationString[1]] + " "
            else:
                error += "startCol "
            if notationString[2] in self.rowsToText:
                res += self.rowsToText[notationString[2]] + " "
            else:
                error += "startRow "
            if notationString[4] in self.colsToText:
                res += self.colsToText[notationString[4]] + " "
            else:
                error += "endCol "
            if notationString[5] in self.rowsToText:
                res += self.rowsToText[notationString[5]] + " "
            else:
                error += "endRow "
            if len(notationString) > 6:
                if notationString[6] in self.figuresToText:
                    res += self.figuresToText[notationString[6]] + " "
                else:
                    error += "piecePromoting"
            if error != "":
                print("An unexpected error in Sayer: wrong input: " + error)
                return True
            else:
                self.say(res)
                return False
