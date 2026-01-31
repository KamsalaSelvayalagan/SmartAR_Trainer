"""
Exercise Preview Screen with GIF preview and start button
Integrated with SQLite database
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QMessageBox, QDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QMovie

# Import data manager
from backend.models import data_manager


class WorkoutDemo(QWidget):
    """Exercise preview screen with GIF and instructions"""

    # 🔁 Exercise name → GIF file mapping
    GIF_MAP = {
        "squats": "Squats.gif",
        "push ups": "Push ups.gif",
        "crunches": "Crunches.gif",
        "jumping jacks": "Jumping jacks.gif",
        "cobra stretch": "Cobra Stretch.gif",
        "plank": "Plank.gif"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_workout_id = None
        self.movie = None
        self.init_ui()

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
            QPushButton:hover {
                color: #667eea;
            }
        """)
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn)

        # ================= Title =================
        self.title_label = QLabel("Workout Demo")
        # self.title_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
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

        # ================= GIF Section =================
        video_container = QFrame()
        video_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #dddddd;
                border-radius: 16px;
            }
        """)
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(20, 20, 20, 20)

        self.gif_label = QLabel("No Preview")
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setMinimumSize(420, 420)
        self.gif_label.setStyleSheet("""
            QLabel {
                background: black;
                color: white;
                border-radius: 10px;
            }
        """)

        video_layout.addWidget(self.gif_label)
        content_layout.addWidget(video_container, 2)

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

        # ================= Buttons =================
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.start_btn = QPushButton("Start Workout")
        self.start_btn.setMinimumSize(300, 50)  # smallest size it can shrink to
        self.start_btn.setMaximumSize(400, 70)  # largest size it can grow to
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
    def load_workout(self, workout_id):
        """Load workout from database"""
        self.current_workout_id = workout_id

        try:
            row = data_manager.get_workout_by_id(workout_id)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return

        if not row:
            QMessageBox.warning(self, "Not Found", "Workout not found")
            return

        workout_name, _, description = row

        self.title_label.setText(workout_name)
        self.muscles_label.setText(workout_name)
        self.instructions_text.setText(description or "No instructions available.")

        self.preview_gif(workout_name)

    # ==================================================
    def preview_gif(self, workout_name):
        key = workout_name.strip().lower()
        gif_file = self.GIF_MAP.get(key)

        if not gif_file:
            self.gif_label.setText("No Preview Available")
            return

        self.load_gif(gif_file)

    # ==================================================
    def load_gif(self, gif_name):
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        gif_path = os.path.join(frontend_dir, "assets", gif_name)


        if not os.path.exists(gif_path):
            self.gif_label.setText("GIF Not Found")
            return

        if self.movie:
            self.movie.stop()

        self.movie = QMovie(gif_path)
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        self.movie.setScaledSize(self.gif_label.size())
        self.gif_label.setMovie(self.movie)
        self.movie.start()

    # ==================================================
    def start_workout(self):
        """Ask for camera permission before starting workout"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Camera Permission")
        dialog.setFixedSize(400, 180)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f4f6fb;
                border-radius: 12px;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #667eea;
                color: white;
                font-size: 13px;
                min-width: 90px;
                min-height: 32px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
            QPushButton:pressed {
                background-color: #5a67d8;
            }
        """)

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

        # ----- Button Actions -----
        def on_yes():
            dialog.accept()
            self.open_camera_screen()

        def on_no():
            dialog.reject()
            # Custom warning dialog
            msg = QMessageBox(self)
            msg.setWindowTitle("Permission Denied")
            msg.setText("Camera access denied. Cannot start workout.")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #f4f6fb;
                    font-family: Segoe UI;
                }
                QLabel {
                color: black;  /* <-- Set the text color to black */
                }
                QPushButton {
                    background-color: #667eea;
                    color: white;
                    border-radius: 6px;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #764ba2;
                }
            """)
            msg.exec()

        yes_btn.clicked.connect(on_yes)
        no_btn.clicked.connect(on_no)

        dialog.exec()

    # ==================================================
    def open_camera_screen(self):
        """Move to the next screen (camera workout)"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Camera Ready")
        msg.setText("Camera permission granted. Moving to workout screen.")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f4f6fb;
                font-family: Segoe UI;
            }
            QLabel {
                color: black;  /* <-- Set the text color to black */
            }
            QPushButton {
                background-color: #667eea;
                color: white;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
        """)
        msg.exec()
        
        main_win = self.window()
        if hasattr(main_win, "show_workout_session"):
            main_win.show_workout_session(self.current_workout_id)
            # TODO: Integrate actual camera screen here
        
        

    # ==========================================
    def go_back(self):
        if self.movie:
            self.movie.stop()

        main_win = self.window()
        if hasattr(main_win, "back_to_dashboard_from_demo"):
            main_win.back_to_dashboard_from_demo()
