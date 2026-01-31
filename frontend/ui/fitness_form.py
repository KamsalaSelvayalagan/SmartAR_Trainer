"""
Fitness Details Form for user onboarding
Integrated with SQLite database
LIGHT MODE VERSION
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame,
    QRadioButton, QButtonGroup,
    QDoubleSpinBox, QMessageBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class FitnessForm(QWidget):
    """Comprehensive fitness details form"""

    formCompleted = pyqtSignal(dict) # Emits all fitness data
    backRequested = pyqtSignal()   # Emits when back button clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # ================= Scroll Area =================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                   stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #667eea;
                border-radius: 5px;
            }
        """)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 80, 0, 40)

        # ================= Card =================
        card = QWidget()
        card.setFixedWidth(650)
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 25px;
                border: 1px solid #e2e8f0;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(25)
        card_layout.setContentsMargins(50, 50, 50, 50)

        # ================= Title =================
        title = QLabel("Complete Your Fitness Profile")
        title.setFont(QFont("Segoe UI", 36, QFont.Weight.ExtraBold))
        # Professional vibrant gradient-like color
        title.setStyleSheet("""
            QLabel {
                color: #667eea;
                background: transparent;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Elevate your lifestyle with personalized AI coaching")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: #718096; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)

        # ================= Styles =================
        label_style = "color:#2d3748; font-size:15px; font-weight:800; background:transparent;"

        radio_style = """
            QRadioButton {
                color:#333333;
                font-size:14px;
            }
            QRadioButton::indicator {
                width:18px;
                height:18px;
                border-radius:9px;
                border:2px solid #555;
            }
            QRadioButton::indicator:checked {
                background:#667eea;
                border:2px solid #667eea;
            }
        """

        input_style = """
            QComboBox, QDoubleSpinBox, QSpinBox {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                color: #2d3748;
                padding: 6px 12px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4a5568;
                width: 0;
                height: 0;
                margin-right: 10px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border-left: 1px solid #e2e8f0;
                background: transparent;
            }
            QDoubleSpinBox::up-arrow, QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #4a5568;
                width: 0;
                height: 0;
            }
            QDoubleSpinBox::down-arrow, QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #4a5568;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2d3748;
                selection-background-color: #667eea;
                selection-color: white;
                border-radius: 8px;
                outline: 0;
            }
        """

        # ================= Helper =================
        def create_row(text, widget):
            container = QWidget()
            container.setFixedWidth(500)
            container.setStyleSheet("""
                background:#ffffff;
                border: 1px solid #edf2f7;
                border-radius:12px;
            """)
            row = QHBoxLayout(container)
            row.setContentsMargins(16, 12, 16, 12)

            lbl = QLabel(text)
            lbl.setStyleSheet(label_style)

            widget.setFixedHeight(40)
            widget.setStyleSheet(input_style)

            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(widget)
            return container

        # ================= DOB =================
        self.day_input = QComboBox()
        self.month_input = QComboBox()
        self.year_input = QComboBox()

        for d in range(1, 32):
            self.day_input.addItem(f"{d:02d}")

        self.month_input.addItems([
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ])

        for y in range(1976, 2026):
            self.year_input.addItem(str(y))

        for cb in (self.day_input, self.month_input, self.year_input):
            cb.setFixedHeight(40)
            cb.setStyleSheet(input_style)

        dob_container = QWidget()
        dob_container.setFixedWidth(500)
        dob_container.setStyleSheet("background:#ffffff; border: 1px solid #edf2f7; border-radius:12px;")
        dob_layout = QHBoxLayout(dob_container)
        dob_layout.setContentsMargins(12, 6, 12, 6)

        dob_label = QLabel("Date of Birth")
        dob_label.setStyleSheet(label_style)
        dob_label.setMinimumWidth(200)

        dob_layout.addWidget(dob_label)
        dob_layout.addWidget(self.day_input)
        dob_layout.addWidget(self.month_input)
        dob_layout.addWidget(self.year_input)

        card_layout.addWidget(dob_container)

        # ================= Gender =================
        gender_label = QLabel("Gender")
        gender_label.setStyleSheet(label_style)
        gender_label.setMinimumWidth(200)

        self.gender_group = QButtonGroup()
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        self.other_radio = QRadioButton("Other")

        for rb in (self.male_radio, self.female_radio, self.other_radio):
            rb.setStyleSheet(radio_style)
            self.gender_group.addButton(rb)

        self.male_radio.setChecked(True)

        gender_box = QWidget()
        gender_box.setFixedWidth(500)
        gender_box.setStyleSheet("background:#ffffff; border: 1px solid #edf2f7; border-radius:12px;")
        gender_layout = QHBoxLayout(gender_box)
        gender_layout.addWidget(gender_label)
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        gender_layout.addWidget(self.other_radio)

        card_layout.addWidget(gender_box)

        # ================= Height & Weight =================
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(100, 250)
        self.height_input.setSuffix(" cm")
        self.height_input.setValue(170)
        card_layout.addWidget(create_row("Height", self.height_input))

        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(30, 200)
        self.weight_input.setSuffix(" kg")
        self.weight_input.setValue(70)
        card_layout.addWidget(create_row("Weight", self.weight_input))

        # ================= Workout Experience =================
        exp_label = QLabel("Workout Experience?")
        exp_label.setStyleSheet(label_style)
        exp_label.setMinimumWidth(200)

        self.workout_yes_radio = QRadioButton("Yes")
        self.workout_no_radio = QRadioButton("No")
        self.workout_no_radio.setChecked(True)

        for rb in (self.workout_yes_radio, self.workout_no_radio):
            rb.setStyleSheet(radio_style)

        exp_box = QWidget()
        exp_box.setFixedWidth(500)
        exp_box.setStyleSheet("background:#ffffff; border: 1px solid #edf2f7; border-radius:12px;")
        exp_layout = QHBoxLayout(exp_box)
        exp_layout.addWidget(exp_label)
        exp_layout.addWidget(self.workout_yes_radio)
        exp_layout.addWidget(self.workout_no_radio)

        card_layout.addWidget(exp_box)

        # ================= Experience Details =================
        self.exp_details_widget = QWidget()
        exp_details_layout = QVBoxLayout(self.exp_details_widget)

        self.duration_input = QDoubleSpinBox()
        self.duration_input.setSuffix(" mins")

        self.freq_input = QSpinBox()
        self.freq_input.setRange(1, 7)
        self.freq_input.setSuffix(" days")

        exp_details_layout.addWidget(create_row("Workout duration", self.duration_input))
        exp_details_layout.addWidget(create_row("Workout frequency", self.freq_input))

        self.exp_details_widget.setVisible(False)
        self.workout_yes_radio.toggled.connect(
            lambda checked: self.exp_details_widget.setVisible(checked)
        )

        card_layout.addWidget(self.exp_details_widget)

        # ================= Actions =================
        actions_layout = QHBoxLayout()
        
        back_btn = QPushButton("Back")
        back_btn.setMinimumHeight(55)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #f7fafc;
                color: #4a5568;
                border: 2px solid #e2e8f0;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #edf2f7;
                border-color: #cbd5e0;
            }
        """)
        back_btn.clicked.connect(self.backRequested.emit)
        
        submit_btn = QPushButton("Sign Up")
        submit_btn.setMinimumHeight(55)
        submit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #764ba2, stop:1 #667eea);
            }
        """)
        submit_btn.clicked.connect(self.handle_submit)
        
        actions_layout.addWidget(back_btn, 1)
        actions_layout.addWidget(submit_btn, 2)
        card_layout.addLayout(actions_layout)

        # ================= Final Layout =================
        center = QHBoxLayout()
        center.addStretch()
        center.addWidget(card)
        center.addStretch()

        layout.addLayout(center)
        scroll.setWidget(content)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(scroll)

    # ======================================================
    def handle_submit(self):
        day = self.day_input.currentText()
        month = self.month_input.currentText()
        year = self.year_input.currentText()

        month_map = {
            "Jan":"01","Feb":"02","Mar":"03","Apr":"04",
            "May":"05","Jun":"06","Jul":"07","Aug":"08",
            "Sep":"09","Oct":"10","Nov":"11","Dec":"12"
        }

        dob = f"{year}-{month_map[month]}-{day}"

        gender = (
            "Male" if self.male_radio.isChecked()
            else "Female" if self.female_radio.isChecked()
            else "Other"
        )

        height = self.height_input.value()
        weight = self.weight_input.value()

        has_exp = self.workout_yes_radio.isChecked()
        duration = self.duration_input.value() if has_exp else 0
        frequency = int(self.freq_input.value()) if has_exp else 0

        fitness_data = {
            "dob": dob,
            "gender": gender,
            "height": height,
            "weight": weight,
            "workout_experience": "Yes" if has_exp else "No",
            "workout_duration": duration,
            "weekly_frequency": frequency
        }

        self.formCompleted.emit(fitness_data)

    def get_data(self):
        """Helper to get current state for data preservation"""
        # This is a bit simplified, but emits the same dict structure
        has_exp = self.workout_yes_radio.isChecked()
        return {
            "dob_day": self.day_input.currentIndex(),
            "dob_month": self.month_input.currentIndex(),
            "dob_year": self.year_input.currentIndex(),
            "gender_male": self.male_radio.isChecked(),
            "gender_female": self.female_radio.isChecked(),
            "gender_other": self.other_radio.isChecked(),
            "height": self.height_input.value(),
            "weight": self.weight_input.value(),
            "workout_exp": has_exp,
            "duration": self.duration_input.value(),
            "frequency": self.freq_input.value()
        }

    def set_data(self, data):
        """Restore state for data preservation"""
        if not data: return
        self.day_input.setCurrentIndex(data.get("dob_day", 0))
        self.month_input.setCurrentIndex(data.get("dob_month", 0))
        self.year_input.setCurrentIndex(data.get("dob_year", 0))
        
        if data.get("gender_male"): self.male_radio.setChecked(True)
        elif data.get("gender_female"): self.female_radio.setChecked(True)
        elif data.get("gender_other"): self.other_radio.setChecked(True)
        
        self.height_input.setValue(data.get("height", 170))
        self.weight_input.setValue(data.get("weight", 70))
        
        if data.get("workout_exp"): 
            self.workout_yes_radio.setChecked(True)
        else:
            self.workout_no_radio.setChecked(True)
            
        self.duration_input.setValue(data.get("duration", 0))
        self.freq_input.setValue(data.get("frequency", 0))
