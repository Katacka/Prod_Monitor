from dataclasses import dataclass
from typing import Optional

import speech_recognition as sr
from playsound import playsound


@dataclass
class Sound:
    record_sound: str = "record_sound.mp3"
    success_sound: str = "success_sound.mp3"
    error_sound: str = "error.mp3"


class SpeechHandler:
    """
    TODO
      - Suppress ALSA/jackShm warnings
      - Reduce mic activation delays
        - Reduce audio file IO overhead
    """

    def __init__(self, sound: Sound = Sound()):
        # Config params
        self.record_sound = f"sound_effects/{sound.record_sound}"
        self.success_sound = f"sound_effects/{sound.success_sound}"
        self.error_sound = f"sound_effects/{sound.error_sound}"

        # Voice to text setup
        self.rec = sr.Recognizer()
        self.__setup_mic()

    def __setup_mic(self) -> None:
        """Creates a speech_recognition mic object for the purpose of capturing audio"""
        self.mic = sr.Microphone()

    def transcribe_input(self) -> Optional[str]:
        """Uses {self.mic} to transcribe audio input"""
        with self.mic as source:
            self.rec.adjust_for_ambient_noise(source, duration=0.5)
            playsound(self.record_sound)
            audio = self.rec.listen(source)

        try:
            parsed_text = self.rec.recognize_google(audio)
            playsound(self.success_sound)
            return parsed_text
        except sr.UnknownValueError:
            playsound(self.error_sound)
            return None
