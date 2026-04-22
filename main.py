import sys
from PyQt5.QtWidgets import QApplication
from UI.MainWindow import App

def main():
    app = QApplication(sys.argv)

    window = App()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()