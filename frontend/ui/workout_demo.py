"""
Workout Demo Screen (LOCAL ASSETS)
✅ MP4 video preview (from frontend/assets)
✅ GIF + Image preview (png/jpg)
✅ Play/Pause button (Qt standard icons) + Seek bar + time labels
✅ Controls are ALWAYS visible (not clipped/hidden)
✅ Auto-pause when screen is hidden / closed / back
✅ Dark styled QMessageBox + QDialog (NO white background behind text)
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QDialog, QMessageBox,
    QSizePolicy, QSlider, QStyle
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QFont, QMovie, QPixmap

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from backend.models import data_manager


# ==================================================
# Main WorkoutDemo Screen
# ==================================================
class WorkoutDemo(QWidget):
    """Exercise preview screen with local asset preview + instructions"""

    ASSET_MAP = {
        "squats": "Squats.mp4",
        "push ups": "Push ups.mp4",
        "crunches": "Crunches.mp4",
        "jumping jacks": "Jumping jacks.mp4",
        "cobra stretch": "Cobra Stretch.png",
        "plank": "Plank.mp4",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_workout_id = None

        # GIF
        self.movie = None

        # Video
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)

        # Seek state
        self.is_seeking = False

        self.init_ui()
        self.hook_player_signals()

    # ==================================================
    # ✅ Dark styles (UPDATED: white border for buttons)
    # ==================================================
    def _apply_dark_msgbox_style(self, msg: QMessageBox):
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #0f0f10;
                border: 1px solid #2a2a2a;
                border-radius: 10px;
                font-family: Segoe UI;
            }

            QLabel {
                color: #ffffff;
                font-size: 16px;
                background: transparent;
            }

            QPushButton {
                background: transparent;
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                padding: 4px 16px;     /* ⬅ compact */
                min-width: 64px;
                          
                border: 1px solid rgba(255,255,255,0.75);   /* ✅ WHITE BORDER */
                border-radius: 8px;
            }

            QPushButton:hover {
                background: rgba(255,255,255,0.12);
                color: #ffffff;
            }

            QPushButton:pressed {
                background: rgba(255,255,255,0.20);
                color: #ffffff;
            }
        """)

    def _apply_dark_dialog_style(self, dialog: QDialog):
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0f0f10;
                border: 1px solid #2a2a2a;
                border-radius: 10px;
                font-family: Segoe UI;
            }

            QLabel {
                color: #ffffff;
                font-size: 14px;
                background: transparent;
            }

            QPushButton {
                background: transparent;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                min-width: 70px;        /* ⬅ smaller */
                min-height: 30px;
                padding: 4px 14px;    

                border: 1px solid rgba(255,255,255,0.75);   /* ✅ WHITE BORDER */
                border-radius: 6px;
            }

            QPushButton:hover {
                background: rgba(255,255,255,0.12);
                color: #ffffff;
            }

            QPushButton:pressed {
                background: rgba(255,255,255,0.20);
                color: #ffffff;
            }
        """)

    # ==================================================
    # Auto pause on screen change / close
    # ==================================================
    def hideEvent(self, event):
        if self.player:
            self.player.pause()
        super().hideEvent(event)

    def closeEvent(self, event):
        if self.player:
            self.player.pause()
        super().closeEvent(event)

    # ==================================================
    # Helper: show dark styled message box
    # ==================================================
    def show_dialog(self, title: str, message: str, icon=QMessageBox.Icon.Information):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        self._apply_dark_msgbox_style(msg)
        msg.exec()

    # ==================================================
    def init_ui(self):
        self.setStyleSheet("background:#f4f6fb;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # ================= Back Button =================
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setMaximumWidth(220)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ffffff;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover { color: #667eea; }
        """)
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn)

        # ================= Title =================
        self.title_label = QLabel("Workout Demo")
        self.title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #ffffff;
                font-size: 32px;
                font-weight: bold;
            }
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        # ================= Content Layout =================
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)

        # ================= Preview Section =================
        preview_container = QFrame()
        preview_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dddddd;
                border-radius: 16px;
            }
        """)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        preview_layout.setSpacing(12)

        # --- Image/GIF label ---
        self.preview_label = QLabel("No Preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(420, 360)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_label.setStyleSheet("""
            QLabel {
                background: black;
                color: white;
                border-radius: 10px;
            }
        """)

        # --- Video widget ---
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(420, 360)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setStyleSheet("background: black; border-radius: 10px;")
        self.video_widget.hide()

        self.player.setVideoOutput(self.video_widget)

        # --- Controls container ---
        self.controls_container = QFrame()
        self.controls_container.setFixedHeight(60)
        self.controls_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.controls_container.setStyleSheet("""
            QFrame {
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
        """)
        controls_outer = QVBoxLayout(self.controls_container)
        controls_outer.setContentsMargins(12, 10, 12, 10)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)

        # Play/Pause button
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(44, 34)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.icon_play = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.icon_pause = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)

        self.play_btn.setIcon(self.icon_play)
        self.play_btn.setIconSize(QSize(18, 18))

        self.play_btn.setStyleSheet("""
            QPushButton {
                background: #667eea;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background: #764ba2; }
        """)
        self.play_btn.clicked.connect(self.toggle_play_pause)

        self.current_time_lbl = QLabel("00:00")
        self.current_time_lbl.setStyleSheet("color:#111827; font-size:12px;")

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.seek_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #e5e7eb;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #667eea;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
                background: #764ba2;
            }
        """)
        self.seek_slider.sliderPressed.connect(self.on_seek_pressed)
        self.seek_slider.sliderReleased.connect(self.on_seek_released)
        self.seek_slider.sliderMoved.connect(self.on_seek_moved)

        self.total_time_lbl = QLabel("00:00")
        self.total_time_lbl.setStyleSheet("color:#111827; font-size:12px;")

        controls_row.addWidget(self.play_btn)
        controls_row.addWidget(self.current_time_lbl)
        controls_row.addWidget(self.seek_slider, 1)
        controls_row.addWidget(self.total_time_lbl)

        controls_outer.addLayout(controls_row)
        self.controls_container.hide()

        preview_layout.addWidget(self.preview_label, 1)
        preview_layout.addWidget(self.video_widget, 1)
        preview_layout.addWidget(self.controls_container, 0)

        content_layout.addWidget(preview_container, 2)

        # ================= Info Section =================
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dddddd;
                border-radius: 16px;
            }
        """)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(25, 25, 25, 25)
        info_layout.setSpacing(20)

        details_label = QLabel("Workout Name")
        details_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        details_label.setStyleSheet("color:#667eea;")
        info_layout.addWidget(details_label)

        self.muscles_label = QLabel()
        self.muscles_label.setFont(QFont("Segoe UI", 14))
        self.muscles_label.setStyleSheet("color:#333333;")
        self.muscles_label.setWordWrap(True)
        info_layout.addWidget(self.muscles_label)

        instructions_header = QLabel("Instructions")
        instructions_header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        instructions_header.setStyleSheet("color:#667eea;")
        info_layout.addWidget(instructions_header)

        self.instructions_text = QTextEdit()
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setMinimumHeight(200)
        self.instructions_text.setStyleSheet("""
            QTextEdit {
                background: #f9f9f9;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                color: #333333;
                font-size: 13px;
            }
        """)
        info_layout.addWidget(self.instructions_text)

        info_layout.addStretch()
        content_layout.addWidget(info_container, 1)

        main_layout.addLayout(content_layout)

        # ================= Start Button =================
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.start_btn = QPushButton("Start Workout")
        self.start_btn.setMinimumSize(300, 50)
        self.start_btn.setMaximumSize(400, 70)
        self.start_btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.start_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                       stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                       stop:0 #764ba2, stop:1 #667eea);
            }
        """)
        self.start_btn.clicked.connect(self.start_workout)

        button_layout.addStretch()
        button_layout.addWidget(self.start_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    # ==================================================
    def hook_player_signals(self):
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.playbackStateChanged.connect(self.on_playback_state_changed)

    # ==================================================
    def assets_path(self, filename: str) -> str:
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(frontend_dir, "assets", filename)

    @staticmethod
    def normalize_name(name: str) -> str:
        return " ".join(name.strip().lower().split())

    # ==================================================
    def load_workout(self, workout_id):
        self.current_workout_id = workout_id

        try:
            row = data_manager.get_workout_by_id(workout_id)
        except Exception as e:
            self.show_dialog("Database Error", str(e), QMessageBox.Icon.Critical)
            return

        if not row:
            self.show_dialog("Not Found", "Workout not found", QMessageBox.Icon.Warning)
            return

        workout_name, _, description = row

        self.title_label.setText(workout_name)
        self.muscles_label.setText(workout_name)
        self.instructions_text.setText(description or "No instructions available.")

        self.preview_asset(workout_name)

    # ==================================================
    def stop_preview(self):
        # Stop GIF
        if self.movie:
            self.movie.stop()
            self.movie = None

        # Stop video
        self.player.pause()
        self.player.setSource(QUrl())

        # Reset controls
        self.controls_container.hide()
        self.play_btn.setIcon(self.icon_play)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.setValue(0)
        self.current_time_lbl.setText("00:00")
        self.total_time_lbl.setText("00:00")

        # Reset UI
        self.video_widget.hide()
        self.preview_label.show()
        self.preview_label.setText("No Preview")
        self.preview_label.setPixmap(QPixmap())

    # ==================================================
    def preview_asset(self, workout_name: str):
        key = self.normalize_name(workout_name)
        filename = self.ASSET_MAP.get(key)

        if not filename:
            self.stop_preview()
            self.preview_label.setText("No Preview Available")
            return

        path = self.assets_path(filename)

        if not os.path.exists(path):
            self.stop_preview()
            self.preview_label.setText(f"File Not Found: {filename}")
            return

        ext = os.path.splitext(filename)[1].lower()

        if ext == ".mp4":
            self.play_video(path)
        elif ext == ".gif":
            self.play_gif(path)
        elif ext in (".png", ".jpg", ".jpeg"):
            self.show_image(path)
        else:
            self.stop_preview()
            self.preview_label.setText("Unsupported Preview Type")

    # ==================================================
    def play_video(self, video_path: str):
        self.stop_preview()

        self.preview_label.hide()
        self.video_widget.show()

        self.controls_container.show()
        self.controls_container.raise_()
        self.controls_container.repaint()

        self.player.setSource(QUrl.fromLocalFile(video_path))
        self.player.play()

    def play_gif(self, gif_path: str):
        self.stop_preview()
        self.controls_container.hide()

        self.movie = QMovie(gif_path)
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.movie.setScaledSize(self.preview_label.size())
        self.preview_label.setMovie(self.movie)
        self.movie.start()

    def show_image(self, img_path: str):
        self.stop_preview()
        self.controls_container.hide()

        pix = QPixmap(img_path)
        if pix.isNull():
            self.preview_label.setText("Image Load Failed")
            return

        self.preview_label.setPixmap(
            pix.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    # ==================================================
    # Controls
    # ==================================================
    def toggle_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setIcon(self.icon_pause)
        else:
            self.play_btn.setIcon(self.icon_play)

    def on_duration_changed(self, duration_ms: int):
        self.seek_slider.setRange(0, max(0, duration_ms))
        self.total_time_lbl.setText(self.format_ms(duration_ms))

    def on_position_changed(self, pos_ms: int):
        if not self.is_seeking:
            self.seek_slider.setValue(pos_ms)
        self.current_time_lbl.setText(self.format_ms(pos_ms))

    def on_seek_pressed(self):
        self.is_seeking = True

    def on_seek_moved(self, value: int):
        self.current_time_lbl.setText(self.format_ms(value))

    def on_seek_released(self):
        self.player.setPosition(self.seek_slider.value())
        self.is_seeking = False

    @staticmethod
    def format_ms(ms: int) -> str:
        total_seconds = max(0, ms // 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    # ==================================================
    def start_workout(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Camera Permission")
        dialog.setFixedSize(420, 190)

        # ✅ Apply dark dialog style (with white-bordered buttons)
        self._apply_dark_dialog_style(dialog)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        label = QLabel("This workout requires access to your camera.\nDo you want to allow camera access?")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
        button_layout.addStretch()
        button_layout.addWidget(yes_btn)
        button_layout.addWidget(no_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        def on_yes():
            dialog.accept()
            self.open_camera_screen()

        def on_no():
            dialog.reject()
            self.show_dialog("Permission Denied", "Camera access denied. Cannot start workout.", QMessageBox.Icon.Critical)

        yes_btn.clicked.connect(on_yes)
        no_btn.clicked.connect(on_no)

        dialog.exec()

    # ==================================================
    def open_camera_screen(self):
        main_win = self.window()
        if hasattr(main_win, "show_workout_session"):
            main_win.show_workout_session(self.current_workout_id)

    # ==================================================
    def go_back(self):
        self.player.pause()
        self.stop_preview()

        main_win = self.window()
        if hasattr(main_win, "back_to_dashboard_from_demo"):
            main_win.back_to_dashboard_from_demo()
