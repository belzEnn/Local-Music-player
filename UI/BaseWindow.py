from PyQt5.QtWidgets import QWidget, QVBoxLayout


class BaseWindow(QWidget):
    def __init__(self, title: str = "App") -> None:
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1000, 650)

        self.rootLayout = QVBoxLayout()
        self.setLayout(self.rootLayout)

        self.loadStyles()

    def loadStyles(self):
        try:
            with open("assets/style.css", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("style.css not found")