
import speech_recognition as sr

from oauth2client.client import GoogleCredentials

mic = sr.Microphone()
running = True
with mic as audio_file:
    while running:
        print("Speak please")
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(audio_file)
        audio = recognizer.listen(audio_file)
        result = recognizer.recognize_google(audio, language='ru-ru')
        print("Command: " + str(result).lower())
        if "отбо" in result:
            print("Выключаюсь")
            running = False
