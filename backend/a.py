from typing import Protocol

class Speaker(Protocol):
    def speak(self) -> str:
        ...

class EnglishSpeaker:
    def speak(self) -> str:
        return "Hello!"

class FrenchSpeaker:
    def speak(self) -> str:
        return "Bonjour!"

def greet(speaker: Speaker) -> None:
    print(speaker.speak())

# Both EnglishSpeaker and FrenchSpeaker are subtypes of Speaker
# because they implement the speak method

eng_speaker = EnglishSpeaker()
fr_speaker = FrenchSpeaker()

# We can pass instances of EnglishSpeaker and FrenchSpeaker to greet
greet(eng_speaker)  # Output: Hello!
greet(fr_speaker)   # Output: Bonjour!
