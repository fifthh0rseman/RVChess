import datetime
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import ChessEngine
import NotationTranslator

def loadModel(lang):
    modelle = Model('vosk-model-small-ru-0.22')
    if lang == 'ru-small':
        modelle = Model('vosk-model-small-ru-0.22')
    elif lang == 'en-small':
        modelle = None
    else:
        modelle = None
    return modelle


def loadModelAndStartExperiment():
    model = loadModel('ru-small')
    rec = KaldiRecognizer(model, 16000)
    stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Выберите файл для записи.\n1 - числа\n2 - фигуры\n3 - буквы\n4 - комбинация строк и столбцов\n5 - ходы")
    mode = input()
    startExperiment(mode, stream, rec)


def listen(stream, rec):
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']
                break


def startExperiment(mode, stream, rec):
    if mode == str(1):
        print("Выбран режим записи в файл с числами.")
        file = open('rows.txt', 'a')
    elif mode == str(2):
        print("Выбран режим записи в файл с фигурами.")
        file = open('figures.txt', 'a')
    elif mode == str(3):
        print("Выбран режим записи в файл с буквами.")
        file = open('cols.txt', 'a')
    elif mode == str(4):
        print("Выбран режим записи в файл с комбинацией строк и столбцов.")
        file = open('colsAndRows.txt', 'a')
    elif mode == str(5):
        print("Выбран режим записи в файл с ходами.")
        file = open('moves.txt', 'a')
    else:
        print("Выбран режим произвольного распознавания.")
        file = open('output.txt', 'a')
    now = datetime.datetime.now()
    dateNow = now.strftime("%d-%m-%Y %H:%M")
    file.write("Время опыта: " + dateNow + "\n")
    for text in listen(stream, rec):
        print("Распознано: " + str(text))
        file.write("Распознано: " + str(text) + "\n")
        if "состо" in text:
            print("Ответ: Я готов")
        elif mode == str(5) and "стоп" not in str(text):
            translator = NotationTranslator.NotationTranslator()
            res = translator.reformatSpeech(str(text))
            gs = ChessEngine.GameState()
            res1 = gs.proposeMoveFromNotation(res).getFullChessNotation()
            file.write("Переведеный ход: " + res + "\n")
            file.write("Предложенный ход: " + res1 + "\n")
        if "стоп" in str(text):
            file.write("Эксперимент завершен.\n\n")
            file.close()
            break



#  loadModelAndStartExperiment()