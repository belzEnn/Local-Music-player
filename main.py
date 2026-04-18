import sys
from PyQt5.QtWidgets import (
    QApplication, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QListWidget,
    QLabel, QFrame, QListWidgetItem
)
from PyQt5.QtCore import Qt
from basewindow import BaseWindow


class MusicApp(BaseWindow):
    def __init__(self) -> None:
        super().__init__("Music Library")

        self.playlists = []

        self.rootLayout.addWidget(self.initHeader())
        self.rootLayout.addWidget(self.initBody())

        self.loadPlaylists()

    # --- HEADER ---
    def initHeader(self):
        header = QFrame(self)
        header.setFixedHeight(50)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        self.searchInput = QLineEdit(self)
        self.searchInput.setPlaceholderText("Search...")
        self.searchInput.textChanged.connect(self.onSearchChanged)

        self.searchButton = QPushButton("Search", self)
        self.searchButton.clicked.connect(self.onSearchClicked)

        layout.addWidget(self.searchInput)
        layout.addWidget(self.searchButton)

        return header

    # --- BODY ---
    def initBody(self):
        body = QFrame(self)

        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        layout.addWidget(self.initSidebar())
        layout.addWidget(self.initContent())

        return body

    # --- SIDEBAR ---
    def initSidebar(self):
        sidebar = QFrame(self)
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self.playlistsLabel = QLabel("Playlists", sidebar)

        self.playlistListWidget = QListWidget(sidebar)
        self.playlistListWidget.itemClicked.connect(self.onPlaylistClicked)

        self.playlistListWidget.setSelectionMode(QListWidget.SingleSelection)
        self.playlistListWidget.setFocusPolicy(Qt.NoFocus)

        self.addPlaylistButton = QPushButton("Add playlist", sidebar)
        self.addPlaylistButton.clicked.connect(self.addPlaylist)

        layout.addWidget(self.playlistsLabel)
        layout.addWidget(self.playlistListWidget)
        layout.addWidget(self.addPlaylistButton)

        return sidebar

    # --- CONTENT ---
    def initContent(self):
        content = QFrame(self)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.contentTitle = QLabel("Main area", content)
        self.contentTitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.contentTitle)

        return content

    # --- LOGIC ---
    def loadPlaylists(self):
        self.playlistListWidget.clear()

        for name in self.playlists:
            item = QListWidgetItem(name)
            self.playlistListWidget.addItem(item)

        if self.playlists:
            self.playlistListWidget.setCurrentRow(0)
            self.contentTitle.setText(self.playlists[0])

    def addPlaylist(self):
        name = f"Playlist {len(self.playlists) + 1}"
        self.playlists.append(name)
        self.loadPlaylists()

    def onPlaylistClicked(self, item):
        self.contentTitle.setText(item.text())

    def onSearchClicked(self):
        query = self.searchInput.text().strip()
        if query:
            self.contentTitle.setText(f"Search: {query}")

    def onSearchChanged(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicApp()
    window.show()
    sys.exit(app.exec())