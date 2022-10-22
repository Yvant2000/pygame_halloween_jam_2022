from abc import ABC, abstractmethod

from scripts.text import TEXT
from scripts.utils import distance


class Interaction(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @abstractmethod
    def can_interact(self, player) -> bool:
        """Test if there is an interaction with the player."""
        ...

    @abstractmethod
    def interact(self, player):
        """Interact with the player."""
        ...

    @abstractmethod
    def update(self):
        """Update the interation each frame."""
        ...


class Test_Interaction(Interaction):
    def __init__(self, pos):
        self.pos = pos

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos) and distance(player.pos, self.pos) < 3:
            TEXT.replace("see the test interaction", duration=0.1, fade_out=0.0)
            return True
        return False

    def interact(self, player):
        print("interact with the test interaction")

    def update(self):
        ...
