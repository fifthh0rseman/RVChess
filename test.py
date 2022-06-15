from application.translator import NotationTranslator as nt

translator = nt.NotationTranslator()

a = "пешка едва четыре"

b = translator.reformatSpeech(a)
print(b)