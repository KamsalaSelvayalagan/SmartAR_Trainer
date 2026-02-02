"""
Workout Dashboard displaying workout plan
Connected to SQLite database using workout_session for unlocks
Professional UI with glassmorphism effects and high-quality layout
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap, QMovie

from backend.models.data_manager import (
    get_trainee_info,
    get_workout_plan,
    save_workout_session,
    WORKOUT_COLUMNS
)


class WorkoutCard(QFrame):
    """Premium individual workout card with video/image preview and progression state"""

    def __init__(self, workout, index, trainee_id, is_locked, parent=None):
        super().__init__(parent)
        self.workout = workout
        self.index = index
        self.trainee_id = trainee_id
        self.is_locked = is_locked
        self.init_ui()

    def init_ui(self):
        self.setObjectName("workoutCard")
        self.setProperty("unlocked", "true" if not self.is_locked else "false")

        self.setStyleSheet("""
            QFrame#workoutCard {
                background: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 24px;
            }
            QFrame#workoutCard[unlocked="true"]:hover {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(102, 126, 234, 0.6);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header: Workout Name
        title = QLabel(self.workout["name"])
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Video/Image Container
        video_container = QFrame()
        video_container.setMinimumSize(280, 160)
        video_container.setMaximumHeight(200)
        video_container.setStyleSheet("""
            QFrame {
                background: #000000;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)

        # --- Load Asset Image/GIF ---
        asset_map = {
            "Jumping Jacks": "Jumping jacks.gif",
            "Push Ups": "Push ups.gif",
            "Plank": "Plank.png",
            "Crunches": "Crunches.gif",
            "Squats": "Squats.gif",
            "Cobra Stretch": "Cobra Stretch.png"
        }

        asset_filename = asset_map.get(self.workout["name"], None)

        if asset_filename:
            # Correct absolute path
            abs_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "assets", asset_filename)
            )
            print("Loading asset from:", abs_path)  # DEBUG: should match your actual path

            if os.path.exists(abs_path):
                if abs_path.lower().endswith(".gif"):
                    movie = QMovie(abs_path)
                    movie.setScaledSize(QSize(280, 160))
                    gif_label = QLabel()
                    gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    gif_label.setMovie(movie)
                    movie.start()
                    video_layout.addWidget(gif_label)
                else:
                    pixmap = QPixmap(abs_path)
                    pixmap = pixmap.scaled(
                        280, 160,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    img_label = QLabel()
                    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    img_label.setPixmap(pixmap)
                    video_layout.addWidget(img_label)
            else:
                fallback = QLabel(f"File not found:\n{abs_path}")
                fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
                video_layout.addWidget(fallback)
        else:
            fallback = QLabel("No Preview Available")
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            video_layout.addWidget(fallback)
        layout.addWidget(video_container)

        # Reps/Time
        unit = "seconds" if self.workout["name"] in ["Plank", "Cobra Stretch"] else "reps"
        target_val = self.workout.get("target", 0)
        target = QLabel(f"{target_val} {unit}")
        target.setFont(QFont("Segoe UI", 15, QFont.Weight.DemiBold))
        target.setStyleSheet("color: #667eea; background: transparent;")
        target.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(target)

        # Start Button
        self.start_btn = QPushButton("Start Workout" if not self.is_locked else " 🔒 Locked")
        self.start_btn.setMinimumHeight(48)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor if not self.is_locked else Qt.CursorShape.ForbiddenCursor)
        self.start_btn.clicked.connect(self.on_start_clicked)

        if self.is_locked:
            self.start_btn.setEnabled(False)
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.1);
                    color: rgba(255, 255, 255, 0.3);
                    border-radius: 12px;
                    font-weight: bold;
                    border: none;
                }
            """)
        else:
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

        layout.addWidget(self.start_btn)

    def on_start_clicked(self):
        if self.is_locked:
            return
        main_win = self.window()
        if hasattr(main_win, "show_workout_demo"):
            main_win.show_workout_demo(self.workout["workout_id"])


