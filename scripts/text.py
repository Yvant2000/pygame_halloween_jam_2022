from pygame import Surface
from pygame.font import Font


from scripts.display import DISPLAY


class TextMessage:
    def __init__(self, text, duration: float = 5., fade_out: float = 1.0,
                 font: str = "PressStart2P", color: tuple[int, int, int] = (255, 255, 255), size: int = 16,
                 y: int = 330,
                 force: bool = False):
        self.duration: float = duration
        self.fade_out: float = fade_out

        font_: Font = Font(f"data/fonts/{font}.ttf", size)

        self._surfaces: list[Surface] = []
        for line in text.split("\n"):
            if line:
                s = font_.render(line, True, color)
                self._surfaces.append(s)
                y -= s.get_height() + 2

        self.y: int = y

        self.force: bool = force

    def display(self, surface: Surface) -> bool:
        """Display the text message on the given surface.
        return True when the text isn't displayed anymore"""

        alpha = 255
        if self.duration <= 0:
            if self.duration <= -self.fade_out:
                return True
            alpha = int((1 + self.duration / self.fade_out) * 255)
            # self._surface.set_alpha(int((1 + self.duration / self.fade_out) * 255))

        y = self.y

        for image in self._surfaces:
            image.set_alpha(alpha)
            surface.blit(image, (DISPLAY.screen_size[0]//2 - image.get_width()//2, y))
            y += image.get_height() + 2

        self.duration -= DISPLAY.delta_time

        return False


class TEXT:
    text_list: list[TextMessage] = []

    @classmethod
    def add(cls, text: str, *args, **kwargs):
        cls.text_list.append(TextMessage(text, *args, **kwargs))

    @classmethod
    def replace(cls, text: str, *args, **kwargs):
        if cls.text_list and cls.text_list[0].force:
            return

        cls.text_list.clear()
        cls.add(text, *args, **kwargs)

    @classmethod
    def update(cls):

        if not cls.text_list:
            return

        if cls.text_list[0].display(DISPLAY.screen):
            cls.text_list.pop(0)
