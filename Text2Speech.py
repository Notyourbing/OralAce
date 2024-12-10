import pyttsx3
engine = pyttsx3.init()

""" RATE"""
rate = engine.getProperty('rate')
engine.setProperty('rate', 150)


"""VOLUME"""
volume = engine.getProperty('volume')
engine.setProperty('volume',1.0)

"""VOICE"""
voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[0].id)
engine.setProperty('voice', voices[1].id)

# engine.say("test.test.test.")
# engine.runAndWait()
# engine.stop()


def text_to_speech(text):
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# """Saving Voice to a file"""
# engine.save_to_file('Hello World', 'test.mp3')
# engine.runAndWait()

