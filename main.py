import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QLabel, QFrame, QSizePolicy
from PyQt5.QtCore import Qt


class MusicApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Music Library")
        self.resize(1000, 650)

        self.playlists = []

        layout = QVBoxLayout()
        layout.addLayout(self.initHeaderLayout())
        layout.addLayout(self.initMainLayout())
        self.setLayout(layout)

        self.loadPlaylists()

    def initHeaderLayout(self) -> QHBoxLayout:
        headerLayout = QHBoxLayout()

        self.searchInput = QLineEdit(self)
        self.searchInput.setPlaceholderText("Search...")
        self.searchInput.textChanged.connect(self.onSearchChanged)

        self.searchButton = QPushButton("Search", self)
        self.searchButton.clicked.connect(self.onSearchClicked)

        headerLayout.addWidget(self.searchInput)
        headerLayout.addWidget(self.searchButton)

        return headerLayout

    def initMainLayout(self) -> QHBoxLayout:
        mainLayout = QHBoxLayout()

        self.sidebarFrame = QFrame(self)
        self.sidebarFrame.setFrameShape(QFrame.StyledPanel)
        sidebarLayout = QVBoxLayout(self.sidebarFrame)

        self.playlistsLabel = QLabel("Playlists", self.sidebarFrame)
        self.playlistListWidget = QListWidget(self.sidebarFrame)
        self.playlistListWidget.itemClicked.connect(self.onPlaylistClicked)

        self.addPlaylistButton = QPushButton("Add playlist", self.sidebarFrame)
        self.addPlaylistButton.clicked.connect(self.addPlaylist)

        sidebarLayout.addWidget(self.playlistsLabel)
        sidebarLayout.addWidget(self.playlistListWidget)
        sidebarLayout.addWidget(self.addPlaylistButton)

        self.contentFrame = QFrame(self)
        self.contentFrame.setFrameShape(QFrame.StyledPanel)
        contentLayout = QVBoxLayout(self.contentFrame)

        self.contentTitle = QLabel("Main area", self.contentFrame)
        self.contentTitle.setAlignment(Qt.AlignCenter)

        contentLayout.addWidget(self.contentTitle)

        mainLayout.addWidget(self.sidebarFrame, 1)
        mainLayout.addWidget(self.contentFrame, 3)

        return mainLayout

    def loadPlaylists(self):
        ...

    def addPlaylist(self):
        ...

    def onPlaylistClicked(self):
        ...

    def onSearchClicked(self):
        ...

    def onSearchChanged(self):
        ...


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicApp()
    window.show()
    sys.exit(app.exec())