class Dashboard(QWidget):
    """Main professional dashboard component"""

    logoutSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trainee_id = None
        self.trainee = None
        self.workouts = []
        self.completed_indices = set()  # Track completion in current session
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Top Navigation Bar ---
        nav_bar = QFrame()
        nav_bar.setFixedHeight(80)
        nav_bar.setStyleSheet("""
            QFrame {
                background: rgba(15, 12, 41, 0.4);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(50, 0, 50, 0)

        app_title = QLabel("SmartARTrainer")
        app_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        app_title.setStyleSheet("color: #667eea; background: transparent;")
        nav_layout.addWidget(app_title)
        nav_layout.addStretch()

        btn_style_template = """
            QPushButton {
                background: %s;
                color: white;
                border: %s;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(102, 126, 234, 0.3);
            }
        """
        self.dash_btn = QPushButton("Dashboard")
        self.dash_btn.setStyleSheet(btn_style_template % ("rgba(102, 126, 234, 0.8)", "none"))

        self.analytics_btn = QPushButton("Analytics")
        self.analytics_btn.setStyleSheet(btn_style_template % ("transparent", "1px solid rgba(255, 255, 255, 0.4)"))
        self.analytics_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analytics_btn.clicked.connect(self.on_analytics_clicked)

        self.profile_btn = QPushButton("Profile")
        self.profile_btn.setStyleSheet(btn_style_template % ("transparent", "1px solid rgba(255, 255, 255, 0.4)"))
        self.profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.profile_btn.clicked.connect(self.on_profile_clicked)

        nav_layout.addWidget(self.dash_btn)
        nav_layout.addSpacing(10)
        nav_layout.addWidget(self.analytics_btn)
        nav_layout.addSpacing(10)
        nav_layout.addWidget(self.profile_btn)

        main_layout.addWidget(nav_bar)

        # --- Content Area ---
        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(50, 30, 50, 40)
        content_layout.setSpacing(25)

        # Header: User Info & Logout
        header_layout = QHBoxLayout()
        titles_layout = QVBoxLayout()

        self.welcome_label = QLabel("Trainee: Loading...")
        self.welcome_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.welcome_label.setStyleSheet("color: white; background: transparent;")
        titles_layout.addWidget(self.welcome_label)

        self.plan_label = QLabel("Plan: Personalized")
        self.plan_label.setFont(QFont("Segoe UI", 16))
        self.plan_label.setStyleSheet("color: #667eea; background: transparent; font-weight: 500;")
        titles_layout.addWidget(self.plan_label)

        self.subtitle_label = QLabel("Personalized Workout Schedule")
        self.subtitle_label.setFont(QFont("Segoe UI", 12))
        self.subtitle_label.setStyleSheet("color: #718096; background: transparent;")
        titles_layout.addWidget(self.subtitle_label)

        header_layout.addLayout(titles_layout)
        header_layout.addStretch()

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setFixedSize(120, 45)
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                color: white;
                border-radius: 10px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QPushButton:hover {
                background: rgba(255, 107, 107, 0.15);
                border-color: #ff6b6b;
                color: #ff6b6b;
            }
        """)
        self.logout_btn.clicked.connect(self.logoutSignal.emit)
        header_layout.addWidget(self.logout_btn, alignment=Qt.AlignmentFlag.AlignTop)

        content_layout.addLayout(header_layout)

        # --- Scrollable Workout Grid ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        scroll.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(102, 126, 234, 0.5);
                border-radius: 5px;
            }
        """)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(30)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.grid_container)

        content_layout.addWidget(scroll)
        main_layout.addWidget(content_wrapper)

    def set_user(self, user_data):
        self.trainee_id = user_data.get("trainee_id")
        self.load_dashboard_data()

    def load_dashboard_data(self):
        if not self.trainee_id:
            return

        self.trainee = get_trainee_info(self.trainee_id)
        if self.trainee:
            self.welcome_label.setText(f"Trainee: {self.trainee['name']}")
            level = self.trainee.get('fitness_level', 'Custom')
            self.plan_label.setText(f"Plan: {level}")

            self.workouts = get_workout_plan(self.trainee['plan_id'])
            self.refresh_cards()

    def mark_exercise_completed(self, index):
        self.completed_indices.add(index)
        if len(self.completed_indices) == len(self.workouts):
            self.finalize_session()
        else:
            self.refresh_cards()

    def finalize_session(self):
        session_data = {col: 1 for col in WORKOUT_COLUMNS}
        success, msg = save_workout_session(self.trainee_id, session_data)
        if success:
            QMessageBox.information(self, "Session Complete",
                                    "Congratulations! You've completed your full workout session. Data has been saved.")
            self.completed_indices.clear()
            self.refresh_cards()
        else:
            QMessageBox.critical(self, "Error", f"Failed to save session: {msg}")

    def refresh_cards(self):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        for i, workout in enumerate(self.workouts):
            is_locked = True
            if i == 0 or (i - 1) in self.completed_indices:
                is_locked = False
            card = WorkoutCard(workout, i, self.trainee_id, is_locked)
            row = i // 3
            col = i % 3
            self.grid_layout.addWidget(card, row, col)

    def refresh(self):
        self.load_dashboard_data()

    def on_profile_clicked(self):
        main_win = self.window()
        if hasattr(main_win, "show_profile"):
            main_win.show_profile()

    def on_analytics_clicked(self):
        main_win = self.window()
        if hasattr(main_win, "show_analytics"):
            main_win.show_analytics()
