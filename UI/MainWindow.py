from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QListWidget, QLabel, 
    QFrame, QListWidgetItem, QWidget, 
    QDialog, QTableWidget, QTableWidgetItem, 
    QHeaderView, QStackedWidget,
)
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from UI.BaseWindow import BaseWindow
from services.youtube import YoutubeService

class App(BaseWindow):
    def __init__(self) -> None:
        super().__init__("Music Library")
        
        self.service = YoutubeService()
        self.player = QMediaPlayer()
        
        self.playlists = []
        self.current_album_data = None

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
        s_layout = QHBoxLayout(searchContainer)
        s_layout.setContentsMargins(10, 0, 10, 0)

        searchIcon = QLabel()
        searchIcon.setPixmap(QPixmap("assets/images/search.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("What do you want to play?")
        self.searchInput.setObjectName("SearchInput")
        self.searchInput.textChanged.connect(self.onSearchChanged)

        s_layout.addWidget(searchIcon)
        s_layout.addWidget(self.searchInput)
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

        libHeader = QWidget()
        libHeader.setObjectName("LibraryHeader")
        lh_layout = QHBoxLayout(libHeader)
        lh_layout.setContentsMargins(0, 0, 0, 0)

        self.playlistsLabel = QLabel("Your Library")
        self.playlistsLabel.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")

        self.addPlaylistButton = QPushButton()
        self.addPlaylistButton.setIcon(QIcon("assets/images/plus.png"))
        self.addPlaylistButton.setFixedSize(32, 32)
        self.addPlaylistButton.setObjectName("AddPlaylistBtn")
        self.addPlaylistButton.clicked.connect(self.addPlaylist)

        lh_layout.addWidget(self.playlistsLabel)
        lh_layout.addStretch()
        lh_layout.addWidget(self.addPlaylistButton)

        self.playlistListWidget = QListWidget()
        self.playlistListWidget.itemClicked.connect(self.onPlaylistClicked)

        layout.addWidget(libHeader)
        layout.addWidget(self.playlistListWidget)
        return sidebar

    # --- CONTENT ---
    def initContent(self):
        self.contentStack = QStackedWidget()
        
        # 1. Заглушка
        self.mainAreaPage = QFrame()
        ma_layout = QVBoxLayout(self.mainAreaPage)
        self.contentTitle = QLabel("Select a playlist or search for music")
        self.contentTitle.setAlignment(Qt.AlignCenter)
        ma_layout.addWidget(self.contentTitle)

        # 2. Результаты поиска
        self.searchResultsPage = QListWidget()
        self.searchResultsPage.itemClicked.connect(self.onAlbumSelected)

        # 3. Список треков
        self.albumPage = QFrame()
        album_layout = QVBoxLayout(self.albumPage)
        self.albumHeaderTitle = QLabel("Album Title")
        self.albumHeaderTitle.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        
        self.trackTable = QTableWidget(0, 2)
        self.trackTable.setHorizontalHeaderLabels(["Title", "Start"])
        self.trackTable.itemDoubleClicked.connect(self.onTrackDoubleClicked)
        self.trackTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        album_layout.addWidget(self.albumHeaderTitle)
        album_layout.addWidget(self.trackTable)

        self.contentStack.addWidget(self.mainAreaPage)
        self.contentStack.addWidget(self.searchResultsPage)
        self.contentStack.addWidget(self.albumPage)
        return self.contentStack

    # --- LOGIC ---
    def onSearchChanged(self, text):
        if not text.strip():
            self.contentStack.setCurrentIndex(0)
            return
            
        results = self.service.search(text)
        self.searchResultsPage.clear()
        self.contentStack.setCurrentIndex(1)
        
        for album in results:
            item = QListWidgetItem(f"{album['artist']} — {album['title']}")
            item.setData(Qt.UserRole, album)
            self.searchResultsPage.addItem(item)

    def onAlbumSelected(self, item):
        album = item.data(Qt.UserRole)
        self.current_album_data = album
        self.albumHeaderTitle.setText(f"{album['artist']} - {album['title']}")
        
        self.trackTable.setRowCount(0)
        for track in album['tracks']:
            row = self.trackTable.rowCount()
            self.trackTable.insertRow(row)
            self.trackTable.setItem(row, 0, QTableWidgetItem(track['title']))
            self.trackTable.setItem(row, 1, QTableWidgetItem(track['start']))
        
        self.contentStack.setCurrentIndex(2)

    def onTrackDoubleClicked(self, item):
        track = self.current_album_data['tracks'][item.row()]
        
        path = self.service.prepare_and_get_path(
            self.current_album_data['id'], 
            self.current_album_data['youtube_url'],
            self.current_album_data['title']
        )
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.player.play()
        self.player.setPosition(self.service.timestamp_to_ms(track['start']))

    def loadPlaylists(self):
        self.playlistListWidget.clear()
        for name in self.playlists:
            self.playlistListWidget.addItem(QListWidgetItem(name))

    def addPlaylist(self):
        dialog = CreatePlaylist("New Playlist", "Playlist Name", self)
        if dialog.exec_():
            name = dialog.get_text()
            if name.strip():
                self.playlists.append(name.strip())
                self.loadPlaylists()

    def onPlaylistClicked(self, item):
        self.contentStack.setCurrentIndex(0)
        self.contentTitle.setText(item.text())

# Класс CreatePlaylist (твой оригинальный)
class CreatePlaylist(QDialog):
    def __init__(self, title, label_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 180)

        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter playlist name...")

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Create")
        self.cancel_btn = QPushButton("Cancel")

        self.ok_btn.setObjectName("DialogOkBtn")
        self.cancel_btn.setObjectName("DialogCancelBtn")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)

        layout.addWidget(self.input)
        layout.addLayout(btn_layout)

    def get_text(self):
        return self.input.text()