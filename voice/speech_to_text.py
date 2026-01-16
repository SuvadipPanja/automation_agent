import speech_recognition as sr


class SpeechToText:
    """
    Converts microphone input to text.
    """

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self) -> str:
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise RuntimeError(f"Speech service error: {e}")
