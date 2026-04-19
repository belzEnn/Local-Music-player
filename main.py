from PyQt5.QtWidgets import (
    QApplication, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QListWidget,
    QLabel, QFrame, QListWidgetItem, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt

import sys
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
        header.setFixedHeight(48) 
        header.setStyleSheet("background-color: transparent; border: none;")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 0, 15, 0) 

        searchContainer = QFrame()
        searchContainer.setObjectName("SearchContainer")
        searchLayout = QHBoxLayout(searchContainer)
        searchLayout.setContentsMargins(10, 0, 10, 0)
        searchLayout.setSpacing(8)

        searchIcon = QLabel()
        searchIcon.setPixmap(QPixmap("assets/images/search.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        searchIcon.setStyleSheet("border: none; background: transparent;")

        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("What do you want to play?")
        self.searchInput.setObjectName("SearchInput")
        
        searchLayout.addWidget(searchIcon)
        searchLayout.addWidget(self.searchInput)

        layout.addStretch(1) 
        layout.addWidget(searchContainer)
        layout.addStretch(1)

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
        sidebar.setFixedWidth(280)
        sidebar.setObjectName("SidebarFrame")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # --- HEADER САЙДБАРА ---
        libHeader = QWidget()
        libHeader.setObjectName("LibraryHeader")
        libHeaderLayout = QHBoxLayout(libHeader)
        libHeaderLayout.setContentsMargins(0, 0, 0, 0)

        self.playlistsLabel = QLabel("Your Library")
        self.playlistsLabel.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")

        # Кнопка "+" (иконка вместо текста)
        self.addPlaylistButton = QPushButton()
        self.addPlaylistButton.setIcon(QIcon("assets/images/plus.png"))
        self.addPlaylistButton.setIconSize(QSize(20, 20))
        self.addPlaylistButton.setCursor(Qt.PointingHandCursor)
        self.addPlaylistButton.setFixedSize(32, 32)
        self.addPlaylistButton.setObjectName("AddPlaylistBtn")
        self.addPlaylistButton.clicked.connect(self.addPlaylist)

        libHeaderLayout.addWidget(self.playlistsLabel)
        libHeaderLayout.addStretch()
        libHeaderLayout.addWidget(self.addPlaylistButton)

        self.playlistListWidget = QListWidget(sidebar)
        self.playlistListWidget.itemClicked.connect(self.onPlaylistClicked)
        self.playlistListWidget.setSelectionMode(QListWidget.SingleSelection)
        self.playlistListWidget.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(libHeader)
        layout.addWidget(self.playlistListWidget)
        
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