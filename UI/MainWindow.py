from PyQt5.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QListWidget, QLabel, 
    QFrame, QListWidgetItem, QWidget, 
    QDialog, QTableWidget, QTableWidgetItem, 
    QHeaderView, QStackedWidget, QSlider,
)
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QBrush
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from UI.BaseWindow import BaseWindow
from services.youtube import YoutubeService

class App(BaseWindow):
    def __init__(self) -> None:
        super().__init__("Music Library")
        
        self.current_track_start = 0
        self.current_track_end = 0

        self.service = YoutubeService()
        self.player = QMediaPlayer()
        
        self.playlists = []
        self.current_album_data = None

        self.rootLayout.addWidget(self.initHeader())
        self.rootLayout.addWidget(self.initBody())
        self.rootLayout.addWidget(self.initFooter())
        
        self.loadPlaylists()
        self.setupPlayerSignals()

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

    def initFooter(self):
            footer = QFrame(self)
            footer.setFixedHeight(80)
            footer.setObjectName("PlayerBar")
            
            layout = QHBoxLayout(footer)
            layout.setContentsMargins(20, 0, 20, 0)
            layout.setSpacing(20)

            # play/pause
            self.playBtn = QPushButton()
            self.playBtn.setObjectName("PlayBtn") # Даем имя для CSS
            self.playBtn.setIcon(QIcon("assets/images/play.png")) 
            self.playBtn.setIconSize(QSize(32, 32))
            self.playBtn.setFixedSize(40, 40)
            self.playBtn.setCursor(Qt.PointingHandCursor)
            self.playBtn.clicked.connect(self.togglePlay)

            # rewind
            self.progressSlider = QSlider(Qt.Horizontal)
            self.progressSlider.setObjectName("ProgressSlider")
            self.progressSlider.sliderMoved.connect(self.seekPosition)

            # volume
            volumeIcon = QLabel()
            volumeIcon.setPixmap(QPixmap("assets/images/volume.png").scaled(18, 18, Qt.KeepAspectRatio))
            
            self.volumeSlider = QSlider(Qt.Horizontal)
            self.volumeSlider.setFixedWidth(100)
            self.volumeSlider.setRange(0, 100)
            self.volumeSlider.setValue(70)
            self.player.setVolume(70)
            self.volumeSlider.valueChanged.connect(self.player.setVolume)

            layout.addWidget(self.playBtn)
            layout.addWidget(self.progressSlider)
            layout.addWidget(volumeIcon)
            layout.addWidget(self.volumeSlider)

            return footer

    # --- CONTENT ---
    def initContent(self):
        self.contentStack = QStackedWidget()

        self.mainAreaPage = QFrame()
        ma_layout = QVBoxLayout(self.mainAreaPage)
        self.contentTitle = QLabel("Select a playlist or search for music")
        self.contentTitle.setAlignment(Qt.AlignCenter)
        ma_layout.addWidget(self.contentTitle)

        self.searchResultsPage = QListWidget()
        self.searchResultsPage.setObjectName("SearchResultsPage")
        self.searchResultsPage.itemClicked.connect(self.onAlbumSelected)

        self.albumPage = QFrame()
        self.albumPage.setObjectName("AlbumPage")
        album_layout = QVBoxLayout(self.albumPage)
        album_layout.setContentsMargins(30, 20, 30, 0)

        # ХЕЕР АЛЬБОМА (Обложка + Инфо)
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 20)
        header_layout.setSpacing(25)

        self.bigCoverLabel = QLabel()
        self.bigCoverLabel.setFixedSize(180, 180)
        self.bigCoverLabel.setScaledContents(True)

        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignBottom)
        
        type_label = QLabel("ALBUM")
        type_label.setStyleSheet("color: #b3b3b3; font-size: 12px; font-weight: bold;")
        
        self.albumHeaderTitle = QLabel("Album Title")
        self.albumHeaderTitle.setObjectName("AlbumTitleLabel")
        
        self.albumHeaderArtist = QLabel("Artist Name")
        self.albumHeaderArtist.setObjectName("AlbumArtistLabel")

        info_layout.addWidget(type_label)
        info_layout.addWidget(self.albumHeaderTitle)
        info_layout.addWidget(self.albumHeaderArtist)

        header_layout.addWidget(self.bigCoverLabel)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()

        self.trackTable = QTableWidget(0, 3)
        self.trackTable.setHorizontalHeaderLabels(["#", "TITLE", "START"])
        self.trackTable.setShowGrid(False)
        self.trackTable.setAlternatingRowColors(False)
        self.trackTable.setSelectionBehavior(self.trackTable.SelectRows) 
        self.trackTable.setEditTriggers(self.trackTable.NoEditTriggers)
        self.trackTable.verticalHeader().setVisible(False)
        self.trackTable.horizontalHeader().setStretchLastSection(True)
        self.trackTable.verticalHeader().setDefaultSectionSize(34)
        self.trackTable.setColumnWidth(0, 50)
        self.trackTable.setColumnWidth(2, 110)

        self.trackTable.itemDoubleClicked.connect(self.onTrackDoubleClicked)

        h_header = self.trackTable.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.Fixed)
        h_header.setSectionResizeMode(1, QHeaderView.Stretch)
        h_header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.trackTable.setColumnWidth(0, 50)
        self.trackTable.setColumnWidth(2, 100)

        album_layout.addWidget(header_widget)
        album_layout.addWidget(self.trackTable)

        # Добавляем страницы в стек
        self.contentStack.addWidget(self.mainAreaPage)      # Index 0
        self.contentStack.addWidget(self.searchResultsPage) # Index 1
        self.contentStack.addWidget(self.albumPage)         # Index 2
        
        return self.contentStack

    # --- LOGIC ---
    def onSearchChanged(self, text):
        if not text.strip():
            self.contentStack.setCurrentIndex(0)
            return
            
        results = self.service.search(text)
        self.searchResultsPage.clear()

        self.searchResultsPage.setViewMode(QListWidget.IconMode)
        self.searchResultsPage.setIconSize(QSize(160, 160))
        self.searchResultsPage.setResizeMode(QListWidget.Adjust)
        self.searchResultsPage.setSpacing(20)
        self.searchResultsPage.setStyleSheet("QListWidget::item { color: white; font-weight: bold; }")
        
        self.contentStack.setCurrentIndex(1)
        
        for album in results:
            cover_path = self.service.get_cover_path(album['id'], album.get('cover_url'))

            icon = QIcon(cover_path)
            display_text = f"{album['title']}\n{album['artist']}"
            
            item = QListWidgetItem(icon, display_text)
            item.setSizeHint(QSize(180, 220)) # Размер карточки
            item.setTextAlignment(Qt.AlignCenter)
            item.setData(Qt.UserRole, album)
            
            self.searchResultsPage.addItem(item)

    def onAlbumSelected(self, item):
        album = item.data(Qt.UserRole)
        self.current_album_data = album
        
        # 1. Заполняем инфо в хедере
        self.albumHeaderTitle.setText(album['title'])
        self.albumHeaderArtist.setText(album['artist'])
        
        # 2. Грузим обложку (используем наш сервис)
        cover_path = self.service.get_cover_path(album['id'], album.get('cover_url'))
        self.bigCoverLabel.setPixmap(QPixmap(cover_path))
        
        # 3. Заполняем таблицу треков
        self.trackTable.setRowCount(0)
        for i, track in enumerate(album['tracks'], start=1):
            row = self.trackTable.rowCount()
            self.trackTable.insertRow(row)
            
            # Колонка №
            num_item = QTableWidgetItem(str(i))
            num_item.setTextAlignment(Qt.AlignCenter)
            
            # Колонка Название
            title_item = QTableWidgetItem(track['title'])
            title_item.setForeground(QBrush(Qt.white))
            
            # Колонка Время
            time_item = QTableWidgetItem(track['start'])
            time_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            self.trackTable.setItem(row, 0, num_item)
            self.trackTable.setItem(row, 1, title_item)
            self.trackTable.setItem(row, 2, time_item)
        
        self.contentStack.setCurrentIndex(2)

    def onTrackDoubleClicked(self, item):
            row = item.row()
            track = self.current_album_data['tracks'][row]

            self.current_track_start, self.current_track_end = self.service.get_track_time_range(
                self.current_album_data, row
            )
            
            path = self.service.prepare_and_get_path(
                self.current_album_data['id'], 
                self.current_album_data['youtube_url'],
                self.current_album_data['title']
            )
            
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.player.play()
            self.player.setPosition(self.current_track_start)
            
            if self.current_track_end != -1:
                duration = self.current_track_end - self.current_track_start
                self.progressSlider.setRange(0, duration)

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

    def setupPlayerSignals(self):
        self.player.positionChanged.connect(self.updatePosition)
        self.player.durationChanged.connect(self.updateDuration)

        self.player.stateChanged.connect(self.updatePlayButtonIcon)

    def togglePlay(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def updatePlayButtonIcon(self, state):
        icon_path = "assets/images/pause.png" if state == QMediaPlayer.PlayingState else "assets/images/play.png"
        self.playBtn.setIcon(QIcon(icon_path))

    def updatePosition(self, position):
        if not self.progressSlider.isSliderDown():
            self.progressSlider.setValue(position)

    def updateDuration(self, duration):
            if self.current_track_end == -1:
                self.current_track_end = duration
                track_duration = self.current_track_end - self.current_track_start
                self.progressSlider.setRange(0, track_duration)
    def updatePosition(self, position):
        if self.current_track_end != -1 and position >= self.current_track_end:
            self.player.pause()
            self.player.setPosition(self.current_track_start) 
            return

        local_pos = position - self.current_track_start
        
        if not self.progressSlider.isSliderDown():
            self.progressSlider.setValue(max(0, local_pos))

    def seekPosition(self, position):
        global_pos = self.current_track_start + position
        self.player.setPosition(global_pos)

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