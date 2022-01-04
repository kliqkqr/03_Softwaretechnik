from abc import ABC, abstractmethod


class Tool(ABC):

    def __init__(self, win, frame):
        self.win = win
        self.frame = frame

        self.drawView()

    @abstractmethod
    def drawView(self):
        pass

