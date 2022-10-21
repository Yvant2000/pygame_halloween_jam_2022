from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""

from scripts.game import GAME

if __name__ == '__main__':
    GAME.main()
