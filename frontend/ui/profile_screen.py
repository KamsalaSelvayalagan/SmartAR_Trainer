"""
User Profile Screen with editable email
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QScrollArea,
    QLineEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from backend.models.data_manager import get_trainee, update_trainee


FONT_MAIN = "Segoe UI Variable"


class ProfileScreen(QWidget):
    backRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trainee_id = None
        self.profile = {}
        self.edit_mode = False
        self.init_ui()

    # ---------------- DATA ----------------
    def set_user(self, user_data):
        self.trainee_id = user_data.get("trainee_id")
        self.load_data()

    def load_data(self):
        if not self.trainee_id:
            return
        self.profile = get_trainee(self.trainee_id)
        if self.profile:
            self.refresh_display()

    # ---------------- UI ----------------
    def init_ui(self):
        # Improved background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1c1c2e, stop:1 #121221);
            }
        """)
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)

        # ---------- NAV BAR ----------
        nav = QFrame()
        nav.setFixedHeight(86)
        nav.setStyleSheet("""
            QFrame {
                background: rgba(28,28,46,0.95);
                border-bottom: 1px solid rgba(255,255,255,0.12);
            }
        """)
        nav_l = QHBoxLayout(nav)
        nav_l.setContentsMargins(50, 0, 50, 0)

        title = QLabel("SmartARTrainer")
        title.setFont(QFont(FONT_MAIN, 26, QFont.Weight.ExtraBold))
        title.setStyleSheet("color:#7c8cff;")
        nav_l.addWidget(title)
        nav_l.addStretch()

        def nav_btn(text, active=False):
            btn = QPushButton(text)
            btn.setFont(QFont(FONT_MAIN, 14, QFont.Weight.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {'rgba(102,126,234,0.9)' if active else 'transparent'};
                    color: white;
                    border-radius: 10px;
                    padding: 10px 22px;
                    border: {'none' if active else '1px solid rgba(255,255,255,0.35)'};
                }}
                QPushButton:hover {{
                    background: rgba(102,126,234,0.35);
                }}
            """)
            return btn

        dash_btn = nav_btn("Workout")
        dash_btn.clicked.connect(self.backRequested.emit)

        analytics_btn = nav_btn("Dashboard")
        analytics_btn.clicked.connect(self.on_analytics_clicked)

        profile_btn = nav_btn("Profile", True)

        nav_l.addWidget(analytics_btn)
        nav_l.addSpacing(12)
        nav_l.addWidget(dash_btn)
        nav_l.addSpacing(12)
        nav_l.addWidget(profile_btn)

        main.addWidget(nav)

        # ---------- CONTENT ----------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(60, 40, 60, 50)
        lay.setSpacing(40)

        # Header
        head = QHBoxLayout()
        h = QLabel("My Profile")
        h.setFont(QFont(FONT_MAIN, 38, QFont.Weight.Black))
        h.setStyleSheet("color:white;")
        head.addWidget(h)
        head.addStretch()

        self.edit_btn = QPushButton("Edit Profile")
        self.edit_btn.setFixedHeight(52)
        self.edit_btn.setFont(QFont(FONT_MAIN, 14, QFont.Weight.Bold))
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 26px;
                padding: 0 26px;
            }
        """)
        self.edit_btn.clicked.connect(self.toggle_edit)
        head.addWidget(self.edit_btn)

        lay.addLayout(head)

        grid = QGridLayout()
        grid.setSpacing(48)

        # ---------- LEFT CARD ----------
        left = QFrame()
        left.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 28px;
            }
        """)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(40, 44, 40, 44)
        ll.setSpacing(26)

        self.avatar = QLabel("A")
        self.avatar.setFixedSize(130,130)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setFont(QFont(FONT_MAIN, 52, QFont.Weight.Black))
        self.avatar.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #667eea, stop:1 #764ba2);
            color:white;
            border-radius:65px;
        """)
        ll.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Name
        self.name_label = QLabel("Loading...")
        self.name_label.setFont(QFont(FONT_MAIN, 34, QFont.Weight.Black))
        self.name_label.setStyleSheet("color:#e0e0ff;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setVisible(False)
        self.name_input.setFont(QFont(FONT_MAIN, 18, QFont.Weight.Bold))
        self.name_input.setStyleSheet("""
            background: rgba(255,255,255,0.14);
            color:white;
            border-radius:14px;
            padding:12px;
        """)

        # Email
        self.email_label = QLabel("")
        self.email_label.setFont(QFont(FONT_MAIN, 18, QFont.Weight.Bold))
        self.email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.email_label.setStyleSheet("color:#b6c0ff;")
        self.email_input = QLineEdit()
        self.email_input.setVisible(False)
        self.email_input.setFont(QFont(FONT_MAIN, 16, QFont.Weight.Bold))
        self.email_input.setStyleSheet("""
            background: rgba(255,255,255,0.14);
            color:white;
            border-radius:14px;
            padding:10px;
        """)

        ll.addWidget(self.name_label)
        ll.addWidget(self.name_input)
        ll.addWidget(self.email_label)
        ll.addWidget(self.email_input)

        # Info rows
        def info(title):
            r = QHBoxLayout()
            t = QLabel(title)
            t.setFont(QFont(FONT_MAIN, 16, QFont.Weight.Bold))
            t.setStyleSheet("color:#aab1ff;")
            v = QLabel("--")
            v.setFont(QFont(FONT_MAIN, 20, QFont.Weight.Black))
            v.setStyleSheet("color:white;")
            r.addWidget(t)
            r.addStretch()
            r.addWidget(v)
            ll.addLayout(r)
            return v

        self.dob_label = info("DATE OF BIRTH")
        self.gender_label = info("GENDER")

        grid.addWidget(left, 0, 0)

        # ---------- RIGHT CARD ----------
        right = QFrame()
        right.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 28px;
            }
        """)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(44, 44, 44, 44)
        rl.setSpacing(28)

        t = QLabel("Fitness Profile")
        t.setFont(QFont(FONT_MAIN, 26, QFont.Weight.Black))
        t.setStyleSheet("color:#8fa2ff;")
        rl.addWidget(t)

        def stat(title):
            r = QHBoxLayout()
            l = QLabel(title)
            l.setFont(QFont(FONT_MAIN, 16, QFont.Weight.Bold))
            l.setStyleSheet("color:#aab1ff;")
            v = QLabel("--")
            v.setFont(QFont(FONT_MAIN, 24, QFont.Weight.Black))
            v.setStyleSheet("color:white;")
            r.addWidget(l)
            r.addStretch()
            r.addWidget(v)
            rl.addLayout(r)
            return v

        self.height_val = stat("HEIGHT")
        self.weight_val = stat("WEIGHT")
        self.duration_val = stat("WORKOUT DURATION")
        self.freq_val = stat("WEEKLY FREQUENCY")

        self.plan_val = QLabel("--")
        self.plan_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plan_val.setFont(QFont(FONT_MAIN, 30, QFont.Weight.Black))
        self.plan_val.setStyleSheet("color:white; margin-top:26px;")
        rl.addWidget(self.plan_val)

        grid.addWidget(right, 0, 1)
        lay.addLayout(grid)

        scroll.setWidget(wrap)
        main.addWidget(scroll)

    # ---------------- LOGIC ----------------
    def refresh_display(self):
        self.name_label.setText(self.profile.get("name", "User"))
        self.avatar.setText(self.profile.get("name", "U")[0].upper())
        self.email_label.setText(self.profile.get("email", "--"))

        self.dob_label.setText(self.profile.get("dob", "--"))
        self.gender_label.setText(self.profile.get("gender", "--"))

        self.height_val.setText(f"{self.profile.get('height', '--')} cm")
        self.weight_val.setText(f"{self.profile.get('weight', '--')} kg")
        self.duration_val.setText(f"{self.profile.get('workout_duration', '--')} min")
        self.freq_val.setText(f"{self.profile.get('weekly_frequency', '--')} days")

        self.plan_val.setText(self.profile.get("fitness_level") or "STANDARD PLAN")

        self.name_label.setVisible(True)
        self.name_input.setVisible(False)
        self.email_label.setVisible(True)
        self.email_input.setVisible(False)

    def toggle_edit(self):
        self.edit_mode = not self.edit_mode
        self.name_label.setVisible(not self.edit_mode)
        self.name_input.setVisible(self.edit_mode)
        self.email_label.setVisible(not self.edit_mode)
        self.email_input.setVisible(self.edit_mode)

        if self.edit_mode:
            self.name_input.setText(self.profile.get("name", ""))
            self.email_input.setText(self.profile.get("email", ""))
            self.edit_btn.setText("Save Changes")
        else:
            self.save_data()

    def save_data(self):
        success, msg = update_trainee(
            self.trainee_id,
            name=self.name_input.text().strip(),
            email=self.email_input.text().strip()
        )
        if success:
            QMessageBox.information(self, "Success", "Profile updated")
            self.edit_btn.setText("Edit Profile")
            self.load_data()
        else:
            QMessageBox.warning(self, "Error", msg)

    def on_analytics_clicked(self):
        main = self.window()
        if hasattr(main, "show_analytics"):
            main.show_analytics()
